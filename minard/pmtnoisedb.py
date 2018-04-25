from .db import engine_nl

import sys

# all fields 
fields = ['average_nhit_trigenabled',
          'run_number',
          'analyze_time',
          'average_noiserate',
          'online_pmt',
          'average_nhit_normal',
          'n_pgt',
          'average_qhl_thresh',
          'average_qhl_peak',
          'average_qhs_peak',
          'run_time',
          'average_qhs_hhp',
          'average_qhs_thresh',
          'average_nhit_raw',
          'average_qhl_hhp',
          'average_noise_crate',
          'average_qhl_hhp_crate',
          'timestamp']

def dictify(rows):
    rv = []
    for row in rows:
        d = {}
        for i,f in enumerate(fields):
            d[f] = row[i]
        rv.append(d)
    return rv

def runs_after_run(run, maxrun='+inf'):
    conn = engine_nl.connect()
    cmd = 'SELECT * FROM pmtnoise WHERE %d < run_number' % run
    if maxrun < '+inf':
        cmd += ' AND run_number < %d' % maxrun
    cmd += ';'
    rows = conn.execute(cmd)
    return dictify(rows)

def get_run_by_number(run):
    conn = engine_nl.connect()
    cmd = 'SELECT * FROM pmtnoise WHERE %d = run_number;' % int(run)
    rows = conn.execute(cmd)
    return dictify(rows)
