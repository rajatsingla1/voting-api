PYTHON := python3.10

# define name of virtual environment directory
VENV := venv

# default target, when make is executed without arguments
all: venv

# create a virtual environment and install dependencies
# TODO: put env source here so that we know what DB to connect to
$(VENV)/bin/activate: requirements.txt
	$(PYTHON) -m venv $(VENV)
	./$(VENV)/bin/pip install -r requirements.txt

# venv is a shortcut target
venv: $(VENV)/bin/activate

run: venv
	./$(VENV)/bin/uvicorn main:app --reload

test: venv
	./$(VENV)/bin/pytest -v

clean:
	@echo "Removing virtual environment and cache files/directories"
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf .pytest_cache

help:
	@echo "-----------------------------  HELP  --------------------------------"
	@echo "Command: 'make' - create virtual environment and install dependencies"
	@echo "Command: 'make venv' - activate the virtual environment"
	@echo "Command: 'make run' - runs the application"
	@echo "Command: 'make test' - tests the application using pytest"
	@echo "Command: 'make clean' - removes all venv and cache files/directories"
	@echo "---------------------------------------------------------------------"