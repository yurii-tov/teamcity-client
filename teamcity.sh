#!/usr/bin/bash


cd $(readlink -f $(dirname $0))


[ -f settings.json ] || {
    cp settings.json.example settings.json
    echo Config file not found
    echo New file has been created: $(readlink -f settings.json)
    echo Please setup desirable values and try again
    exit 1
}


[ -d venv ] && source $(find -name activate) || \
{
    python -m venv venv
    source $(find -name activate) || exit 1
    pip install -r requirements.txt
}


python teamcity.py "$@"
