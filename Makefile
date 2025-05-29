#Commands
COVERAGE=python3-coverage
PYLINT=pylint
LINECOUNT=sloccount --duplicates --wide --details
RM=rm -rf

#targets
.PHONY: clean dev_doc help

clean:
	$(RM) results/
	$(RM) .coverage
	$(RM) build/
	find . -name "*~" -delete
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

help:
	$(info Available targets:)
	$(info dev_doc: serve documentation)
	$(info clean: cleans repository)
	$(info help: displays this message)
	@:

dev_doc:
	cd documentation/user_doc/ && mkdocs serve -a localhost:8888

