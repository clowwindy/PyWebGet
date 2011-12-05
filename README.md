# [PyWebGet](https://github.com/clowwindy/PyWebGet "PyWebGet Homepage")
A background HTTP download manager with a web interface.

## Dependency
 Python 2.6 ~ Python 2.7, Unix/Linux or Windows.

## Install
 Just copy all the files to the path you want. Then run `./pywebget.py`. Open your browser, open [http://localhost:8090/](http://localhost:8090/). The default username is admin with a blank password.

 The default download directory on Liunx is `/tmp`. You may want to change this in the preferences window. Click the preferences button on the toolbar, a window will popup.

 For more information, run `./pywebget.py -h`

## Config PyWebGet
 Typically the config file is saved to ~/.pywebget/settings.json on Linux.

 You may want to change username and password of the web UI. The password will be hashed before saving to the disk. You can just replace it with a new password(please don't use {} in your password).

## Debian
 Debian or Ubuntu users may want to install PyWebGet as a Debian package.
 To build a deb file, use build_deb.sh.

    sudo ./build_deb.sh
    sudo dpkg -i build/pywebget-0.1.deb

 Now, you have a pywebget service. You can control the service via the following commands:

    sudo /etc/init.d/pywebget start
    sudo /etc/init.d/pywebget stop

 The config file is saved at `/etc/pywebget/settings.json`
