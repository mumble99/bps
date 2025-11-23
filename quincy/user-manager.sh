#! /bin/sh

mode="$1"
MAIN_USER_FILE="conf/users"

if [[ $EUID -ne 0 ]] ; then
    echo "run as root"
    exit 1
fi

if [[ -z $mode || ! $mode =~ ^(add|delete)$ ]] ; then
    echo "usage: $0 add|delete"
    exit 1
fi

if [ "$mode" = "add" ] ; then
    mkdir -p temp
    touch temp/users
    docker run --rm -it -v ./temp:/etc/quincy m0dex/quincy:latest quincy-users --add /etc/quincy/users
    cat temp/users >> $MAIN_USER_FILE
    rm -rf temp
else
    read -p "Enter username: " username
    sed -i "/^${username}/d" $MAIN_USER_FILE
fi