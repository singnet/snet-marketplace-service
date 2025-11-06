from typing import Dict, List, Any

from pandas import DataFrame, date_range, DatetimeIndex, Series

from deployer.application.schemas.billing_schemas import GetMetricsRequest
from deployer.config import REQUEST_MAX_LIMIT
from deployer.constant import OrderType, PeriodType
from deployer.domain.schemas.haas_responses import CallEventResponse
from deployer.exceptions import HostedServiceNotFoundException
from deployer.infrastructure.clients.haas_client import HaaSClient
from deployer.infrastructure.db import DefaultSessionFactory, session_scope
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository


class MetricsService:
    def __init__(self, session_factory=None):
        self.session_factory = session_factory if session_factory else DefaultSessionFactory
        self._haas_client = HaaSClient()

    def get_metrics(self, request: GetMetricsRequest) -> dict:
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon_by_hosted_service(
                session, request.hosted_service_id
            )
        if daemon is None or daemon.hosted_service is None:
            raise HostedServiceNotFoundException(hosted_service_id=request.hosted_service_id)

        events = []
        page = 1
        response = self._haas_client.get_call_events(
            services=(daemon.org_id, daemon.service_id),
            limit=REQUEST_MAX_LIMIT,
            page=page,
            order=OrderType.ASC,
            period=request.period,
        )
        events.extend(response.events)

        while response.total_count > len(events):
            page += 1
            response = self._haas_client.get_call_events(
                services=(daemon.org_id, daemon.service_id),
                limit=REQUEST_MAX_LIMIT,
                page=page,
                order=OrderType.ASC,
                period=request.period,
            )
            events.extend(response.events)

        if not events:
            return self._get_empty_metrics_response()

        df = self._create_events_dataframe(events)
        grouped_data = self._group_events_by_timeframe(df, request.period)

        metrics = {
            "requests": self._prepare_requests_metrics(grouped_data),
            "costs": self._prepare_costs_metrics(grouped_data),
            "durations": self._prepare_durations_metrics(grouped_data),
            "summary": self._prepare_summary_metrics(df)
        }

        return metrics

    def _get_empty_metrics_response(self) -> dict:
        return {
            "requests": {"labels": [], "data": []},
            "costs": {"labels": [], "data": []},
            "durations": {"labels": [], "data": []},
            "summary": {
                "total_requests": 0,
                "total_cost": 0,
                "avg_duration": 0,
                "success_rate": 100
            }
        }

    def _create_events_dataframe(self, events: List[CallEventResponse]) -> DataFrame:
        events_data = []
        for event in events:
            events_data.append({
                'timestamp': event.timestamp,
                'duration': event.duration,
                'amount': event.amount,
            })

        return DataFrame(events_data)

    def _group_events_by_timeframe(self, df: DataFrame, period: PeriodType) -> Dict[str, Any]:
        df = df.sort_values('timestamp')
        df = df.copy()

        if period == PeriodType.HOUR:
            df['time_group'] = df['timestamp'].dt.floor('min')
        elif period == PeriodType.DAY:
            df['time_group'] = df['timestamp'].dt.floor('h')
        elif period == PeriodType.WEEK:
            df['time_group'] = df['timestamp'].dt.floor('4h')
        elif period == PeriodType.MONTH:
            df['time_group'] = df['timestamp'].dt.floor('D')
        elif period == PeriodType.YEAR:
            df['time_group'] = df['timestamp'].dt.to_period('W').dt.to_timestamp()
        else:
            df['time_group'] = df['timestamp'].dt.to_period('W').dt.to_timestamp()

        if not df.empty:
            time_groups = date_range(
                start = df['time_group'].min(),
                end = df['time_group'].max(),
                freq = self._get_frequency_for_period(period)
            )
        else:
            time_groups = DatetimeIndex([])

        return {
            'grouped_df': df,
            'time_groups': time_groups,
            'period': period
        }

    def _get_frequency_for_period(self, period: PeriodType) -> str:
        frequency_map = {
            PeriodType.HOUR: 'min',
            PeriodType.DAY: 'h',
            PeriodType.WEEK: '4h',
            PeriodType.MONTH: 'D',
            PeriodType.YEAR: 'W',
            PeriodType.ALL: 'W'
        }
        return frequency_map[period]

    def _prepare_requests_metrics(self, grouped_data: Dict) -> Dict:
        df = grouped_data['grouped_df']
        time_groups = grouped_data['time_groups']

        if df.empty:
            return {"labels": [], "data": []}

        requests_count = df.groupby('time_group').size()
        full_series = requests_count.reindex(time_groups, fill_value = 0)
        labels = self._format_time_labels(full_series.index, grouped_data['period'])

        return {
            "labels": labels.tolist(),
            "data": full_series.values.tolist()
        }

    def _prepare_costs_metrics(self, grouped_data: Dict) -> Dict:
        df = grouped_data['grouped_df']
        time_groups = grouped_data['time_groups']

        if df.empty:
            return {"labels": [], "data": []}

        costs_sum = df.groupby('time_group')['amount'].sum()
        full_series = costs_sum.reindex(time_groups, fill_value = 0)
        labels = self._format_time_labels(full_series.index, grouped_data['period'])

        return {
            "labels": labels.tolist(),
            "data": full_series.values.tolist()
        }

    def _prepare_durations_metrics(self, grouped_data: Dict) -> Dict:
        df = grouped_data['grouped_df']
        time_groups = grouped_data['time_groups']

        if df.empty:
            return {"labels": [], "data": []}

        avg_durations = df.groupby('time_group')['duration'].mean()
        full_series = avg_durations.reindex(time_groups, fill_value = 0)
        labels = self._format_time_labels(full_series.index, grouped_data['period'])

        return {
            "labels": labels.tolist(),
            "data": full_series.values.tolist()
        }

    def _format_time_labels(self, timestamps: DatetimeIndex, period: PeriodType) -> Series:
        if period == PeriodType.HOUR:
            return timestamps.strftime('%H:%M')
        elif period == PeriodType.DAY:
            return timestamps.strftime('%H:%M')
        elif period in [PeriodType.WEEK, PeriodType.MONTH]:
            return timestamps.strftime('%d.%m')
        elif period == PeriodType.YEAR:
            return timestamps.strftime('%b %Y')
        else:
            return timestamps.strftime('%d.%m.%Y')

    def _prepare_summary_metrics(self, df: DataFrame) -> Dict:
        if df.empty:
            return {
                "total_requests": 0,
                "total_cost": 0,
                "avg_duration": 0,
                "success_rate": 100
            }

        total_requests = len(df)
        total_cost = df['amount'].sum()
        avg_duration = df['duration'].mean()

        return {
            "total_requests": int(total_requests),
            "total_cost": float(total_cost),
            "avg_duration": float(avg_duration)
    }