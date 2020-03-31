#!/usr/bin/env bash
set -e

coverage erase

coverage run -m unittest discover tests

coverage report -m
