# Contributing

Thank you for helping `w1thermsensor` to get a better piece of software.

## Support

If you have any questions regarding the usage of `w1thermsensor` please use [StackOverflow](https://stackoverflow.com).

## Reporting Issues / Proposing Features

Before you submit an Issue or proposing a Feature check the existing Issues in order to avoid duplicates. <br>
Please make sure you provide enough information to work on your submitted Issue or proposed Feature:

* Which version of w1thermsensor are you using?
* Which version of python are you using?
* On which platform are you running w1thermsensor?

## Pull Requests

We are very happy to receive Pull Requests considering:

* Style Guide. Follow the rules of [PEP8](http://legacy.python.org/dev/peps/pep-0008/), but you may ignore *too-long-lines* and similar warnings. The CI uses flake8 to ensure proper styling.
* Tests. If our change affects python code inside the source code directory, please make sure your code is covered by an automated test case.

### Testing

To test the w1thermsensor source code against all supported python versions you should use *tox*:

```bash
cd ~/work/w1thermsensor
pip3 install tox
tox
```

However, if you want to test your code on certain circumstances you can create a *virtualenv*:

```
cd ~/work/w1thermsensor
virtualenv env -p python3
source env/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip install .
pytest tests/
```

## AUTHORS file
Please feel free to open a Pull Request and add yourself to the `AUTHORS` file. <br>
Well, ... only if you've done some considerable changes :beers:
