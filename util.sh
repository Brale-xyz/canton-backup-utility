#!/bin/sh

network=$1
cmd=$2

if [ -z "$network" ]; then
    poetry run python src/util.py
elif [ -z "$cmd" ]; then
    poetry run python src/util.py -n $network
else
    poetry run python src/util.py -n $network -c $cmd
fi