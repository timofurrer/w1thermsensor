.PHONY: tests deb

tests:
	@tox

tests-all: tests docker-deb

deb:
	debuild -us -uc

docker-deb:
	docker build . -t w1thermsensor
	docker run --rm -v $(shell pwd):/src w1thermsensor /src/tests/integration/test_build_deb_pkg.sh

travis-prepare-integration:
	./tests/integration/travis-run-hack.sh docker pull timofurrer/w1thermsensor

travis-integration-tests:
	./tests/integration/travis-run-hack.sh docker run --rm -v $(shell pwd):/src timofurrer/w1thermsensor /src/tests/integration/test_build_deb_pkg.sh

deploy-docker-hub:
	docker build . -t timofurrer/w1thermsensor
	docker push timofurrer/w1thermsensor:latest

lint:
	pylint w1thermsensor

install:
	pip install .

readme:
	pandoc README.md --from markdown --to rst -o README.rst

publish: readme
	python setup.py sdist register upload

manpages:
	python setup.py --command-packages=click_man.commands man_pages --target docs/
