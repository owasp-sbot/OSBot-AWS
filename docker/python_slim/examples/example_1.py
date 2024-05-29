from osbot_aws.aws.sts.STS import STS
from osbot_utils.utils.Dev import pprint


class OSBot_AWS__Example_1:

    def main(self):
        sts = STS()
        sts.check_current_session_credentials()
        print(f"your current identity is:")
        pprint(sts.caller_identity())

if __name__ == '__main__':
    OSBot_AWS__Example_1().main()
