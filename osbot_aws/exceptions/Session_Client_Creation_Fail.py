class Session_Client_Creation_Fail(Exception):

    def __init__(self, status):
        self.status  = status
        self.message = status.get('message')
        self.data    = status.get('data')
        self.error   = status.get('error')
        super().__init__(self.message)

    def __str__(self):
        return self.message