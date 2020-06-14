.PHONY: tests deb

W1THERMSENSOR_NO_KERNEL_MODULE=1

tests:
	@tox

tests-all: docker-deb

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

manpages:
	python3 setup.py --command-packages=click_man.commands man_pages --target docs/
