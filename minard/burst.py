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

def load_bursts_search(search, start, end, offset, limit):
    """
    Returns a dictionary with the burst runs loaded from couchdb.
    The returned dictionary is given by one of the search conditions on the page:
    either by run, date or GTID which all use corresponding couchdb views.
    """
    server = couchdb.Server("http://snoplus:"+app.config["COUCHDB_PASSWORD"]+"@"+app.config["COUCHDB_HOSTNAME"])
    db = server["burst"]

    i = 0 #the counter keeps the ordering correct
    results = {}
    skip = offset

    if (search == "run"):

        startkey = [int(start), 0, {}]
        endkey = [int(end), {}]

        view = '_design/burst/_view/burst_by_run'

    elif (search == "date"):

        Syear = start[0:4]
        Smonth = start[5:7]
        Sday = start[8:10]
        Eyear = end[0:4]
        Emonth = end[5:7]
        Eday = end[8:10]
        if Smonth[0] == "0": Smonth = Smonth[1]
        if Emonth[0] == "0": Emonth = Emonth[1]
        if Sday[0] == "0": Sday = Sday[1]
        if Eday[0] == "0": Eday = Eday[1]
        startkey = [int(Syear), int(Smonth), int(Sday)]
        endkey = [int(Eyear), int(Emonth), int(Eday)]

        view = '_design/burst/_view/burst_by_date'

    elif (search == "gtid"):

        view = '_design/burst/_view/burst_by_GTID'

    if ((search == "run") or (search == "date")):
        try:
            all = db.view(view, startkey=startkey, endkey=endkey, descending=False)
            total=len(all.rows)
        except:
            app.logger.warning("Code returned KeyError searching for burst information in the couchDB.")

        for row in db.view(view, startkey=startkey, endkey=endkey, descending=False, skip=skip, limit=limit):
            if (search == "run"): run = row.key[0]
            elif (search == "date"): run = row.value[0]
            run_id = row.id
            try:
                results[i] = dict(db.get(run_id).items())
            except KeyError:
                app.logger.warning("Code returned KeyError searching for burst information in the couchDB. Run Number: %d" % run)
            i += 1

        return results, total, offset, limit

    elif (search == "gtid"): ### because this needs to loop through all docs, skip and limit won't work here

        for row in db.view(view, descending=False):
            startgtid = int(row.key[0])
            endgtid = int(row.key[1])

            if (endgtid < startgtid): ### case for gtid roll-over
                if ( (int(start) >= startgtid) and (int(start) <= pow(2,24)) ) or ( (int(end) <= endgtid) and (int(end) >= 0 ) ):
                    run = row.value[0]
                    run_id = row.id

                    try:
                        results[i] = dict(db.get(run_id).items())
                    except KeyError:
                        app.logger.warning("Code returned KeyError searching for burst information in the couchDB. Run Number: %d" % run)
                    i += 1
            else:
                if ( (int(start) >= startgtid) and (int(end) <= endgtid) ):
                    run = row.value[0]
                    run_id = row.id

                    try:
                        results[i] = dict(db.get(run_id).items())
                    except KeyError:
                        app.logger.warning("Code returned KeyError searching for burst information in the couchDB. Run Number: %d" % run)
                    i += 1
            total = len(results)

        return results, total, 0, 100
