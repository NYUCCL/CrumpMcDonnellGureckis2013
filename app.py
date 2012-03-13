from flask import Flask, render_template, request, Response, jsonify, send_from_directory
from string import split
import os
import time
import datetime
import os.path
from random import choice, shuffle, seed, getstate, setstate
import sys
from sqlalchemy import *
from functools import wraps

# constants
DEPLOYMENT_ENV = 'sandbox'  # 'sandbox' or 'deploy' (the real thing)   # THIS ONE IS IMPORTANT TO SET
CODE_VERSION = '4.3'

DATABASE = 'mysql://lab:2research@gureckislab.org:3306/active_learn_shj_turk'   # 'sqlite:///:memory:' - tests in memory
TABLENAME = 'nosofskyrep'
NUMCONDS = 6
NUMCOUNTERS = 24*16
ALLOCATED = 1
STARTED = 2
COMPLETED = 3
DEBRIEFED = 4
CREDITED = 5
QUITEARLY = 6

MAXBLOCKS = 10



TESTINGPROBLEMSIX = False

# error codes
STATUS_INCORRECTLY_SET = 1000
HIT_ASSIGN_WORKER_ID_NOT_SET_IN_MTURK = 1001
HIT_ASSIGN_WORKER_ID_NOT_SET_IN_CONSENT = 1002
HIT_ASSIGN_WORKER_ID_NOT_SET_IN_EXP = 1003
HIT_ASSIGN_APPEARS_IN_DATABASE_MORE_THAN_ONCE = 1004
IN_EXP_ACCESSED_WITHOUT_POST = 1005
DEBRIEF_ACCESSED_WITHOUT_POST = 1006
COMPLETE_ACCESSED_WITHOUT_POST = 1007
ALREADY_STARTED_EXP = 1008
ALREADY_STARTED_EXP_MTURK = 1009
ALREADY_DID_EXP_HIT = 1010
TRIED_TO_QUIT= 1011
INTERMEDIATE_SAVE = 1012

IN_DEBUG = 2005

app = Flask(__name__)

#----------------------------------------------
# based counterbalancing code
#----------------------------------------------
seed(500)  # use the same order each time the program is launched
counterbalanceconds = []
dimorders = range(24)
dimvals = range(16)
shuffle(dimorders)
shuffle(dimvals)
for i in dimorders:
    for j in dimvals:
        counterbalanceconds.append((i,j))


#----------------------------------------------
# function for authentication
#----------------------------------------------
def wrapper(func, args):
    return func(*args)


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'gureckislab' and password == '2research'


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


#----------------------------------------------
# general utilities
#----------------------------------------------
def get_people(conn, s):
    people={}
    i=0
    for row in conn.execute(s):
        person = {}
        for field in ['subjid', 'ipaddress', 'hitid', 'assignmentid', 'workerid',
                        'cond', 'counterbalance', 'beginhit','beginexp', 'endhit',
                        'status', 'datafile']:
            if field=='datafile':
                if row[field] == None:
                    person[field] = "Nothing yet"
                else:
                    person[field] = row[field][:10]
            else:
                person[field] = row[field]
        people[i] = person
        i+=1
    return [people, i]

#----------------------------------------------
# routes
#----------------------------------------------
@app.route('/mturk', methods=['GET','POST'])
def mturkroute():
    if request.user_agent.browser == "msie":
        return render_template( 'ie.html' )
    # this just is a way-stop along the way to the experiment code
    if request.method == 'GET':
        if request.args.has_key('hitId') and request.args.has_key('assignmentId'):
            conn = engine.connect()
            hitID = request.args['hitId']
            assignmentID = request.args['assignmentId']
            if request.args.has_key('workerId'):
                workerID = request.args['workerId']
                # first check if this workerId has completed the task before (v1)
                s = select([participantsdb.c.subjid])
                s = s.where(and_(participantsdb.c.hitid!=hitID, participantsdb.c.workerid==workerID))
                result = conn.execute(s)
                matches = [row for row in result]
                numrecs = len(matches)
                
                if numrecs != 0:
                    return render_template('error.html', errornum=ALREADY_DID_EXP_HIT, hitid=request.args['hitId'], assignid=request.args['assignmentId'], workerid=request.args['workerId']) # already completed task
            else:
                workerID = '-1'
            print hitID, assignmentID, workerID
            s = select([participantsdb.c.status, participantsdb.c.subjid])
            s = s.where(and_(participantsdb.c.hitid==hitID, participantsdb.c.assignmentid==assignmentID, participantsdb.c.workerid==workerID))
            
            status = -1;
            for row in conn.execute(s):
                status = row[0]
                subj_id = row[1]
            if status == ALLOCATED or status==-1:
                return render_template('mturkindex.html', hitid = hitID, assignmentid = assignmentID, workerid = workerID)
            elif status == STARTED:
                return render_template('error.html', errornum=ALREADY_STARTED_EXP_MTURK, hitid=request.args['hitId'], assignid=request.args['assignmentId'], workerid=request.args['workerId']) # this means the screwed something up (closed window in middle of experiment)
            elif status == COMPLETED:
                return render_template('debriefing.html', subjid = subj_id) # if reloading but not debriefed
            elif status == DEBRIEFED:
                return render_template('thanks.html', target_env=DEPLOYMENT_ENV, hitid = hitID, assignmentid = assignmentID, workerid = workerID) # if debriefed successfully
            else:
                return render_template('error.html', errornum=STATUS_INCORRECTLY_SET, hitid=request.args['hitId'], assignid=request.args['assignmentId'], workerid=request.args['workerId'])  # hopefully never get here
        else:
            return render_template('error.html', errornum=HIT_ASSIGN_WORKER_ID_NOT_SET_IN_MTURK)


def get_random_condition(conn):
    # hits can be in one of three states:
        # jobs that are finished
        # jobs that are started but not finished
        # jobs that are never going to finish (user decided not to do it)
    # our count should be based on the first two so, lets stay anything finished or anything not finished that was started in the last 45 minutes should be counted
    starttime = datetime.datetime.now() + datetime.timedelta(minutes=-30)
    s = select([participantsdb.c.cond], and_(participantsdb.c.codeversion==CODE_VERSION, or_(participantsdb.c.endhit!=null, participantsdb.c.beginhit>starttime)), from_obj=[participantsdb])
    result = conn.execute(s)
    counts = [0]*NUMCONDS
    # Excluding less interesting conditions:
    
    counts[0] = 1000
    counts[2] = 1000
    counts[4] = 1000
    counts[5] = 1000
    for row in result:
        counts[row[0]]+=1
    
    # choose randomly from the ones that have the least in them (so will tend to fill in evenly)
    indicies = [i for i, x in enumerate(counts) if x == min(counts)]
    rstate = getstate()
    seed()
    if TESTINGPROBLEMSIX:
        #subj_cond = choice([5,11])
        subj_cond = 5
    else:
        subj_cond = choice(indicies)
    setstate(rstate)
    return subj_cond


def get_random_counterbalance(conn):
    starttime = datetime.datetime.now() + datetime.timedelta(minutes=-30)
    s = select([participantsdb.c.counterbalance], and_(participantsdb.c.codeversion==CODE_VERSION, or_(participantsdb.c.endhit!=null, participantsdb.c.beginhit>starttime)), from_obj=[participantsdb])    
    result = conn.execute(s)
    counts = [0]*NUMCOUNTERS
    assert len(counts) == NUMCOUNTERS, "WTF? len(counts)=%d while NUMCOUNTERS was %d." % (len(counts), NUMCOUNTERS)
    for row in result:
        counts[row[0]]+=1
    
    # choose randomly from the ones that have the least in them (so will tend to fill in evenly)
    indicies = [i for i, x in enumerate(counts) if x == min(counts)]
    rstate = getstate()
    seed()
    subj_counter = choice(indicies)
    setstate(rstate)
    return subj_counter


@app.route('/consent', methods=['GET'])
def give_consent():
    # this serves up the experiment applet
    if request.method == 'GET':
        if request.args.has_key('hitId') and request.args.has_key('assignmentId') and request.args.has_key('workerId'):
            hitID = request.args['hitId']
            assignmentID = request.args['assignmentId']
            workerID = request.args['workerId']
            print hitID, assignmentID, workerID
            return render_template('consent.html', hitid = hitID, assignmentid=assignmentID, workerid=workerID)
        else:
            return render_template('error.html', errornum=HIT_ASSIGN_WORKER_ID_NOT_SET_IN_CONSENT)


