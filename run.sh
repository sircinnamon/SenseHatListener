#!/bin/bash

NETWORK_IP=172.10.10.0/24
NGINX_IP=172.10.10.2
PYTHON_IP=172.10.10.3

NETWORK_NAME=sensehat

PYTHON_HOSTNAME=python

NGINX_CONTAINER=sh-nginx
PYTHON_CONTAINER=sh-python

docker network create \
	--subnet $NETWORK_IP \
	--opt com.docker.network.bridge.name=$NETWORK_NAME \
	--opt com.docker.network.bridge.enable_icc=true \
	$NETWORK_NAME

docker rm $PYTHON_CONTAINER
docker run -d \
	-v $(pwd)/sensehat_listener.py:/sensehat_listener.py \
	-v $(pwd)/dummy_sense_hat.py:/dummy_sense_hat.py \
	-v /etc/localtime:/etc/localtime:ro \
	--name $PYTHON_CONTAINER \
	--net $NETWORK_NAME --ip $PYTHON_IP \
	--privileged \
	sensehat python3 /sensehat_listener.py 80

docker rm $NGINX_CONTAINER
docker run -d \
	-v $(pwd)/nginx.conf:/etc/nginx/nginx.conf \
	-v $(pwd)/webroot:/var/www/html \
	-v $(pwd)/openapi.yaml:/var/www/html/openapi.yaml \
	-v /etc/localtime:/etc/localtime:ro \
	--name $NGINX_CONTAINER \
	--add-host=$PYTHON_HOSTNAME:$PYTHON_IP \
	--net $NETWORK_NAME --ip $NGINX_IP \
	-p 8080:8080 \
	nginx:1.14.0