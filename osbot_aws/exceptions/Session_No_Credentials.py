import sys


class Session_No_Credentials(Exception):

    def __init__(self, print_error_message= True):
        message = (f"\tNo Security credentials where found\n\n"
                   f"\tPlease check: current environment values, "
                   f"profile name or value in your ~/.aws/credentials file")
        self.print_error_message = print_error_message
        if self.print_error_message:
            print()
            print("\n*********** OSBot_AWS ***********\n")
            print(f"{message}")
            print("\n*********** OSBot_AWS ***********\n")

        super().__init__(message)