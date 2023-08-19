
install:
	@echo Nothing to be done for upgrade scripts as pure python

clean:
	-del *.pyc *.pyd *.pyo

.DEFAULT:
	@echo Nothing to be done for upgrade scripts as pure python

.PHONY:
	runtests

runtests:
	$(PYTHON3) -u run_tests.py
