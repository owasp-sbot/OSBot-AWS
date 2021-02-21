import sys


class Session_Bad_Credentials(Exception):

    def __init__(self, exception, print_error_message= True):
        error_code    = exception.get("Code")                               # todo: refactor into separate methods
        error_message = exception.get('Message')
        message = (f"\tCurrent Security credentials are invalid! \n\n"
                   f"\tPlease check: current environment values, "
                   f"profile name or value in your ~/.aws/credentials file"
                   f"\n\n"
                   f"\tBoto3 Error message: {error_code}  {error_message}")
        self.message             = message
        self.print_error_message = print_error_message
        if self.print_error_message:
            print()
            print("\n*********** OSBot_AWS ***********\n")
            print(f"{self.message}")
            print("\n*********** OSBot_AWS ***********\n")

        super().__init__(self.message)