@app.route('/exp', methods=['GET'])
def start_exp():
    # this serves up the experiment applet
    if request.method == 'GET':
        if request.args.has_key('hitId') and request.args.has_key('assignmentId') and request.args.has_key('workerId'):
            hitID = request.args['hitId']
            assignmentID = request.args['assignmentId']
            workerID = request.args['workerId']
            print hitID, assignmentID, workerID
            
            conn = engine.connect()
            
            # check first to see if this hitID or assignmentID exists.  if so check to see if inExp is set
            s = select([participantsdb.c.subjid, participantsdb.c.cond, participantsdb.c.counterbalance, participantsdb.c.status], from_obj=[participantsdb])
            s = s.where(and_(participantsdb.c.hitid==hitID,participantsdb.c.assignmentid==assignmentID,participantsdb.c.workerid==workerID))
            result = conn.execute(s)
            matches = [row for row in result]
            numrecs = len(matches)
            if numrecs == 0:
                
                # doesn't exist, get a histogram of completed conditions and choose an under-used condition
                subj_cond = get_random_condition(conn)
                
                # doesn't exist, get a histogram of completed counterbalanced, and choose an under-used one
                subj_counter = get_random_counterbalance(conn)
                
                if request.remote_addr==None:
                    myip = "UKNOWNIP"
                else:
                    myip = request.remote_addr
                
                # set condition here and insert into database
                result = conn.execute(participantsdb.insert(),
                    hitid = hitID,
                    ipaddress = myip,
                    assignmentid = assignmentID,
                    workerid = workerID,
                    cond = subj_cond,
                    counterbalance = subj_counter,
                    status = ALLOCATED,
                    codeversion = CODE_VERSION,
                    debriefed=False,
                    beginhit = datetime.datetime.now()
                )
                myid = result.inserted_primary_key[0]
            
            elif numrecs==1:
                myid, subj_cond, subj_counter, status = matches[0]
                if status>=STARTED: # in experiment (or later) can't restart at this point
                    return render_template('error.html', errornum=ALREADY_STARTED_EXP, hitid=request.args['hitId'], assignid=request.args['assignmentId'], workerid=request.args['workerId'])
            else:
                print "Error, hit/assignment appears in database more than once (serious problem)"
                return render_template('error.html', errornum=HIT_ASSIGN_APPEARS_IN_DATABASE_MORE_THAN_ONCE, hitid=request.args['hitId'], assignid=request.args['assignmentId'], workerid=request.args['workerId'])
            
            conn.close()
            dimo, dimv = counterbalanceconds[subj_counter]
            return render_template('exp.html', subj_num = myid, traintype = 1, rule = subj_cond%6, dimorder = dimo, dimvals = dimv, maxblocks=MAXBLOCKS)
        else:
            return render_template('error.html', errornum=HIT_ASSIGN_WORKER_ID_NOT_SET_IN_EXP)


@app.route('/debug', methods=['GET','POST'])
def start_exp_debug():
    # this serves up the experiment applet in debug mode
    if request.method == 'GET':
        if "cond" in request.args.keys():
            subj_cond = int( request.args['cond'] );
        else:
            import random
            subj_cond = random.randrange(12);
        if "subjid" in request.args.keys():
            counterbalance = int( request.args['counterbalance'] );
        else:
            import random
            counterbalance = random.randrange(384);
        return render_template('exp.html', 
                               subj_num = -1, 
                               traintype = 0 if subj_cond<6 else 1, 
                               rule = subj_cond%6, 
                               dimorder = counterbalance%24, 
                               dimvals = counterbalance//24,
                               skipto = request.args['skipto'] if 'skipto' in request.args else ''
                              )
    else:
        return render_template('error.html', errornum=IN_DEBUG)


@app.route('/inexp', methods=['POST'])
def enterexp():
    print "accessing /inexp"
    if request.method == 'POST':
        if request.form.has_key('subjId'):
            subid = request.form['subjId']
            conn = engine.connect()
            results = conn.execute(participantsdb.update().where(participantsdb.c.subjid==subid).values(status=STARTED, beginexp = datetime.datetime.now()))
            conn.close()
    return render_template('error.html', errornum=IN_EXP_ACCESSED_WITHOUT_POST)


@app.route('/debrief', methods=['POST'])
def savedata():
    if request.method == 'POST':
        print request.form.keys()
        if request.form.has_key('subjid') and request.form.has_key('data'):
            conn = engine.connect()
            subj_id = int(request.form['subjid'])
            datafile = request.form['data']
            print subj_id, datafile
            s = participantsdb.update()
            s = s.where(participantsdb.c.subjid==subj_id)
            s = s.values(status=COMPLETED, datafile=datafile, endhit=datetime.datetime.now())
            conn.execute(s)
            return render_template('debriefing.html', subjid=subj_id)
    else:
        return render_template('error.html', errornum=DEBRIEF_ACCESSED_WITHOUT_POST)


@app.route('/inexpsave', methods=['POST'])
def inexpsave():
    print "accessing the /inexpsave route"
    if request.method == 'POST':
        print request.form.keys()
        if request.form.has_key('subjId') and request.form.has_key('dataString'):
            subj_id = request.form['subjId']
            datastring = request.form['dataString']  
            print "getting the save data", subj_id, datastring
            conn = engine.connect()
            conn.execute(participantsdb.update().where(participantsdb.c.subjid==subj_id).values(datafile=datastring, status=STARTED))
            conn.close()
    return render_template('error.html', errornum=INTERMEDIATE_SAVE)

