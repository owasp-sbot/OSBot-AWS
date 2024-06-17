source .env
IMAGE_TYPE=lambda_python_nginx_supervisord
ACCOUNT_ID="${AWS_ACCOUNT_ID}"
REGION="${AWS_DEFAULT_REGION}"
IMAGE_NAME=${ACCOUNT_ID}.dkr.ecr.$REGION.amazonaws.com/${IMAGE_TYPE}

echo
echo "*** Logging in docker to AWS ECR"
echo
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com


echo
echo "*** Building Lambda Docker image for ${IMAGE_TYPE}"
echo


#docker build -t $IMAGE_NAME .
cd ../..  # Navigate to the context directory
docker build --platform linux/amd64 -t $IMAGE_NAME -f ./docker/lambda_python_nginx_supervisord/Dockerfile .

exit 0
echo
echo "*** publishing image to AWS ECR"
echo
docker push $IMAGE_NAME

echo
echo "*** all done"
echo

#echo
#echo "*** Run locally"
#echo
docker run --platform linux/amd64 -it --rm -p 8080:8080 $IMAGE_NAME
