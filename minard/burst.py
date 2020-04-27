import couchdb
from . import app

def load_burst_runs(offset, limit):
    """
    Returns a dictionary with the burst runs loaded from couchdb. The dummy itterator is used as key
    to keep the ordering from the couchdb query. The content of the couchdb document is stored as values.
    This loads ALL the documents in burst database, ordered by run_subrun_burst logic.
    The logic to limit and split the results per page was implemented.
    """
    server = couchdb.Server("http://snoplus:"+app.config["COUCHDB_PASSWORD"]+"@"+app.config["COUCHDB_HOSTNAME"])
    db = server["burst"]

    i = 0 #the counter keeps the ordering correct
    results = {}
    skip = offset
    all = db.view('_design/burst/_view/burst_by_run', descending=True, skip=skip)
    total = all.total_rows
    offset = all.offset
    for row in db.view('_design/burst/_view/burst_by_run', descending=True, limit=limit, skip=skip):
        run = row.key[0]
        run_id = row.id
        try:
            results[i] = dict(db.get(run_id).items())
        except KeyError:
            app.logger.warning("Code returned KeyError searching for burst information in the couchDB. Run Number: %d" % run)
        i += 1

    return results, total, offset, limit

def burst_run_detail(run_number, subrun, sub):
    """
    Returns a dictionary that is a copy of the couchdb document for specific run_subrun_burst.
    """
    server = couchdb.Server("http://snoplus:"+app.config["COUCHDB_PASSWORD"]+"@"+app.config["COUCHDB_HOSTNAME"])
    db = server["burst"]

    startkey = [run_number, subrun, sub]
    endkey = [run_number, subrun, sub]
    rows = db.view('_design/burst/_view/burst_by_run', startkey=startkey, endkey=endkey, descending=False, include_docs=True)
    for row in rows:
        run_id = row.id
        try:
            result = dict(db.get(run_id).items())
        except KeyError:
            app.logger.warning("Code returned KeyError searching for burst_details information in the couchDB. Run Number: %d" % run_number)
        files = "%i_%i_%i" % (run_number,subrun,sub)

    return result, files