@app.route('/quitter', methods=['POST'])
def quitter():
    print "accessing the /quitter route"
    if request.method == 'POST':
        print request.form.keys()
        if request.form.has_key('subjId') and request.form.has_key('dataString'):
            subj_id = request.form['subjId']
            datastring = request.form['dataString']  
            print "getting the save data", subj_id, datastring
            conn = engine.connect()
            conn.execute(participantsdb.update().where(participantsdb.c.subjid==subj_id).values(datafile=datastring, status=QUITEARLY))
            conn.close()
    return render_template('error.html', errornum=TRIED_TO_QUIT)


@app.route('/complete', methods=['POST'])
def completed():
    print "accessing the /complete route"
    if request.method == 'POST':
        print request.form.keys()
        if request.form.has_key('subjid') and request.form.has_key('agree'):
            subj_id = request.form['subjid']
            agreed = request.form['agree']  
            print subj_id, agreed
            conn = engine.connect()
            if agreed=="true":
                conn.execute(participantsdb.update().where(participantsdb.c.subjid==subj_id).values(debriefed=True, status=DEBRIEFED))
            else:
                conn.execute(participantsdb.update().where(participantsdb.c.subjid==subj_id).values(debriefed=False, status=DEBRIEFED))
            conn.close()
            return render_template('closepopup.html')
    return render_template('error.html', errornum=COMPLETE_ACCESSED_WITHOUT_POST)


#----------------------------------------------
# routes for displaying the database/editing it in html
#----------------------------------------------
@app.route('/list')
@requires_auth
def viewdata():
    s = select([participantsdb], use_labels=False)
    s = s.order_by(participantsdb.c.subjid.asc())
    conn = engine.connect()
    [people, i] = get_people(conn, s)
    conn.close()
    return render_template('simplelist.html', records=people, nrecords=i)


@app.route('/updatestatus', methods=['POST'])
@app.route('/updatestatus/', methods=['POST'])
def updatestatus():
    if request.method == 'POST':
        conn = engine.connect()
        field = request.form['id']
        value = request.form['value']
        print field, value
        [tmp, field, id] = split(field,'_')
        id = int(id)
        s = participantsdb.update()
        s = s.where(participantsdb.c.subjid==id)
        if field=='status':
            s = s.values(status=value)
        conn.execute(s)
        return value


#----------------------------------------------
# generic route
#----------------------------------------------
@app.route('/<pagename>')
#@requires_auth
def regularpage(pagename=None):
    if pagename==None:
        print "error"
    else:
        return render_template(pagename)


#----------------------------------------------
# favicon issue - http://flask.pocoo.org/docs/patterns/favicon/
#----------------------------------------------
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                'favicon.ico', mimetype='image/vnd.microsoft.icon')

#----------------------------------------------
# database management
#----------------------------------------------
def createdatabase(engine, metadata):

    # try to load tables from a file, if that fails create new tables
    try:
        participants = Table(TABLENAME, metadata, autoload=True)
    except: # can you put in the specific exception here?
        # ok will create the database
        print "ok will create the participant database"
        participants = Table(TABLENAME, metadata,
            Column('subjid', Integer, primary_key=True),
            Column('ipaddress', String(128)),
            Column('hitid', String(128)),
            Column('assignmentid', String(128)),
            Column('workerid', String(128)),
            Column('cond', Integer),
            Column('counterbalance', Integer),
            Column('codeversion',String(128)),
            Column('beginhit', DateTime(), nullable=True),
            Column('beginexp', DateTime(), nullable=True),
            Column('endhit', DateTime(), nullable=True),
            Column('status', Integer, default = ALLOCATED),
            Column('debriefed', Boolean),
            Column('datafile', Text, nullable=True),  #the data from the exp
        )
        participants.create()
    return participants


def loaddatabase(engine, metadata):
    # try to load tables from a file, if that fails create new tables
    try:
        participants = Table(TABLENAME, metadata, autoload=True)
    except: # can you put in the specific exception here?
        print "Error, participants table doesn't exist"
        exit()
    return participants


###########################################################
# let's start
###########################################################
if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "Useage: python webapp.py [initdb/server]"
    elif len(sys.argv)>1:
        engine = create_engine(DATABASE, echo=False) 
        metadata = MetaData()
        metadata.bind = engine
        if sys.argv[1]=='initdb':
            print "initializing database"
            createdatabase(engine, metadata)
            pass
        elif sys.argv[1]=='server':
            print "starting webserver"
            participantsdb = loaddatabase(engine, metadata)
            # by default just launch webserver
            app.run(debug=True, host='0.0.0.0', port=5001)

