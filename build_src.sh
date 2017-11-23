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
find build -iname '*.pyc' -delete
version=$(git describe | grep -E -o "^[[:digit:]]{1,}\.[[:digit:]]{1,}\.[[:digit:]]{1,}-[[:digit:]]{1,}")
    sed -i "s/^VERSION.*/VERSION = '$version'/" build/src/about.py

cd build
debchange --create --package gshell -v $version -D xenial --empty "Some bugs fixed"
dpkg-buildpackage -S -rfakeroot
cd ..
#dput ppa:alexei38/gshell gshell_$version\_source.changes
