FROM public.ecr.aws/lambda/python:3.12

RUN pip install osbot_aws

COPY ./docker/lambda_python_nginx_supervisord/app.py ${LAMBDA_TASK_ROOT}

CMD ["app.lambda_handler"]