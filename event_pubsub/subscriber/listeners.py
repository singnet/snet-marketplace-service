import requests
class ListenersHandlers(object):

    def push_event(self):
        pass


class WebHookHandler(ListenersHandlers):

    def __init__(self,url,data):
        self.url=url
        self.data=data

    def push_event(self):
        try:
            requests.post(self.url,self.data)
        except Exception as e:
            print(e)
            raise e
