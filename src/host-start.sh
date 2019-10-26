#!/bin/bash

prefix=node-
bridge=emanenode0

source utils.sh

function create_bridge {
    # create bridge
    if (check_bridge $bridge)
    then
        echo "Creating bridge: $bridge"
        brctl addbr $bridge
        wait_for_device $bridge 10
        ip link set $bridge up
        sleep 1
        ip addr add 10.99.0.100/24 dev $bridge
        iptables -I INPUT -i $bridge -j ACCEPT
        iptables -I FORWARD -i $bridge -j ACCEPT
    else
        echo "Found bridge: $bridge"
    fi
}

function generate_node_config {
    nodeid=$1
    name=$prefix$nodeid
    hex=$(printf "%02x" $nodeid)
    cat <<EOF > host-tmp/lxc.conf.$nodeid
lxc.uts.name=$name
lxc.net.0.type=veth
lxc.net.0.name=eth1
lxc.net.0.flags=up

lxc.net.0.link=$bridge
lxc.net.0.hwaddr=02:00:$hex:01:00:01
lxc.net.0.ipv4.address=10.99.0.$nodeid/24
lxc.net.0.veth.pair=veth$nodeid.1

lxc.net.1.type=veth
lxc.net.1.name=eth2
lxc.net.1.hwaddr=02:00:$hex:02:00:01
lxc.net.1.veth.pair=veth$nodeid.2

lxc.net.2.type = empty
lxc.net.2.flags=up

lxc.console.path = none
lxc.tty.max = 1
lxc.pty.max = 128

# FIXME what is setting a?
lxc.cgroup.devices.allow = a
lxc.mount.auto = proc sys cgroup

lxc.autodev = 1

# (HEBI: FIXME why this is absolute path?)
# lxc.hook.autodev = $topdir/$demoid/persist/$nodeid/var/run/lxc.hook.autodev.sh
lxc.hook.autodev = /tmp/lxc.hook.autodev.sh
lxc.apparmor.profile = unconfined

# fix problem
lxc.cgroup.devices.allow =
lxc.cgroup.devices.deny =

EOF
}

function generate_autodev {
    cat <<EOF > /tmp/lxc.hook.autodev.sh
#!/bin/bash -
if ! [ -c /dev/net/tun ]; then
 mkdir -p /dev/net
 mknod -m 666 /dev/net/tun c 10 200
fi

EOF

    chmod a+x host-tmp/lxc.hook.autodev.sh
}

function create_node {
    nodeid=$1
    name=$prefix$nodeid
    hex=$(printf "%02x" $nodeid)

    generate_autodev $nodeid
    # FIXME this seems to be the same across different nodes
    generate_node_config

    lxc-execute -f host-tmp/lxc.conf.$nodeid \
                -n $name \
                -o host-tmp/lxc-execute.log.$nodeid \
                -- \
                node-init.sh \
                "$(pwd)" \
                $nodeid $nodecount 2> /dev/null &
    while (! test -f host-tmp/lxc-execute.log.$nodeid)
    do
        sleep 1
    done
}

function main {
    check_euid
    create_bridge
    # disable realtime scheduling contraints
    sysctl kernel.sched_rt_runtime_us=-1
    # I'm going to use only 4 nodes
    nodecount=4
    rm -rf host-tmp
    mkdir host-tmp
    for nodeid in $(seq 1 $nodecount); do
        create_node $nodeid
    done

    start_emaneeventservice eventservice.xml \
                            host-tmp/emaneeventservice.log \
                            host-tmp/emaneeventservice.pid \
                            host-tmp/emaneeventservice.uuid \
                            "$starttime"
    start_otestpoint_broker \
        otestpoint-broker.xml \
        host-tmp/otestpoint-broker.log \
        host-tmp/otestpoint-broker.pid \
        host-tmp/otestpoint-broker.uuid

}

main
