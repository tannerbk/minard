from .db import engine_nl

def get_scintillator_level(run_begin, run_end):

    conn = engine_nl.connect()

    result = conn.execute("SELECT run::INTEGER, scint_lvl FROM scint_level WHERE " 
                          "run >= %s AND run <= %s ORDER BY run", (run_begin, run_end))

    keys = map(str, result.keys())
    rows = result.fetchall()

    return [dict(zip(keys,row)) for row in rows]


def get_av_z_offset(run_begin, run_end):

    conn = engine_nl.connect()

    result = conn.execute("SELECT run::INTEGER, av_offset_z FROM av_offset WHERE " 
                          "run >= %s AND run <= %s ORDER BY run", (run_begin, run_end))

    keys = map(str, result.keys())
    rows = result.fetchall()

    return [dict(zip(keys,row)) for row in rows]

