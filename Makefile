SHELL=/bin/bash
PYTHON = python3
COMPOSE = docker-compose
COMPOSE_F = /home/amadmin/box4s/docker/box4security.yml

images = `arg="$(filter-out $@,$(MAKECMDGOALS))" && echo $${arg:-${1}}`


help: 
	@echo "---------------HELP-----------------"
	@echo "make build <image> # builds the container, e.g. make build web"
	@echo "make push <image> # pushes the container, e.g. make push web"
	@echo "make recreate <image> # recreates the container, e.g. make recreate web"
	@echo "make nocache <image> # builds the container without cache, e.g. make nocache web"
	@echo "------------------------------------"

build:
	sudo ${COMPOSE} -f ${COMPOSE_F} build $(call images)

push:
	sudo ${COMPOSE} -f ${COMPOSE_F} push $(call images)

nocache:
	sudo ${COMPOSE} -f ${COMPOSE_F} build --nocache $(call images)
	
recreate:
	sudo ${COMPOSE} -f ${COMPOSE_F} up -d --force-recreate $(call images)

%:
	@: