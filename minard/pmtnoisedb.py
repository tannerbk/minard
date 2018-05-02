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

def runs_after_run(run, maxrun=None):
    conn = engine_nl.connect()
    cmd = 'SELECT * FROM pmtnoise WHERE %d < run_number' % run
    if maxrun:
        rows = conn.execute('SELECT * FROM pmtnoise'
                            ' WHERE %s < run_number AND run_number < %s'
                            ' ORDER BY run_number DESC;', 
                            (int(run), int(maxrun)))
    else:
        rows = conn.execute('SELECT * FROM pmtnoise' 
                            ' WHERE %s < run_number'
                            ' ORDER BY run_number DESC;', 
                            (int(run)))
    return dictify(rows)

def get_run_by_number(run):
    conn = engine_nl.connect()
    rows = conn.execute('SELECT * FROM pmtnoise WHERE %s = run_number;', \
                        (int(run)))
    return dictify(rows)
