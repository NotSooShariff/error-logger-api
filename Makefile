APP_NAME = error-logger-api
DOCKER_IMAGE = $(APP_NAME)-image
DOCKER_CONTAINER = $(APP_NAME)-container

.PHONY: all build run stop remove clean test git-init git-status

all: build run

build:
	docker build -t $(DOCKER_IMAGE) .

run:
	docker run -d --name $(DOCKER_CONTAINER) -p 8000:8000 $(DOCKER_IMAGE)

stop:
	docker stop $(DOCKER_CONTAINER)

remove:
	docker rm $(DOCKER_CONTAINER)

clean: stop remove
	docker rmi $(DOCKER_IMAGE)

test:
	docker run --rm $(DOCKER_IMAGE) pytest ../tests/test.py

git-init:
	git init
	git add .
	git commit -m "Initial commit"

git-status:
	git status

push-lin:
	./git-push.sh

push-win:
	@call git-push.bat