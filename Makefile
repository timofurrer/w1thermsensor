tests:
	@tox

deb:
	debuild -us -uc

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
