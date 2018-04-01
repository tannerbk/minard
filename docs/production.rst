Production Install
==================

To install minard for production use, just run make install::

    git clone git@github.com/snoplus/minard
    cd minard
    sudo make install

The install rule will:

    * create a virtual environment in `/opt/minard`
    * install/update minard
    * set up init scripts and configuration files for gunicorn and nginx

In addition to this, you will have to separately:

    * install redis
    * install nginx
    * set up init scripts and configuration files for redis
    * install/update disp
    * create users `gunicorn`, `minard`, `nginx`
    * set up the iptables rules to allow the L2 and nearline processes to write to redis

Some of the above procedures are automated via salt, and some are not. To get
everything installed from scratch you should have a look at the `SNO+ computing
manual <https://snopl.us/detector/documents/snoplus_computing_manual.pdf>`_ and
talk to experts.
