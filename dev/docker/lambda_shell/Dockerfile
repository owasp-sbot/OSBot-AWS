FROM public.ecr.aws/lambda/python:3.12

RUN pip install osbot_aws

COPY ./dev/docker/lambda_shell/app.py ${LAMBDA_TASK_ROOT}

CMD ["app.lambda_handler"]
