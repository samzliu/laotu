all: init run

init: run.sh
	chmod +x run.sh

run:
	./run.sh
