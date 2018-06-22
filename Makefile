.PHONY: help clean

help:
	@echo "Usage: make TARGET"
	@echo "TARGETs:"
	@echo "  clean   rm -vrf ./build ./dist ./.tox ./*.pyc ./*.tgz ./*.egg-info AUTHORS ChangeLog"
	@echo "  help    display this help and exit"

clean:
	rm -vrf ./build ./dist ./.tox ./*.pyc ./*.tgz ./*.egg-info AUTHORS ChangeLog
