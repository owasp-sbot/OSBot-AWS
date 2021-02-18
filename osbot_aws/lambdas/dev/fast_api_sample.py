from osbot_aws.Dependencies import load_dependencies


def run(event, context=None):
    load_dependencies('fastapi,mangum')
    from osbot_aws.lambdas.dev.fastapi.app.main import handler
    return handler(event, context)
