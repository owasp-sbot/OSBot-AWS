FROM python:3.12-slim

# Install nginx supervisor and gettext
RUN apt-get update                              && \
    apt-get install -y --no-install-recommends  \
    nginx                                       \
    supervisor                                  \
    gettext                                     && \
    apt-get clean                               && \
    rm -rf /var/lib/apt/lists/*

COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.3 /lambda-adapter /opt/extensions/lambda-adapter

RUN pip install osbot_aws

COPY ./docker/lambda_python_nginx_supervisord/nginx.conf /etc/nginx/nginx.conf

COPY ./docker/lambda_python_nginx_supervisord/public /var/task/app/public

#
#COPY ./docker/lambda_python_nginx_supervisord/app.py ${LAMBDA_TASK_ROOT}
#
#CMD ["app.lambda_handler"]
CMD ["nginx", "-g", "daemon off;"]