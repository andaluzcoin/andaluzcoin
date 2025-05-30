#!/usr/bin/env bash
#
# Copyright (c) 2020-present The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

export LC_ALL=C.UTF-8

export CONTAINER_NAME=ci_native_centos
export CI_IMAGE_NAME_TAG="quay.io/centos/centos:stream9"
export STREAM_GCC_V="12"
export CI_BASE_PACKAGES="gcc-toolset-${STREAM_GCC_V}-gcc-c++ glibc-devel gcc-toolset-${STREAM_GCC_V}-libstdc++-devel ccache make git python3 python3-pip which patch xz procps-ng dash rsync coreutils bison e2fsprogs cmake"
export PIP_PACKAGES="pyzmq"
export GOAL="install"
export ANDALUZCOIN_CONFIG="-DWITH_ZMQ=ON -DBUILD_GUI=ON -DREDUCE_EXPORTS=ON"
