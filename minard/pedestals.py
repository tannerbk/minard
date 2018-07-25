from .db import engine

def get_pedestals(crate, slot, channel):

    conn = engine.connect()

    result = conn.execute("SELECT DISTINCT ON (crate, slot, channel, cell) "
        "qhs_avg, qhl_avg, qlx_avg FROM pedestals WHERE "
        "crate = %s AND slot = %s AND channel = %s ORDER "
        "BY crate, slot, channel, cell, timestamp DESC", (crate, slot, channel))

    rows = result.fetchall()

    qhs_ped = []
    qhl_ped = []
    qlx_ped = []
    for qhs, qhl, qlx in rows:
        qhs_ped.append(qhs)
        qhl_ped.append(qhl)
        qlx_ped.append(qlx)

    return qhs_ped, qhl_ped, qlx_ped

