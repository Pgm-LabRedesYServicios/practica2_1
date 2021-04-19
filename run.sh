#!/usr/bin/env bash
set -euo pipefail

# docker build -t zentauro/asterisk:0.1 .
docker run -ti --rm \
    -v "${PWD}/../logs":/var/log/asterisk \
    -v "${PWD}/configs":/etc/asterisk \
    -p 5060:5060 \
    -p 8088:8088 \
    -p 5038:5038 \
    zentauro/asterisk:0.1
