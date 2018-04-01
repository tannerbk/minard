Data Sources
============

Dispatch Stream
---------------

The dispatch stream is processed by the `minard_dispatch
<https://github.com/snoplus/minard/blob/master/bin/minard_dispatch>`_
script and written to the redis database.

To run the dispatch processor as a daemon::

    $ source [/path/to/virtual-env]/bin/activate
    $ minard-dispatch --host [dispatcher ip]

To see how to set up a local dispatcher see :doc:`dispatch_local`.

Data Stream
-----------

The data stream is processed directly from a socket connection to the data
server. The stream is processed by two scripts:

`minard-cmos
<https://github.com/snoplus/minard/blob/master/bin/minard-cmos>`_
    This script processes the CMOS count records from the data stream server
    and updates the CMOS rates in the redis database.

`minard-base
<https://github.com/snoplus/minard/blob/master/bin/minard-base>`_
    This script processes the base current records from the data server and
    updates the base currents in the redis database.

For more information on the data file formats see `Data File Format
<http://snopl.us/detector/html/daq.html>`_.

To mimic the data stream see :doc:`mimic_data`.

