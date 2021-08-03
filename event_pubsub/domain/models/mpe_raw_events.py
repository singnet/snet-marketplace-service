class MpeEventsRaw:
    def __init__(self, block_no, event, json_str, processed, transactionHash, logIndex, error_code, error_msg):
        self._block_no = block_no
        self._event = event
        self._json_str = json_str
        self._processed = processed
        self._transactionHash = transactionHash
        self._logIndex = logIndex
        self._error_code = error_code
        self._error_msg = error_msg

    @property
    def block_no(self):
        return self._block_no

    @property
    def event(self):
        return self._event

    @property
    def json_str(self):
        return self._json_str

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
