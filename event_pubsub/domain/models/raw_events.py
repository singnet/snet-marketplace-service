class RawEvents:
    def __init__(self, block_no, uncle_block_no, event, event_data, processed, transactionHash, logIndex, error_code,
                 error_msg):
        self._block_no = block_no
        self._uncle_block_no = uncle_block_no
        self._event = event
        self._event_data = event_data
        self._processed = processed
        self._transactionHash = transactionHash
        self._logIndex = logIndex
        self._error_code = error_code
        self._error_msg = error_msg

    def to_dict(self):
        return {
            "block_no": self._block_no,
            "uncle_block_no": self._uncle_block_no,
            "event": self._event,
            "event_data": self._event_data,
            "processed": self._processed,
            "transactionHash": self._transactionHash,
            "logIndex": self._logIndex,
            "error_code": self._error_code,
            "error_msg": self._error_msg
        }

    @property
    def block_no(self):
        return self._block_no

    @property
    def uncle_block_no(self):
        return self._uncle_block_no

    @property
    def event(self):
        return self._event

    @property
    def event_data(self):
        return self._event_data

    @property
    def processed(self):
        return self._processed

    @property
    def transactionHash(self):
        return self._transactionHash

    @property
    def logIndex(self):
        return self._logIndex

    @property
    def error_code(self):
        return self._error_code

    @property
    def error_msg(self):
        return self._error_msg
