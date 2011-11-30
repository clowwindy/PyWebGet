#! /bin/sh

export VERSION=0.1
export DEBFULLNAME="pywebget"
export DEBEMAIL="clowwindy42@gmail.com"

name=pywebget-0.1
install_path=/opt/pywebget/

# check if is run as root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# copy files
rm -rf build
mkdir -p build/$name$install_path

cp -r core build/$name$install_path
cp -r share build/$name$install_path
cp -r simplejson build/$name$install_path
cp -r static build/$name$install_path
cp -r web build/$name$install_path
cp -r webui build/$name$install_path
cp -r core build/$name$install_path
cp pywebget.py build/$name$install_path/pywebget
cp LICENSE build/$name$install_path
cp README build/$name$install_path

find build/$name$install_path -name '*.pyc' -print | xargs rm -f

# minimize js files

java -jar packaging/utils/yuicompressor-2.4.6.jar build/$name$install_path/static/js/jquery.dataTables.js -o build/$name$install_path/static/js/jquery.dataTables.min.js
rm -f build/$name$install_path/static/js/jquery.dataTables.js
mv build/$name$install_path/static/js/jquery.dataTables.min.js build/$name$install_path/static/js/jquery.dataTables.js

java -jar packaging/utils/yuicompressor-2.4.6.jar build/$name$install_path/static/js/pywebget.js -o build/$name$install_path/static/js/pywebget.min.js
rm -f build/$name$install_path/static/js/pywebget.js
mv build/$name$install_path/static/js/pywebget.min.js build/$name$install_path/static/js/pywebget.js

java -jar packaging/utils/yuicompressor-2.4.6.jar build/$name$install_path/static/css/Aristo/Aristo.css -o build/$name$install_path/static/css/Aristo/Aristo.min.css
rm -f build/$name$install_path/static/css/Aristo/Aristo.css
mv build/$name$install_path/static/css/Aristo/Aristo.min.css build/$name$install_path/static/css/Aristo/Aristo.css


# copy init scripts

mkdir -p build/$name/etc/init.d/
cp packaging/debian/init.sh build/$name/etc/init.d/pywebget

cd build/
tar -czf $name.orig.tar.gz $name/

# copy debian scripts
cd $name/
mkdir DEBIAN
cp -u ../../packaging/debian/control DEBIAN/
cp -u ../../packaging/debian/postinst DEBIAN/
cp -u ../../packaging/debian/prerm DEBIAN/
cp -u ../../packaging/debian/postrm DEBIAN/

sudo chown root:root -R .
cd ..

# make deb
dpkg-deb --build pywebget-0.1
rm -rf ../build/$name
rm -f ../build/$name.orig.tar.gz
