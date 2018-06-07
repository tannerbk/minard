import sqlalchemy
from .db import engine, engine_test

penn_daq_tests = {
    0: "Crate CBal",
    1: "ZDisc",
    2: "Set TTot",
    3: "GTValid",
    4: "Pedestal",
    5: "CGT",
    6: "Get TTot",
    7: "FEC Test", 
    8: "Disc Check"
}

def test_failed_str(tests):
    """
    """
    test_failed = ""
    for bit in penn_daq_tests.keys():
        if not tests & (1<<bit):
            continue
        test_failed += str(penn_daq_tests[bit]) + ", "
    test_failed = test_failed[0:-2]

    return test_failed

def get_penn_daq_tests(crate, slot, channel):
    """
    """
    conn = engine_test.connect()

    result = conn.execute("SELECT tests_failed FROM penn_daq_test_status WHERE "
                          "crate = %s AND slot = %s AND channel = %s", (crate, slot, channel))

    rows = result.fetchone()

    if rows is None:
        return None

    rows = rows[0]
    test_failed = test_failed_str(rows)

    return test_failed

def penn_daq_ccc_by_test(test):
    """
    """
    conn = engine_test.connect()

    if test != -1:
        test_bit = (1<<test)
        result = conn.execute("SELECT DISTINCT ON (crate, slot, channel) "
                              "crate, slot, channel, tests_failed "
                              "FROM penn_daq_test_status "
                              "WHERE (tests_failed & %s > 0) ORDER BY "
                              "crate, slot, channel, timestamp DESC", (test_bit,))
    else:
        result = conn.execute("SELECT DISTINCT ON (crate, slot, channel) "
                              "crate, slot, channel, tests_failed "
                              "FROM penn_daq_test_status WHERE (tests_failed > 0) "
                              "ORDER BY crate, slot, channel, timestamp DESC")


    rows = result.fetchall()
    for i, arr in enumerate(rows):
        rows[i] = list(rows[i])
        test_failed = test_failed_str(arr[3])
        rows[i][3] = test_failed

    return rows

def ecal_state(crate, slot, channel):
    """
    """
    conn = engine.connect()

    result = conn.execute("SELECT vthr, tcmos_isetm, vbal_0, vbal_1, "
                          "mbid, dbid, tdisc_rmp FROM fecdoc WHERE "
                          "crate = %s AND slot = %s ORDER BY timestamp "
                          "DESC", (crate, slot))

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

