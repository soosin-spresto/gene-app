.PHONY: test clean

default: up

help:
	@echo 'Management commands:'
	@echo
	@echo 'Usage:'
	@echo '    make build   Compile the project.'
	@echo '    make up      Start the service.'
	@echo '    make down    Stops project.'
	@echo '    make clean   Clean project.'
	@echo

build:
	docker-compose build --parallel

up:
	docker-compose up app

rup:
	docker-compose up  -d redis

eup:
	docker-compose up  -d kibana

down:
	docker-compose down --remove-orphans

clean: down
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
