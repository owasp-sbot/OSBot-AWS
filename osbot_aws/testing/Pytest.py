from osbot_utils.testing.Pytest import skip_pytest__if_env_var_is_not_set


def skip_pytest___aws_pytest_user_name__is_not_set():
    skip_pytest__if_env_var_is_not_set('AWS_PYTEST_USER_NAME')
