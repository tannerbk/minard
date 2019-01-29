from __future__ import division
import redis
import time
import os
from sys import exit
from snotdaq import Logger
from psycopg2.pool import ThreadedConnectionPool

log = Logger()

BASELINES = ['100L-Baseline', 
             '100M-Baseline',
             '100H-Baseline',
             '20LB-Baseline', 
             '20-Baseline',
             'ESUMH-Baseline',
             'OWLN-Baseline',
             'OWLEH-Baseline']

# 12-bit ADC over 5V
RESOLUTION = 5/4096

def get_data(p, t1, t2, step, interval, name):
    '''
    Get the baseline data from the redis server.
    '''
    for i in range(t1, t2, step):
        key = 'ts:%i:%i:%s' % (interval,i//interval,name)
        p.get(key)

    x = []
    values = p.execute()
    for y in values:
        if y is None:
            continue
        x.append(float(y))

    return x

def get_baselines(t1, t2, step, interval, baseline_name):
    '''
    Get the baseline values and the number of polls 
    over a specified time.
    '''
    r = redis.Redis()
    p = r.pipeline()

    baselines = get_data(p, t1, t2, step, interval, baseline_name)
    counts = get_data(p, t1, t2, step, interval, 'baseline-count')

    return baselines, counts

def get_sum(b, c): 
    '''
    Calculated the difference betwen sequential baseline polls
    and sum that difference.
    '''
    dbsum = 0
    for i in range(0, len(b)-1):
        # Find the change in baseline for each step
        # by dividing by the number of polls
        baseline_now =  b[i]/c[i] 
        baseline_later = b[i+1]/c[i+1]
        db = baseline_later - baseline_now
        # Sum the change over the entire range
        dbsum += db/RESOLUTION

    return abs(dbsum)

def add_baseline_info(pool, sleep_time, blines):
    '''
    Add the summed baseline information to the database.
    '''
    try:
        conn = pool.getconn()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO mtca_baselines (time, n100_hi, n100_med, n100_lo, n20_lo, n20_med, esumh, owl_esumh, owln) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (sleep_time, blines['100H-Baseline'], blines['100M-Baseline'], blines['100L-Baseline'], blines['20LB-Baseline'], blines['20-Baseline'], blines['ESUMH-Baseline'], blines['OWLEH-Baseline'], blines['OWLN-Baseline']))
        cursor.close()
        conn.commit()
        pool.putconn(conn)
    except Exception as e:
        print "Error updating the database: %s" % str(e)
        exit()

def daemonize():
    if os.fork() != 0:
        os._exit(0)

    os.setsid()

    f = open('/dev/null', 'w')

    fd = f.fileno()

    os.dup2(fd, 0)
    os.dup2(fd, 1)
    os.dup2(fd, 2)

if __name__=='__main__':

    import argparse
    parser = argparse.ArgumentParser(description="Baseline monitor")
    parser.add_argument("--step", type=int, default=1) 
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--sleep", type=float, default=30.0)
    parser.add_argument("--log-server", default='teststand.sp.snolab.ca')
    parser.add_argument("--db-user", default="snotdaq")
    parser.add_argument("--db-host", default="minard.sp.snolab.ca")
    parser.add_argument("--db-port", default=5432)
    parser.add_argument("--db-name", default="test")
    parser.add_argument("--db-pass", default=None)
    parser.add_argument("--daemonize", "-d", action='store_true')
    args = parser.parse_args()

    if args.daemonize:
        daemonize()

    try:
        log.set_verbosity('notice')
        log.connect('BaselineMonitor', args.log_server, 4001)
    except Exception as e:
        print "Could not connect to log: %s" % str(e)
        exit()

    try:
        if args.db_pass is None:
            pool = ThreadedConnectionPool(1, 5, host=args.db_host, database=args.db_name, \
                                          user=args.db_user, port=args.db_port)
        else:
            pool = ThreadedConnectionPool(1, 5, host=args.db_host, database=args.db_name, \
                                          user=args.db_user, password=args.db_pass, port=args.db_port)
    except Exception as e:
        print "Could not connect to the database: %s" % str(e)
        exit()

    while(True):

        # The sleep time determines the number of
        # seconds we average over for the baseline
        # monitor
        t1 = int(time.time())
        time.sleep(args.sleep)
        t2 = int(time.time())
    
        blines = {}
        for name in BASELINES:

            b, c = get_baselines(t1, t2, args.step, args.interval, name)
            dB = get_sum(b, c)
            blines[name] = dB
            if(dB > 10):
                log.warn("%s baseline value: %d" % (name, dB))

        add_baseline_info(pool, args.sleep, blines) 

