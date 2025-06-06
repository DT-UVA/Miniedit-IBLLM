#!/usr/bin/env bash

# This script is largely based on a Dockerhub image and can be found at: https://github.com/iwaseyusuke/docker-mininet

service openvswitch-switch start
ovs-vsctl set-manager ptcp:6640

echo "Started openvswitch-switch service"

if [ $# -gt 0 ]
then
  if [ "$1" == "mn" ]
  then
    bash -c "$@"
  else
    mn "$@"
  fi
else
  bash
fi

service openvswitch-switch stop