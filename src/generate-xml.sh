#!/bin/bash

nodecount=4

olsd_name=$(find /usr/lib* -name "olsrd_txtinfo.so*" -print 2> /dev/null)
olsd_name=$(basename $olsd_name)

for name in templates/*; do
    name=$(basename $name)
    for nodeid in $(seq 1 $nodecount); do
        name1=${name/.template/}
        name2=${name1%.*}$nodeid.${name1#*.}
        echo "Generating xml/$name2"
        sed -e "s|@NEMID[@]|$nodeid|g" \
            -e "s|@NODEID[@]|$nodeid|g" \
            -e "s|@OLSRTXTINFO[@]|$olsd_name|g" \
            templates/$name > xml/$name2
    done
done
