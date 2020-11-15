#!/usr/bin/bash


cd $(readlink -f $(dirname $0))


[ -f config ] || {
    cp config.example config
    echo Config file not found
    echo New file has been created: $(readlink -f config)
    echo Please setup desirable values and try again
    exit 1
}
source config


[ -d venv ] && source $(find -name activate) || \
{
    python -m venv venv
    source $(find -name activate) || exit 1
    pip install -r requirements.txt
}


python teamcity.py "$@"
