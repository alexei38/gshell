#!/bin/bash

src_dir=$(dirname $0)
src_dir=$(readlink -f $src_dir)

if type docker >/dev/null 2>&1 ; then
    docker pull debian:7
    docker run --name gshell_build -tid --privileged -v $src_dir:/src debian:7
    docker exec -t gshell_build apt-get update
    docker exec -t gshell_build apt-get install -y dpkg debconf debhelper md5deep git
    docker exec -t gshell_build /bin/sh -c 'mkdir -p /build/gshell/usr/share/applications; \
                                            mkdir -p /build/gshell/usr/share/icons/; \
                                            mkdir -p /build/gshell/usr/bin/; \
                                            cp -r /src/DEBIAN /build/gshell/; \
                                            cp /src/gshell /build/gshell/usr/bin/; \
                                            cp /src/Gshell.desktop /build/gshell/usr/share/applications/; \
                                            cp /src/src/icon/gshell.png /build/gshell/usr/share/icons/; \
                                            cp -r /src/src /build/gshell/usr/share/gshell; \
                                            cd /build/gshell; \
                                            version=$(cd /src/; git describe); \
                                            sed -i "s/VERSION/$version/g" DEBIAN/control; \
                                            md5deep -r usr > DEBIAN/md5sums; \
                                            cd /build; \
                                            fakeroot dpkg-deb --build gshell /src/'

    docker stop gshell_build
    docker rm gshell_build
    echo 'DEB package locate in' $src_dir
    find $src_dir -iname '*.deb'
else
    echo 'Need docker for build'
    exit 1
fi