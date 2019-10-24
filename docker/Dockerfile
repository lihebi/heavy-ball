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

# For some reason the sys.path does not include site-packages
# directory.  But using PYTHONPATH is a hack, as both python2 and
# python3 use it. But I probably should not add it here, but in
# profile instead.
# ENV PYTHONPATH "${PYTHONPATH}:/usr/lib/python2.7/site-packages"

FROM myubuntu

# so that bashrc can detect and set PS1 properly
ENV DOCKER_ENVIRONMENT "set"

RUN useradd -m -s /bin/bash hebi && echo "hebi:hebi" | chpasswd && usermod -aG sudo hebi
RUN echo "root:root" | chpasswd

USER hebi
WORKDIR /home/hebi

RUN mkdir .vnc
ADD xstartup .vnc/xstartup
ADD xstartup-xmonad .vnc/xstartup-xmonad
ADD xstartup-stumpwm .vnc/xstartup-stumpwm
ADD Xresources .Xresources

RUN echo "vnc" | vncpasswd -f > .vnc/passwd && chmod 600 .vnc/passwd

ADD startvnc.sh startvnc.sh

# it turns out all the copied files are owned by root
USER root
RUN sudo chown -R hebi:hebi /home/hebi
USER hebi

CMD ["/home/hebi/startvnc.sh"]

# TODO clone my repositories
RUN git clone https://github.com/lihebi/emacs.d .emacs.d
RUN git clone https://github.com/lihebi/dothebi .hebi
RUN .hebi/install.sh
RUN sh .hebi/setup-git.sh

# TODO is it possible to create multi-stage build with CMD in middle layers?
# TODO reduce number of layers by chaining commands
