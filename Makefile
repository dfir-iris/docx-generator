include Makefile.conf

VERSION=$(uv version --short)

#paths
DOCUMENTATION_SOURCE_DIR=documentation/user_doc/
##result paths
RESULTS_PATH=results/
ARTIFACTS_PATH=$(RESULTS_PATH)artifacts/
DOCUMENTATION_RESULTS_PATH=$(RESULTS_PATH)documentation/
BUNDLED_DOCUMENTATION=$(RESULTS_PATH)docx_generator_documentation_$(VERSION).tar.gz

#files
ARTIFACTS=$(BUNDLED_DOCUMENTATION)

#Commands
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
	$(RM) .coverage
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

dev_doc:
	cd $(DOCUMENTATION_SOURCE_DIR) && mkdocs serve -a localhost:8888

$(BUNDLED_DOCUMENTATION): $(shell find $(DOCUMENTATION_SOURCE_DIR) -type f) | $(DOCUMENTATION_RESULTS_PATH)
	cd $(DOCUMENTATION_SOURCE_DIR) && mkdocs build --clean -d ../../$(DOCUMENTATION_RESULTS_PATH)
	tar czvf $(BUNDLED_DOCUMENTATION) $(RESULTS_PATH)documentation/

#paths creation
$(DOCUMENTATION_RESULTS_PATH):
	mkdir -p $(DOCUMENTATION_RESULTS_PATH)
