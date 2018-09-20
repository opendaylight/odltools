.PHONY: help clean

clean_artifacts=./*.egg-info ./.eggs ./.tox ./build ./dist ./*.pyc ./*.tgz AUTHORS ChangeLog

help:
	@echo "Usage: make TARGET"
	@echo "TARGETs:"
	@echo "  clean     ${clean_artifacts}"
	@echo "  gitsetup  add commit-msg with signoff and pre-commit hooks"
	@echo "  help      display this help and exit"
	@echo "  release   build the current code and release the distribution"
	@echo "            make release TAG=0.1.25 BRANCH=rel"
	@echo "            - checkout rel-0.1.25"
	@echo "            - update __version__ in __init__.py, tag the repo"
	@echo "            - build the pypi distribution and upload"
	@echo "            - push the commit and tags"

clean:
	rm -vrf ${clean_artifacts}

checkrepo:
	@if [ ! -d ".git" ]; then printf "Error: Run make gitsetup from the root of the repo\n"; exit 1; fi

checktag:
	@if [ "${BRANCH}" = "" ]; then printf "Error: Please enter a BRANCH\n"; exit 1; fi
	@if [ "$$(git branch | grep ${BRANCH})" = "${BRANCH}" ]; then printf "Error: Branch already exists\n"; exit 1; fi
	@if [ "${TAG}" = "" ]; then printf "Error: Please enter a TAG\n"; exit 1; fi
	@if [ "$$(git tag | grep ${TAG})" = "${TAG}" ]; then printf "Error: Tag already exists\n"; exit 1; fi

gitsetup: checkrepo
	scp -p -P 29418 git.opendaylight.org:hooks/commit-msg .git/hooks/ && chmod 755 .git/hooks/commit-msg;
	cp -f .git/hooks/pre-commit.sample .git/hooks/pre-commit

gitco: checkrepo checktag
	git checkout -b ${BRANCH}-${TAG}

gitbranch: checkrepo
	$(eval CURBRANCH=$(shell git rev-parse --abbrev-ref HEAD))
	@printf "current branch: $(CURBRANCH)\n"

gittag: checkrepo checktag
	@printf "updating version and tagging release with TAG: ${TAG}\n"
	sed -ni "/^__version__ = /s/'.*'/'${TAG}'/p" odltools/__init__.py
	git add odltools/__init__.py
	git commit -s -m "release ${TAG}"
	git tag -m "release ${TAG}" -a ${TAG}
	git tag -l

release-build:
	python setup.py sdist bdist_wheel upload
	git push origin HEAD:refs/for/master
	git push origin ${TAG}

release: clean gitbranch gitco gittag release-build
	git checkout $(CURBRANCH)
	git branch -D ${BRANCH}-${TAG}
