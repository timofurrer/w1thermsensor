#!/bin/bash

# This script is used to allow conditional Travis CI Build Stage Jobs

ERROR_MSG='Travis CI run conditions not met - thus do nothing'

if [[ -z "${TRAVIS_TAG}" || "${TRAVIS_TAG}" == "false" ]] && [[ "${TRAVIS_BRANCH}" != "master" ]]; then
    echo "${ERROR_MSG}"
    exit 0
fi

eval $@
