from .db import engine_nl

# turn a sql result into a list of dicts
def dictify(rows):
    keys = rows.keys()
    rv = []
    for row in rows:
        d = {}
        for k in keys:
            d[k] = row[k]
        rv.append(d)
    return rv

def runs_after_run(run, maxrun='+inf'):
    conn = engine_nl.connect()
    cmd = 'SELECT * FROM pmtnoise WHERE %d < run_number' % run
    if maxrun < '+inf':
        cmd += ' AND run_number < %d' % maxrun
    cmd += ' ORDER BY run_number DESC;'
    rows = conn.execute(cmd)
    return dictify(rows)

def get_run_by_number(run):
    conn = engine_nl.connect()
    cmd = 'SELECT * FROM pmtnoise WHERE %d = run_number;' % int(run)
    rows = conn.execute(cmd)
    return dictify(rows)
