include Makefile.conf

VERSION=$(shell cat VERSION)
PACKAGE_NAME=$(NAME)-$(VERSION)

PYTAG=$(shell grep python-tag setup.cfg | sed 's/python-tag\s=\s//')

#paths
SOURCE_PATH=source/
PROJECT_SOURCE_PATH=$(SOURCE_PATH)$(NAME)

##result paths
RESULTS_PATH=results/
ARTIFACTS_PATH=$(RESULTS_PATH)artifacts/
PACKAGE_PATH=$(RESULTS_PATH)package/

#files
VERSION_FILE=$(RESULTS_PATH)version.txt
PACKAGE=$(PACKAGE_PATH)$(PACKAGE_NAME)-$(PYTAG)-none-any.whl
ARTIFACTS=$(PACKAGE) $(VERSION_FILE)
MAKEFILE_CONF=Makefile.conf
PROJECT_CONF=Project.conf

#Commands
PYTHON=python3
GIT=git
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
$(PROJECT_CONF): 
	cat $(MAKEFILE_CONF) > $(PROJECT_CONF)
	echo "" >> $(PROJECT_CONF)
	echo "VERSION="$(VERSION) >> $(PROJECT_CONF)
	echo "DEPENDENCIES=$(shell grep -vE "^\s*#" requirements.txt)" >> $(PROJECT_CONF)

$(PACKAGE): $(PROJECT_CONF)
	$(PYTHON) setup.py bdist_wheel --dist-dir=$(PACKAGE_PATH) # Info in setup.cfg

$(VERSION_FILE):
	echo "NAME="$(NAME) > $(VERSION_FILE)
	echo "VERSION="$(VERSION) >> $(VERSION_FILE)
	echo "REPOSITORY="$(REPOSITORY) >> $(VERSION_FILE)
	echo "REVISION="`$(GIT) rev-parse HEAD^{commit}` >> $(VERSION_FILE)

init:
	pip install -r requirements.txt
