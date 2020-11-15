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


[ -d venv ] && source venv/bin/activate || \
{
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
}


python teamcity.py "$@"
