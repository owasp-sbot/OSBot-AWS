#!/usr/bin/env bash

export COVERALLS_REPO_TOKEN=T8G6bB0sBkk5q2C12PRKnzeeEOAW3OGCL
cd tests && pytest -v --cov=osbot_aws --json=report.json
cp tests/.coverage .
coveralls