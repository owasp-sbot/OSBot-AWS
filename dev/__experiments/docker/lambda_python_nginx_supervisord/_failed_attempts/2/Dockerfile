FROM public.ecr.aws/awsguru/nginx:1.23.2023.3.11.1

COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.3 /lambda-adapter /opt/extensions/lambda-adapter

# config files
ADD ./docker/lambda_python_nginx_supervisord/nginx.conf /opt/nginx/conf/nginx.conf

# code files
COPY ./docker/lambda_python_nginx_supervisord/public /var/task/app/public

# Install dependencies for building Python
RUN yum update -y && \
    yum groupinstall -y "Development Tools" && \
    yum install -y openssl-devel bzip2-devel libffi-devel wget

# Download and install Python 3.12
RUN cd /usr/src && \
    wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz && \
    tar xzf Python-3.12.0.tgz && \
    cd Python-3.12.0 && \
    ./configure --enable-optimizations && \
    make altinstall && \
    ln -s /usr/local/bin/python3.12 /usr/bin/python3 && \
    cd / && \
    rm -rf /usr/src/Python-3.12.0.tgz /usr/src/Python-3.12.0 \

ENTRYPOINT ["python", "--version"]