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

def get_noise_results(limit=100, offset=0):
    conn = engine_nl.connect()
    rows = conn.execute('SELECT * FROM pmtnoise '
                        'ORDER BY run_number DESC '
                        'LIMIT %s OFFSET %s;', (limit, offset))
    return dictify(rows)
