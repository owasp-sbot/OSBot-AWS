ACCOUNT_ID="785217600689"
REGION="eu-west-1"
PROFILE="${ACCOUNT_ID}_AdministratorAccess"

#aws ecr get-login-password --region $REGION --profile $PROFILE | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

echo "***************************************"
echo "Building Lambda Docker image for Python"

export IMAGE_NAME=${ACCOUNT_ID}.dkr.ecr.$REGION.amazonaws.com/python-for-lambda
docker build -t $IMAGE_NAME .
echo
echo "*** Logging in docker to AWS ECR"
echo
CONTAINER_ID=$(docker run -it --rm -p 9000:8080 -d $IMAGE_NAME)

echo
echo "*** test image"
echo
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"name":"world!"}'
echo
echo
echo "*** stop image (which will be automaticaly deleted)"
echo
docker stop $CONTAINER_ID
echo

echo "publishing image"

docker push $IMAGE_NAME

