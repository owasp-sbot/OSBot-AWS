echo "***** Run lambda handler locally"
#docker run --rm -v "$PWD":/var/task:ro,delegated lambci/lambda:python3.8 lambda_function.run '{"name":"world"}'

# start watcher
#docker run --rm                             \
#           -e DOCKER_LAMBDA_WATCH=1         \
#           -e DOCKER_LAMBDA_STAY_OPEN=1     \
#           -p 9001:9001                     \
#           -v "$PWD":/var/task:ro,delegated \
#           lambci/lambda:python3.8          \
#           lambda_function.run

# run commands (or bash interactively)
docker run --rm -it --entrypoint bash lambci/lambda:python3.8
#docker run --rm -it --entrypoint bash lambci/lambda:python3.8 -c pwd

# invoke like this
#curl -d '{"name":"world"}' http://localhost:9001/2015-03-31/functions/myfunction/invocations


# dev version of python build
#docker run --rm lambci/lambda:build-python3.8 aws --version