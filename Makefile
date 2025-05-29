include Makefile.conf

VERSION=$(shell cat VERSION)
PACKAGE_NAME=$(NAME)-$(VERSION)

PYTAG=$(shell grep python-tag setup.cfg | sed 's/python-tag\s=\s//')

#paths
SOURCE_PATH=src/
PROJECT_SOURCE_PATH=$(SOURCE_PATH)$(NAME)
DOCUMENTATION_SOURCE_DIR=documentation/user_doc/
DOCUMENTATION_SOURCE_RESULT_DIR=$(DOCUMENTATION_SOURCE_DIR)site/
##result paths
RESULTS_PATH=results/
ARTIFACTS_PATH=$(RESULTS_PATH)artifacts/
PACKAGE_PATH=$(RESULTS_PATH)package/
DOCUMENTATION_RESULTS_PATH=$(RESULTS_PATH)documentation/
BUNDLED_DOCUMENTATION=$(RESULTS_PATH)docx_generator_documentation_$(VERSION).tar.gz

#files
PACKAGE=$(PACKAGE_PATH)$(PACKAGE_NAME)-$(PYTAG)-none-any.whl
ARTIFACTS=$(PACKAGE) $(BUNDLED_DOCUMENTATION)
MAKEFILE_CONF=Makefile.conf
PROJECT_CONF=Project.conf

#Commands
PYTHON=python3
GIT=git
COVERAGE=python3-coverage
PYLINT=pylint
LINECOUNT=sloccount --duplicates --wide --details
MKDIR=mkdir -p
RM=rm -rf
CP=cp -r


#targets
.PHONY: artifacts clean help

artifacts: $(ARTIFACTS)
	$(MKDIR) $(ARTIFACTS_PATH)
	$(CP) $(ARTIFACTS) $(ARTIFACTS_PATH)

clean:
	$(RM) $(RESULTS_PATH)
	$(RM) $(PROJECT_SOURCE_PATH).egg-info
	$(RM) .coverage
	$(RM) $(PROJECT_CONF)
	$(RM) build/
	find . -name "*~" -delete
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

help:
	$(info Available targets:)
	$(info artifacts: builds all artifacts)
	$(info clean: cleans repository)
	$(info help: displays this message)
	@:

#files creation
$(PROJECT_CONF): VERSION requirements.txt
	cat $(MAKEFILE_CONF) > $(PROJECT_CONF)
	echo "" >> $(PROJECT_CONF)
	echo "VERSION="$(VERSION) >> $(PROJECT_CONF)
	echo "DEPENDENCIES=$(shell grep -vE "^\s*#" requirements.txt)" >> $(PROJECT_CONF)

$(PACKAGE): $(PROJECT_CONF)
	$(PYTHON) setup.py bdist_wheel --dist-dir=$(PACKAGE_PATH) # Info in setup.cfg

init:
	pip install -r dev_requirements.txt
	pip install -r requirements.txt

dev_doc:
	cd $(DOCUMENTATION_SOURCE_DIR) && mkdocs serve -a localhost:8888

$(BUNDLED_DOCUMENTATION): $(shell find $(DOCUMENTATION_SOURCE_DIR) -type f) | $(DOCUMENTATION_RESULTS_PATH)
	cd $(DOCUMENTATION_SOURCE_DIR) && mkdocs build --clean -d ../../$(DOCUMENTATION_RESULTS_PATH)
	tar czvf $(BUNDLED_DOCUMENTATION) $(RESULTS_PATH)documentation/

#paths creation
$(DOCUMENTATION_RESULTS_PATH):
	mkdir -p $(DOCUMENTATION_RESULTS_PATH)
