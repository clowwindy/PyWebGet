#! /bin/sh

export VERSION=0.1
export DEBFULLNAME="pywebget"
export DEBEMAIL="clowwindy42@gmail.com"

name=pywebget-0.1
install_path=/opt/pywebget/

rm -rf build_deb
mkdir -p build_deb/$name$install_path

cp -r core build_deb/$name$install_path
cp -r share build_deb/$name$install_path
cp -r simplejson build_deb/$name$install_path
cp -r static build_deb/$name$install_path
cp -r web build_deb/$name$install_path
cp -r webui build_deb/$name$install_path
cp -r core build_deb/$name$install_path
cp pywebget build_deb/$name$install_path
cp LICENSE build_deb/$name$install_path
cp README build_deb/$name$install_path

cd build_deb/

tar -czf $name.orig.tar.gz $name/
cd $name/
mkdir DEBIAN
cp -u ../../packaging/debian/changelog DEBIAN/
cp -u ../../packaging/debian/control DEBIAN/
cp -u ../../packaging/debian/ DEBIAN/
cp -u ../../packaging/debian/* DEBIAN/
cp -u ../../packaging/debian/* DEBIAN/
cd ..
dpkg-deb --build pywebget-0.1