#!/bin/bash

nodecount=4
for name in templates/*; do
    name=$(basename $name)
    for nodeid in $(seq 1 $nodecount); do
        echo "Generating xml/${name%%.*}$nodeid.xml"
        sed -e 's|@NEMID[@]|$nodeid|g' \
            -e 's|@NODEID[@]|$nodeid|g' \
            templates/$name > xml/${name%%.*}$nodeid.xml
    done
done


