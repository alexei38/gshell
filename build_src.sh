#!/bin/bash

export DEBEMAIL='alexei@margasov.ru'
export DEBFULLNAME='Alexei Margasov'

src_dir=$(dirname $0)
src_dir=$(readlink -f $src_dir)

cd $src_dir
rm -rf build
mkdir -p build
cp -r debian build/debian
cp -r src build/src
cp gshell build/gshell
cp Gshell.desktop build/
cd build

version=$(git describe | grep -E -o "^[[:digit:]]{1,}\.[[:digit:]]{1,}\.[[:digit:]]{1,}-[[:digit:]]{1,}")
debchange --create --package gshell -v $version -D trusty --empty "Some bugs fixed"
dpkg-buildpackage -S -rfakeroot
#dput ppa:alexei38/gshell gshell\_$version\_source.changes