from typing import Dict, List, Any, Tuple

from pandas import DataFrame, date_range

from deployer.application.schemas.billing_schemas import GetMetricsRequest
from deployer.config import REQUEST_MAX_LIMIT
from deployer.constant import OrderType, PeriodType, FREQUENCY_BY_PERIOD
from deployer.domain.schemas.haas_responses import CallEventResponse
from deployer.exceptions import HostedServiceNotFoundException
from deployer.infrastructure.clients.haas_client import HaaSClient
from deployer.infrastructure.db import DefaultSessionFactory, session_scope
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository


class MetricsService:
    def __init__(self, session_factory=None, haas_client=None):
        self.session_factory = DefaultSessionFactory if session_factory is None else session_factory
        self._haas_client = HaaSClient() if haas_client is None else haas_client
        self.datetime_format = "%Y-%m-%dT%H:%M:%S"

    def get_metrics(self, request: GetMetricsRequest) -> dict:
        events = self._get_all_events(request)

        if not events:
            return self._get_empty_metrics_response()

        df = self._create_events_dataframe(events)
        grouped_data = self._group_events_by_timeframe(df, request.period)

        metrics = self._prepare_aggregated_metrics(grouped_data)
        metrics["summary"] = self._prepare_metrics_summary(df)

        return metrics

    def download_metrics(self, request: GetMetricsRequest) -> Tuple[str, str]:
        file_content = "orgId,serviceId,duration,amount,timestamp"
        filename = f"hosted_service_{request.hosted_service_id}_metrics.csv"

        events = self._get_all_events(request)

        for event in events:
            file_content += f"\n{event.org_id},{event.service_id},{event.duration},{event.amount},{event.timestamp}"

        return file_content, filename

    def _get_all_events(self, request: GetMetricsRequest) -> List[CallEventResponse]:
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

        return events

    def _prepare_aggregated_metrics(self, grouped_data: dict):
        df = grouped_data["grouped_df"]
        time_groups = grouped_data["time_groups"]

        aggregated_metrics = {
            "requests_count": df.groupby("time_group").size(),
            "costs_sum": df.groupby("time_group")["amount"].sum(),
            "costs_avg": df.groupby("time_group")["amount"].mean(),
            "durations_sum": df.groupby("time_group")["duration"].sum(),
            "durations_avg": df.groupby("time_group")["duration"].mean(),
        }

        full_series = aggregated_metrics["requests_count"].reindex(time_groups, fill_value=0)
        labels = full_series.index.strftime(self.datetime_format)

        for name, data in aggregated_metrics.items():
            full_series = data.reindex(time_groups, fill_value=0)
            aggregated_metrics[name] = full_series.values.tolist()

        return {"labels": labels.tolist(), "values": aggregated_metrics}

    def _get_empty_metrics_response(self) -> dict:
        return {
            "labels": [],
            "values": {
                "requestsCount": [],
                "costsSum": [],
                "costsAvg": [],
                "durationsSum": [],
                "durationsAvg": [],
            },
            "summary": {
                "requests": {"total": 0},
                "costs": {"total": 0, "avg": 0, "max": 0, "min": 0},
                "durations": {"total": 0, "avg": 0, "max": 0, "min": 0},
            },
        }

    def _create_events_dataframe(self, events: List[CallEventResponse]) -> DataFrame:
        events_data = []
        for event in events:
            events_data.append(
                {
                    "timestamp": event.timestamp,
                    "duration": event.duration,
                    "amount": event.amount,
                }
            )

        return DataFrame(events_data)

    def _group_events_by_timeframe(self, df: DataFrame, period: PeriodType) -> Dict[str, Any]:
        df = df.sort_values("timestamp")
        df = df.copy()
        df["time_group"] = df["timestamp"].dt.floor(FREQUENCY_BY_PERIOD[period])

        time_groups = date_range(
            start=df["time_group"].min(),
            end=df["time_group"].max(),
            freq=FREQUENCY_BY_PERIOD[period],
        )

        return {"grouped_df": df, "time_groups": time_groups, "period": period}

    def _prepare_metrics_summary(self, df: DataFrame) -> Dict:
        cost_stats = df["amount"].describe()
        duration_stats = df["duration"].describe()

        return {
            "requests": {"total": len(df)},
            "costs": {
                "total": int(df["amount"].sum()),
                "avg": round(float(cost_stats["mean"]), 2),
                "max": round(float(cost_stats["max"]), 2),
                "min": round(float(cost_stats["min"]), 2),
            },
            "durations": {
                "total": int(df["duration"].sum()),
                "avg": round(float(duration_stats["mean"]), 2),
                "max": round(float(duration_stats["max"]), 2),
                "min": round(float(duration_stats["min"]), 2),
            },
        }
