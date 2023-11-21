#!/bin/bash

docker image prune -a
yum clean all
sudo rm -rf /var/chahe/yum/*
