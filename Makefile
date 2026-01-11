# Makefile for common tasks
.PHONY: build up down logs test shell clean

IMAGE_NAME := smartsec:latest

build:
	docker build -t $(IMAGE_NAME) .

build-prod:
	docker build -f Dockerfile.prod -t $(IMAGE_NAME)-prod:latest .

push-prod:
	# Example: docker push <registry>/$(IMAGE_NAME)-prod:latest
	echo "Run docker push manually or configure CI to push to registry"

up:
	docker-compose up -d --build

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	# Run tests inside a container (requires image built)
	docker run --rm -v "$(PWD)":/app -w /app $(IMAGE_NAME) pytest -q

shell:
	docker run --rm -it -v "$(PWD)":/app -w /app $(IMAGE_NAME) /bin/bash

clean:
	rm -rf ./*.db ./*.sqlite data/*
