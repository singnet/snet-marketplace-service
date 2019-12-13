from datetime import datetime as dt

from common.logger import get_logger

logger = get_logger(__name__)


class TruliooTransactionHistoryDAO:
    def __init__(self, repo):
        self.__repo = repo

    def insert_trulioo_transaction_data(self, transaction_id, transaction_record_id, country_code, product_name,
                                        uploaded_date, record_status):
        query_response = self.__repo.execute(
            "INSERT INTO trulioo_transaction_history (transaction_id, transaction_record_id, country_code, product_name,"
            " uploaded_date, record_status, row_created, row_updated) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
            [transaction_id, transaction_record_id, country_code, product_name, uploaded_date, record_status,
             dt.utcnow(), dt.utcnow()])
        return query_response
