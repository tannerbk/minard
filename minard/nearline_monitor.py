from .db import engine, engine_nl
from .detector_state import get_latest_run
from .pingcratesdb import ping_crates_list
from .channelflagsdb import get_channel_flags, get_channel_flags_by_run
from .triggerclockjumpsdb import get_clock_jumps, get_clock_jumps_by_run
from .nlrat import RUN_TYPES
from .occupancy import run_list, occupancy_by_trigger, occupancy_by_trigger_limit

# Limits for failing channel flags check
OUT_OF_SYNC_1 = 32
OUT_OF_SYNC_2 = 64
MISSED_COUNT_1 = 64
MISSED_COUNT_2 = 256

# Limits for failing clock jump check
CLOCK_JUMP_1 = 10
CLOCK_JUMP_2 = 20

def get_run_list(limit, selected_run, all_runs):
    '''
    Returns dictionaries keeping track of a list
    of failures for each nearline job
    '''

    if not selected_run:
        ping_crates_status = ping_crates(limit, all_runs)
        channel_flags_status = channel_flags(limit, all_runs) 
        clock_jumps_status = clock_jumps(limit, all_runs)
        occupancy_status = occupancy(limit, all_runs)
    else:
        ping_crates_status = ping_crates_run(selected_run)
        channel_flags_status = channel_flags_run(selected_run)
        clock_jumps_status = clock_jumps_run(selected_run)
        occupancy_status = occupancy_run(selected_run)

    return clock_jumps_status, ping_crates_status, channel_flags_status, occupancy_status


def occupancy_run(run):
    '''
    Return the ESUM occupancy status of a selected run
    '''
    occupancy_fail = {}
    status,_,_ = occupancy_by_trigger_limit(0, run)
    try:
        if status[run] == 1:
            occupancy_fail[run] = 1
        elif status[run] == 0:
            occupancy_fail[run] = 0
    except Exception as e:
        occupancy_fail[run] = -1

    return occupancy_fail


def occupancy(limit, all_runs):
    '''
    Return a dictionary of ESUM occupancy status by run
    '''
    occupancy_fail = {}
    status,_,_ = occupancy_by_trigger_limit(limit, 0)
    for run in all_runs:
        try:
            # Check ESUMH Occupancy
            if status[run] == 1:
                occupancy_fail[run] = 1
            elif status[run] == 0:
                occupancy_fail[run] = 0
        except Exception as e:
            occupancy_fail[run] = -1
            continue

    return occupancy_fail


def clock_jumps_run(run):
    '''
    Return the clock jumps status for a selected run
    '''
    clock_jumps_status = {}
    conn = engine_nl.connect()

    result = conn.execute("SELECT run FROM trigger_clock_jumps WHERE run = %s", run)

    # This should be the best way to check if the job ran for the given run
    try:
        result.fetchone()[0]
    except Exception as e:
        clock_jumps_status[run] = -1
        return clock_jumps_status

    data10, data50 = get_clock_jumps_by_run(run)
    njump10 = len(data10)
    njump50 = len(data50)
    if((njump10 + njump50) >= CLOCK_JUMP_1 and \
       (njump10 + njump50) < CLOCK_JUMP_2):
        clock_jumps_status[run] = 2
    elif(njump10 + njump50 >= CLOCK_JUMP_2):
        clock_jumps_status[run] = 1
    else:
        clock_jumps_status[run] = 0

    return clock_jumps_status


def clock_jumps(limit, all_runs):
    '''
    Return a dictionary of clock jumps status by run
    '''
    clock_jumps_fail = {}

    _, njump10, njump50 = get_clock_jumps(limit, 0) 
    for run in all_runs:
        try:
            if((njump10[run] + njump50[run]) >= CLOCK_JUMP_1 and \
               (njump10[run] + njump50[run]) < CLOCK_JUMP_2):
                clock_jumps_fail[run] = 2
            elif(njump10[run] + njump50[run] >= CLOCK_JUMP_2):
                clock_jumps_fail[run] = 1
            else:
                clock_jumps_fail[run] = 0
        except Exception as e:
            clock_jumps_fail[run] = -1
            continue

    return clock_jumps_fail


