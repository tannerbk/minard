List of Monitoring Software
===========================

minard-dispatch
--------------------

* **Command**: ``minard-dispatch [--host HOST]``
* **Runs as**: minard
* **Started by**: /etc/init.d/minard-dispatch
* **Log File**: ``/var/log/minard/minard_dispatch_*.log``
* **Description**: Reads events from the dispatch stream and updates the stream info in the redis database.

redis
-----

* **Command**: ``redis``
* **Runs as**: root
* **Snapshot**: ``/opt/redis/dump.rdb``
* **Configuration file**: ``/etc/redis/6379.conf``
* **Ports**: 6379
* **Started by**: ``/etc/init.d/redis_6379``
* **Log File**: ``/var/log/redis.log``
* **Description**: redis database.

gunicorn
--------

* **Command**: ``gunicorn -b 0.0.0.0:8080 minard:app --user=gunicorn``
* **Run as** : root (drops to gunicorn)
* **Ports**: 8080
* **Started by**: ``/etc/init.d/gunicorn``
* **Log File**: ``/tmp/minard.log`` and ``/var/log/gunicorn.log``
* **Description**: Gunicorn web server which serves the main site.

gunicorn (logging server)
-------------------------

* **Command**: ``gunicorn -b 0.0.0.0:8081 snoplus_log:app --user=gunicorn``
* **Run as** : root (drops to gunicorn)
* **Ports**: 8081
* **Started by**: supervisord
* **Log File**: ``/tmp/snoplus_log.log`` and ``/var/log/gunicorn_log.log``
* **Description**: Gunicorn web server for logging.

nginx
-----

* **Command**: ``nginx -c /etc/nginx/nginx.conf``
* **Run as** : root (drops to nginx)
* **Configuration file**: ``/etc/nginx/nginx.conf``
* **Ports**: 50000
* **Started by**: ``/etc/init.d/nginx``
* **Log File**: ``/var/log/nginx/error.log`` and ``/var/log/nginx/access.log``
* **Description**: nginx web server which serves static files and slow clients for the main site.

minard-cmos
-----------

* **Command**: ``minard-cmos [--host HOST] [--port PORT] [--logfile LOGFILE] [-d] [--loglevel LOGLEVEL]``
* **Run as**: minard
* **Ports**: 5557
* **Started by**: /etc/init.d/minard-cmos
* **Log File**: ``/var/log/minard/minard_cmos.log``
* **Description**: Reads CMOS rates from the data server and writes to the redis database.

minard-base
-----------

* **Command**: ``minard-base [--host HOST] [--port PORT] [--logfile LOGFILE] [-d] [--loglevel LOGLEVEL]``
* **Run as**: minard
* **Started by**: /etc/init.d/minard-base
* **Log File**: ``/var/log/minard/minard_base.log``
* **Description**: Reads base currents from the data server and writes to the redis database.
