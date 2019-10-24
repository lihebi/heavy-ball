#!/bin/sh

# FIXME this is not printed out when running as a daemon. Also, error
# messages are not printed.
#
echo "IP Address of this container: " `hostname -i`

echo "Starting lxd service"
echo "hebi" | sudo --stdin service lxd start
service lxd status

echo "Starting openbox session on :5901 .."
vncserver :1 -localhost no -xstartup $HOME/.vnc/xstartup

# echo "Starting xmonad session on :5902 .."
# vncserver :2 -localhost no -xstartup $HOME/.vnc/xstartup-xmonad

# echo "Starting stumpwm session on :5903 .."
# vncserver :3 -localhost no -xstartup $HOME/.vnc/xstartup-stumpwm

echo "Done"

# run bash to keep the machine alive
bash