def channel_flags_run(run):
    '''
    Return the channel flags status for a selected run
    '''
    channel_flags_status = {}
    conn = engine_nl.connect()

    result = conn.execute("SELECT sync16 FROM channel_flags WHERE run = %s", run)

    # This should be the best way to check if the job ran for the given run
    try:
        result.fetchone()[0]
    except Exception as e:
        channel_flags_status[run] = -1
        return channel_flags_status
    
    missed, sync16, sync24, _, _ = get_channel_flags_by_run(run)
    missed = len(missed)
    sync16 = len(sync16)
    sync24 = len(sync24)
    if((sync16 >= OUT_OF_SYNC_1 and sync16 < OUT_OF_SYNC_2) or \
        missed >= MISSED_COUNT_1 and missed < MISSED_COUNT_2):
        channel_flags_status[run] = 2
    elif(sync16 >= OUT_OF_SYNC_2 or missed >= MISSED_COUNT_2):
        channel_flags_status[run] = 1
    else:
        channel_flags_status[run] = 0

    return channel_flags_status 


def channel_flags(limit, all_runs):
    '''
    Return a dictionary of channel flags status by run
    '''
    _, _, _, count_sync16, _, count_missed, count_sync16_pr, _ = get_channel_flags(limit)
    channel_flags_fail = {}
    for run in all_runs:
        run = int(run)
        try:
            if((count_sync16[run] >= OUT_OF_SYNC_1 and count_sync16[run] < OUT_OF_SYNC_2) or \
                count_missed[run] >= MISSED_COUNT_1 and count_missed[run] < MISSED_COUNT_2):
                channel_flags_fail[run] = 2
            elif(count_sync16[run] >= OUT_OF_SYNC_2 or count_missed[run] >= MISSED_COUNT_2 or \
                 count_sync16_pr[run] >= OUT_OF_SYNC_2):
                channel_flags_fail[run] = 1
            else:
                channel_flags_fail[run] = 0
        except Exception as e:
            channel_flags_fail[run] = -1
            continue

    return channel_flags_fail


def ping_crates_run(run):
    '''
    Return ping crates status for selected run
    '''
    conn = engine_nl.connect()

    ping_crates_status = {}
    result = conn.execute("SELECT status FROM ping_crates WHERE run = %i" % run)
    try:
        row = result.fetchone()[0]
        if row == 0:
            ping_crates_status[run] = 0
        elif row == 1:
            ping_crates_status[run] = 1
        elif row == 2:
            ping_crates_status[run] = 2
    except Exception as e:
        ping_crates_status[run] = -1

    return ping_crates_status


def ping_crates(limit, all_runs):
    '''
    Return a dictionary of ping crates status by run
    '''
    ping_list = ping_crates_list(limit, 0)
    ping_crates_fail = {}
    ping_runs = []
    for i in ping_list:
        run = int(i[1])
        ping_runs.append(run)
        if i[6] == 1:
            ping_crates_fail[run] = 1
        elif i[6] == 0:
            ping_crates_fail[run] = 0
        elif i[6] == 2:
            ping_crates_fail[run] = 2
    for run in all_runs:
        if run in ping_runs:
            continue
        ping_crates_fail[run] = -1

    return ping_crates_fail


def run_type(selected_run):
    '''
    Return the run_type for a selected run
    '''
    conn = engine.connect()

    result = conn.execute("SELECT run_type FROM run_state WHERE run > %s" % selected_run)
    row = result.fetchone()[0]
    runtypes = {}
    for i in range(len(RUN_TYPES)):
        if (row & (1<<i)):
            runtypes[selected_run] = RUN_TYPES[i]
            break

    return runtypes


def get_run_types(limit):
    '''
    Return a dictionary of run types for each run in the list
    '''
    conn = engine.connect()

    latest_run = get_latest_run()

    result = conn.execute("SELECT run, run_type FROM run_state WHERE run > %s", \
                          (latest_run - limit))

    rows = result.fetchall()

    runtypes = {}
    for run, run_type in rows:
        for i in range(len(RUN_TYPES)):
            if (run_type & (1<<i)):
                runtypes[run] = RUN_TYPES[i]
                break

    return runtypes

