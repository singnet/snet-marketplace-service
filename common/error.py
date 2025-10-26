

class ErrorHandler:
    def __init__(self, ERROR_MSG):
        self.error_msg = ERROR_MSG

    def log_err_msg(self, err, fn_nme='', err_cd=None):
        try:
            if err_cd == None:
                err_msg = 'Error in {}::error: {}'.format(fn_nme, repr(err))
            else:
                err_msg = self.error_msg[err_cd].format(err_cd)
            print(repr(err_msg))
            return err_msg
        except KeyError:
            return self.error_msg[err_cd].format(err_cd=9001)
        except Exception:
            return self.error_msg['default']

    def get_err_msg(self, err_cd):
        try:
            return self.error_msg[err_cd].format(err_cd)
        except Exception:
            return self.error_msg[err_cd].format(err_cd=9001)
