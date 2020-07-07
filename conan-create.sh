#!/usr/bin/env bash

set -xe

fn_get()
{
    echo `cat conanfile.py | grep "$1 =" | awk '{ print $3 }' | xargs`
}

fn_log()
{
    echo "## NIO #############################"
    echo "$1"
    echo "####################################"
}

CONANFILE_NAME=$(fn_get name)
CONANFILE_VERSION=$(fn_get version)
CONANFILE_STREAM="nio/latest"
CONAN_PACKAGE_NAME="${CONANFILE_NAME}/${CONANFILE_VERSION}@${CONANFILE_STREAM}"

fn_log "CONAN CREATE: $CONAN_PACKAGE_NAME"
conan create . ${CONANFILE_STREAM}

fn_log "CONAN INFO: $CONAN_PACKAGE_NAME"
conan info ${CONAN_PACKAGE_NAME}

