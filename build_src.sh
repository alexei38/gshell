#!/bin/bash

src_dir=$(dirname $0)
src_dir=$(readlink -f $src_dir)

cd $src_dir
version=$(git describe)
rm -f debian/changelog
debchange --create --package gshell -v $version -D trusty --empty "Some bugs fixed"
dpkg-buildpackage -S -rfakeroot

#dput ppa:alexei38/gshell <source.changes>