FROM diniscruz/osbot_utils:latest

WORKDIR /app

COPY pyproject.toml requirements.txt README.md ./
COPY ./osbot_aws ./osbot_aws

RUN pip install -e .
RUN rm -f osbot_utils-1.11.14-py3-none-any.whl

COPY ./docker/python_slim/examples ./examples

CMD ["python", "./examples/example_1.py"]