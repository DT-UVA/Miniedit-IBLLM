# This script is largely based on a Dockerhub image and can be found at: https://github.com/iwaseyusuke/docker-mininet

FROM ubuntu:24.04

USER root
WORKDIR /root

COPY . /root
RUN rm -rf /root/venv

RUN apt-get update && \
    apt-get install -y \
        python3-pip \
        python3.12-venv \
        curl \
        dnsutils \
        ifupdown \
        iproute2 \
        iptables \
        iputils-ping \
        mininet \
        net-tools \
        openvswitch-switch \
        openvswitch-testcontroller \
        tcpdump \
        vim \
        x11-xserver-utils \
        xterm \
        python3-tk \
    && rm -rf /var/lib/apt/lists/* \
    && touch /etc/network/interfaces \
    && chmod +x /root/ENTRYPOINT.sh

RUN python3 -m venv /root/venv \
    && . /root/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r /root/requirements.txt

EXPOSE 6633 6653 6640

ENTRYPOINT ["/root/ENTRYPOINT.sh"]