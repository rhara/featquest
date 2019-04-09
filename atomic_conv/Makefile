SHELL = /bin/bash

.PHONY: list bulkrun clean mkbulkrun bulkrun all

list:
	@echo Please specify one of the targets\;
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

mkbulkrun: bulkrun.sh

bulkrun.sh: mkbulkrun.py
	python $< v2015 > $@

bulkrun: bulkrun.sh
	bash $<

all:
	python concat_npz.py

clean:
	rm -rf *.npz
