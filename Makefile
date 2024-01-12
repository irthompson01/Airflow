.ONSHELL:
.PHONY: docker
docker: # run the server as a docker container
	docker-compose up --build
