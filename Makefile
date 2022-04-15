.PHONY: help deploy list test true


PROJECT_NAME ?= health-plus
BLUE := "\e[1;34m"
NC := "\e[0m"
INFO := @bash -c 'printf $(BLUE); echo "=> $$1"; printf $(NC)' VALUE

true:  ## will return true
	${INFO} True

list: ## will list all Make command
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | xargs

make run-server: ## running application server using docker compose up
	${INFO} "Building docker compose"
	@docker-compose build
	${INFO} "Running docker compose"
	@docker-compose up

test:  ## run application test
	${INFO} "Building docker compose"
	@docker-compose -f docker-compose.test.yaml build
	${INFO} "test are running ... "
	@docker-compose -f docker-compose.test.yaml up --exit-code-from webapp
	${INFO} "Test is done"
#	${INFO} "Cleaning up "
#	@$(MAKE) docker_clean

docker_clean: ## delete dangled images
	# Todo add filter to remove only app image
	@docker images -q -f dangling=true  | xargs -I ARGS sudo docker rmi -f ARGS

check-style: ## Check code style
	${INFO} "Checking code style..."
	@pycodestyle . --config=.pycodestyle
	${INFO} "Done"
## TODO install venv
