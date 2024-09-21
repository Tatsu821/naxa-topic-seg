#!/bin/bash
docker run \
    -d \
    --init \
    --rm \
    -p 5002:5002 \
    -it \
    --ipc=host \
    --name=nhk-metadata \
    --env-file=.env \
    --volume=$PWD:/workspace \
    nhk-metadata \
    fish
