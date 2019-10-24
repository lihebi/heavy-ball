# ubuntu is using service, not systemctl
FROM ubuntu:18.04 AS myubuntu

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y
RUN apt-get install -y apt-utils
RUN apt-get install -y build-essential pkg-config cmake autoconf
RUN apt-get install -y git cloc
# RUN apt-get install -y sqlite3 libsqlite3-dev libboost-all-dev libgtest-dev
# RUN apt-get install -y libpugixml-dev doxygen
RUN apt-get install -y emacs
RUN apt-get install -y wget
# RUN apt-get install -y libtinfo-dev libz-dev
# RUN apt-get install -y subversion
RUN apt-get install -y locate

RUN apt-get install -y openbox
RUN apt-get install -y stumpwm
RUN apt-get install -y tigervnc-standalone-server
RUN apt-get install -y xterm
# testing xmonad
RUN apt-get install -y xmonad
RUN apt-get install -y xmobar dmenu suckless-tools
RUN apt-get install -y sudo
RUN apt-get install -y rxvt-unicode
RUN apt-get install -y tmux htop silversearcher-ag
RUN apt-get install -y python python-dev python-pip
RUN apt-get install -y python3 python3-dev python3-pip
RUN apt-get install -y lxc lxd

# lxc will install libpam-cgfs, but this package will make all sudo
# command output warnings:
#
#     PAM-CGFS[324]: Failed to get list of controllers
#     sudo[324]: pam_unix(sudo:session): session closed for user root
#     PAM-CGFS[324]: Failed to get list of controllers
#
# But I probably don't need it anyway, so removing it
RUN apt-get remove -y libpam-cgfs

# For some reason the sys.path does not include site-packages
# directory.  But using PYTHONPATH is a hack, as both python2 and
# python3 use it. But I probably should not add it here, but in
# profile instead.
# ENV PYTHONPATH "${PYTHONPATH}:/usr/lib/python2.7/site-packages"

# Setup lxd here. This has to be in one RUN, because the service is
# stopped across RUNs.
#
# Also I'm not enabling this because this requires --privileged during
# docker run, and that is not directly available in docker build. See
# https://github.com/moby/moby/issues/1916 and
# https://github.com/docker/buildx. Specifically, I'll need:
#
#     docker buildx build --allow security.insecure -t xxx .
#
# RUN service lxd start &&\
#         service lxd status &&\
#         lxd init --auto
#
# I would probably want to start the lxd service automatically? This
# should go into the startup.sh script

# Emane dependencies
RUN apt-get install -y libxml2-dev libpcap-dev libpcre3 uuid-dev\
        protobuf-compiler libprotobuf-dev python-protobuf python-lxml libtool

# Emane tutorial dependencies
RUN apt-get install -y iproute2 python3-pyqt5\
        gpsd gpsd-clients olsrd iperf iperf3

# mgen?
# RUN apt-get install -y mgen

# opentestpoint
RUN apt-get install -y python-dev libsqlite3-dev libczmq-dev python-setuptools

FROM myubuntu

# so that bashrc can detect and set PS1 properly
ENV DOCKER_ENVIRONMENT "set"

RUN useradd -m -s /bin/bash hebi &&\
        echo "hebi:hebi" | chpasswd &&\
        usermod -aG sudo hebi
RUN echo "root:root" | chpasswd

USER hebi
WORKDIR /home/hebi
# clone my config repositories
RUN git clone https://github.com/lihebi/emacs.d .emacs.d
RUN git clone https://github.com/lihebi/dothebi .hebi &&\
        sh .hebi/install.sh &&\
        sh .hebi/setup-git.sh

# FIXME WORKDIR does not seem to create dir
RUN mkdir git
WORKDIR /home/hebi/git
# clone emane repositories
RUN git clone https://github.com/adjacentlink/opentestpoint
RUN git clone https://github.com/USNavalResearchLaboratory/mgen
RUN git clone https://github.com/adjacentlink/pynodestatviz
RUN git clone https://github.com/lihebi/emane

# TODO this fork is private
# https://github.com/adjacentlink/emane-tutorial
# RUN git clone https://git.ece.iastate.edu/hebi/emane-tutorial

# setup VNC
WORKDIR /home/hebi
RUN mkdir .vnc
ADD xstartup .vnc/xstartup
ADD xstartup-xmonad .vnc/xstartup-xmonad
ADD xstartup-stumpwm .vnc/xstartup-stumpwm
ADD Xresources .Xresources

RUN echo "vnc" | vncpasswd -f > .vnc/passwd &&\
        chmod 600 .vnc/passwd

ADD startvnc.sh startvnc.sh
CMD ["/home/hebi/startvnc.sh"]

# it turns out all the copied files are owned by root
USER root
RUN sudo chown -R hebi:hebi /home/hebi
USER hebi

# TODO reduce number of layers by chaining commands
