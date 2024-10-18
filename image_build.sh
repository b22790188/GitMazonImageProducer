#!/bin/bash

DOCKER_USERNAME=$DOCKER_USERNAME
DOCKER_PASSWORD=$DOCKER_PASSWORD
REPO_OWNER=$1
REPO_NAME=$2
REPO_OWNER_LOWER=$(echo "$REPO_OWNER" | tr '[:upper:]' '[:lower:]')
REPO_NAME_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')

# change directory name
if [ -d ${REPO_OWNER}_${REPO_NAME} ]; then
	echo "${REPO_OWNER}_${REPO_NAME} already exists. Pulling latest changes..."
	cp Dockerfile ${REPO_OWNER}_${REPO_NAME}/
	cd ${REPO_OWNER}_${REPO_NAME}/
	git pull
else
	git clone https://github.com/${REPO_OWNER}/${REPO_NAME}.git ${REPO_OWNER}_${REPO_NAME}
	cp Dockerfile ${REPO_OWNER}_${REPO_NAME}/
	cd ${REPO_OWNER}_${REPO_NAME}/
fi

sudo docker image build -t b22790188/${REPO_OWNER_LOWER}_${REPO_NAME_LOWER}:latest .

sudo docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}

sudo docker push b22790188/${REPO_OWNER_LOWER}_${REPO_NAME_LOWER}:latest
