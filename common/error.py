from common.constant import ERROR_MSG


class ErrorHandler:
    def __init__(self):
        pass

    def log_err_msg(self, err, fn_nme='', err_cd=None):
        try:
            if err_cd == None:
                err_msg = 'Error in {}::error: {}'.format(fn_nme, repr(err))
            else:
                err_msg = ERROR_MSG[err_cd].format(err_cd)
            print(repr(err_msg))
            return err_msg
        except KeyError as e:
            return ERROR_MSG[err_cd].format(err_cd=9001)
        except Exception as e:
            return ERROR_MSG['default']

    def get_err_msg(self, err_cd):
        try:
            return ERROR_MSG[err_cd].format(err_cd)
        except Exception as e:
            return ERROR_MSG[err_cd].format(err_cd=9001)
