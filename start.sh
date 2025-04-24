#!/bin/bash

# shellcheck disable=SC2164
source venv/bin/activate
env -S "$(cat .env)" python main.py
