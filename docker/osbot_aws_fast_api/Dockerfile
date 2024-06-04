FROM diniscruz/osbot_aws:latest

WORKDIR /app

RUN  pip install fastapi
RUN  pip install osbot-github

# todo: should these be in the osbot_aws
RUN apt-get update
RUN apt-get install -y ssh

#CMD ["python", "./examples/example_1.py"]

