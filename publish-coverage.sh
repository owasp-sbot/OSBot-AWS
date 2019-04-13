#!/usr/bin/env bash

export COVERALLS_REPO_TOKEN=T8G6bB0sBkk5q2C12PRKnzeeEOAW3OGCL
export COVERALLS_SERVICE_NAME=$(git describe --always)

cd tests && pytest -v --cov=osbot_aws --json=report.json
cp tests/.coverage .
coveralls