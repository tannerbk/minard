import sqlalchemy
from .db import engine
import time

penn_daq_tests = {
    "Crate CBal": 0,
    "ZDisc": 1,
    "Set TTot": 2,
    "GTValid": 3,
    "Pedestal": 4,
    "CGT": 5,
    "Get TTot": 6,
    "FEC Test": 7, 
    "Disc Check": 8
}

def test_failed_str(tests):
    """
    Convert an integer specifying the ECAL tests that failed
    to a string listing the failed ECAL tests.
    """
    test_failed = ""
    for test in penn_daq_tests.keys():
        bit = penn_daq_tests[test]
        if not tests & (1<<bit):
            continue
        test_failed += str(test) + ", "
    test_failed = test_failed[0:-2]

    return test_failed

def get_penn_daq_tests(crate, slot, channel):
    """
    Get the ECAL tests that failed for a specified CCC
    """
    conn = engine.connect()

    result = conn.execute("SELECT tests_failed FROM test_status WHERE "
         "crate = %s AND slot = %s AND channel = %s", (crate, slot, channel))

    rows = result.fetchone()

    if rows is None:
        return None

    rows = rows[0]
    test_failed = test_failed_str(rows)

    return test_failed

def penn_daq_ccc_by_test(test, crate_sel, slot_sel, channel_sel):
    """
    Get the CCCs for all the tests that failed for a specified
    test (can by "All" of them).
    """
    conn = engine.connect()

    if test != "All":
        test_bit = penn_daq_tests[test]

    result = conn.execute("SELECT DISTINCT ON (crate, slot) "
        "crate, slot, ecalid, mbid, dbid, problems FROM test_status "
        "WHERE crate < 19 ORDER BY crate, slot, timestamp DESC")

    rows = result.fetchall()
    if rows is None:
        return None

    result = conn.execute

    ccc = []
    for crate, slot, ecalid, mbid, dbid, problems in rows:
        if crate_sel != -1 and crate != crate_sel:
            continue
        if slot_sel != -1 and slot != slot_sel:
            continue
        for channel in range(len(problems)):
            if channel_sel != -1 and channel != channel_sel:
                continue
            db_id = dbid[channel/8]
            if test == "All" and problems[channel] != 0 or \
               test != "All" and problems[channel] & (1<<test_bit):
                tests_failed = test_failed_str(problems[channel])
                ccc.append((crate, slot, channel, ecalid, \
                            hex(int(mbid)), hex(int(db_id)), tests_failed))
    return ccc

def ecal_state(crate, slot, channel):
    """
    Get the hardware values determined by the ECAL for a CCC
    """
    conn = engine.connect()

    result = conn.execute("SELECT vthr, tcmos_isetm, vbal_0, vbal_1, "
        "mbid, dbid, tdisc_rmp FROM fecdoc WHERE crate = %s AND slot = %s "
        "ORDER BY timestamp DESC", (crate, slot))

    keys = result.keys()
    rows = result.fetchone()

    if rows is None:
        return None

    data = dict(zip(keys, rows))
    data['mbid'] = hex(int(data['mbid']))
    data['dbid'] = hex(int(data['dbid'][channel/8]))
    data['vbal_0'] = int(data['vbal_0'][channel])
    data['vbal_1'] = int(data['vbal_1'][channel])
    data['vthr'] = int(data['vthr'][channel])
    data['isetm0'] = int(data['tcmos_isetm'][0])
    data['isetm1'] = int(data['tcmos_isetm'][1])
    data['rmp'] = int(data['tdisc_rmp'][channel/4])

    return data

