IMAGE_TYPE=python-for-lambda
IMAGE_TYPE=icap-client
ACCOUNT_ID="785217600689"
REGION="eu-west-1"
PROFILE="${ACCOUNT_ID}_AdministratorAccess"

echo
echo "*** Logging in docker to AWS ECR"
echo
aws ecr get-login-password --region $REGION --profile $PROFILE | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

echo
echo "*** Building Lambda Docker image for ${IMAGE_TYPE}"
echo

export IMAGE_NAME=${ACCOUNT_ID}.dkr.ecr.$REGION.amazonaws.com/${IMAGE_TYPE}
docker build -t $IMAGE_NAME .

echo
echo "*** Starting container in local docker host with newly created image"
echo

#CONTAINER_ID=$(docker run -it --rm -p 9000:8080 -d $IMAGE_NAME)

echo
echo "*** invoke locally hosted lambda"
echo

#curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"name":"world!"}'

echo
echo "*** stop container (which will be deleted on stop)"
echo

docker stop $CONTAINER_ID

echo
echo "*** publishing image to AWS ECR"
echo
docker push $IMAGE_NAME

echo
echo "*** all done"
echo

