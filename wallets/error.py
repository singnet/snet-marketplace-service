class Error:
    @staticmethod
    def undefined_error(error_message):
        return {
            "code": 0, "message": str(error_message)
        }
