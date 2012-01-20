from flask import Flask, render_template, request, Response, jsonify
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
DATABASE = 'mysql://lab:2research@gureckislab.org:3306/active_learn_shj_turk'   # 'sqlite:///:memory:' - tests in memory
NUMCONDS = 12
NUMCOUNTERS = 24*16
ALLOCATED = 1
STARTED = 2
COMPLETED = 3
DEBRIEFED = 4
CREDITED = 5


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
        for field in ['participants_subjid', 'participants_ipaddress', 'participants_hitid', 'participants_assignmentid', 
                        'participants_condition', 'participants_counterbalance', 'participants_beginhit', 'participants_endhit',
                        'participants_status', 'participants_datafile']:
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
            hitID = request.args['hitId']
            assignmentID = request.args['assignmentId']
            print hitID, assignmentID
            s = select([participantsdb.c.status, participantsdb.c.subjid])
            s = s.where(and_(participantsdb.c.hitid==hitID, participantsdb.c.assignmentid==assignmentID))
            conn = engine.connect()
            status = -1;
            for row in conn.execute(s):
                status = row[0]
                subj_id = row[1]
            finished = status >= DEBRIEFED
            if status >= COMPLETED:
                if finished:
                    return render_template('thanks.html', hitid = hitID, assignmentId = assignmentID)
                else:
                    # They haven't answered the debriefing question.
                    return render_template('debriefing.html', hitid = hitID, subjid = subj_id)
            else:
                return render_template('mturkindex.html', hitid = hitID, assignmentid = assignmentID)
        else:
            return render_template('error.html')


def get_random_condition(conn):
    s = select([participantsdb.c.condition], participantsdb.c.endhit!=null, from_obj=[participantsdb])
    result = conn.execute(s)
    counts = [0]*NUMCONDS
    for row in result:
        counts[row[0]]+=1
    
    # choose randomly from the ones that have the least in them (so will tend to fill in evenly)
    indicies = [i for i, x in enumerate(counts) if x == min(counts)]
    rstate = getstate()
    seed()
    subj_cond = choice(indicies)
    setstate(rstate)
    return subj_cond


def get_random_counterbalance(conn):
    s = select([participantsdb.c.counterbalance], participantsdb.c.endhit!=null, from_obj=[participantsdb])
    result = conn.execute(s)
    counts = [0]*NUMCOUNTERS
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
        if request.args.has_key('hitId') and request.args.has_key('assignmentId'):
            hitID = request.args['hitId']
            assignmentID = request.args['assignmentId']
            print hitID, assignmentID
            
            return render_template('consent.html', hitid = hitID, assignmentid=assignmentID)
        else:
            return render_template('error.html')


@app.route('/exp', methods=['GET'])
def start_exp():
    # this serves up the experiment applet
    if request.method == 'GET':
        if request.args.has_key('hitId') and request.args.has_key('assignmentId'):
            hitID = request.args['hitId']
            assignmentID = request.args['assignmentId']
            print hitID, assignmentID
            
            conn = engine.connect()
            
            # check first to see if this hitID or assignmentID exists.  if so check to see if inExp is set
            s = select([participantsdb.c.subjid, participantsdb.c.condition, participantsdb.c.counterbalance, participantsdb.c.status], from_obj=[participantsdb])
            s = s.where(and_(participantsdb.c.hitid==hitID,participantsdb.c.assignmentid==assignmentID))
            result = conn.execute(s)
            matches = [row for row in result]
            numrecs = len(matches)
            if numrecs == 0:
                
                # doesn't exist, get a histogram of completed conditions and choose a under-used condition
                subj_cond = get_random_condition(conn)
                
                # doesn't exist, get a histogram of completed counterbalanced, and choose a under-used one
                subj_counter = get_random_counterbalance(conn)
                
                # set condition here and insert into database
                result = conn.execute(participantsdb.insert(),
                    hitid = hitID,
                    ipaddress = request.remote_addr,
                    assignmentid = assignmentID,
                    condition = subj_cond,
                    counterbalance = subj_counter,
                    status = ALLOCATED,
                    debriefed=False,
                    beginhit = datetime.datetime.now()
                )
                myid = result.inserted_primary_key[0]
            
            elif numrecs==1:
                myid, subj_cond, subj_counter, status = matches[0]
                if status>=STARTED: # in experiment (or later) can't restart at this point
                    return render_template('error.html')
            else:
                print "Error, hit/assignment appears in database more than once (serious problem)"
                exit()
            
            conn.close()
            dimo, dimv = counterbalanceconds[subj_counter]
            return render_template('exp.html', subj_num = myid, traintype = 0 if subj_cond<6 else 1, rule = subj_cond%6, dimorder = dimo, dimvals = dimv)
        else:
            return render_template('error.html')


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
        return render_template('error.html')


@app.route('/inexp', methods=['POST'])
def enterexp():
    print "accessing /inexp"
    if request.method == 'POST':
        if request.form.has_key('subjId'):
            subid = request.form['subjId']
            conn = engine.connect()
            results = conn.execute(participantsdb.update().where(participantsdb.c.subjid==subid).values(status=STARTED))
            conn.close()
    return render_template('error.html')


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
    return render_template('error.html')


@app.route('/complete', methods=['POST'])
def completed():
    print "ACCESSING the /complete route"
    if request.method == 'POST':
        print request.form.keys()
        if request.form.has_key('subjid') and request.form.has_key('agree'):
            subj_id = request.form['subjid']
            agreed = request.form['agree']  
            print subj_id, agreed
            conn = engine.connect()
            if agreed=="true":
                results = conn.execute(participantsdb.update().where(participantsdb.c.subjid==subj_id).values(debriefed=True))
            else:
                results = conn.execute(participantsdb.update().where(participantsdb.c.subjid==subj_id).values(debriefed=False))
            s = select([participantsdb.c.hitid, participantsdb.c.assignmentid])
            s = s.where(and_(participantsdb.c.subjid==subj_id))
            result = conn.execute(s)
            matches = [row for row in result]
            numrecs = len(matches)
            if numrecs == 1:
                hitid, assignid = matches[0]
                s = participantsdb.update()
                s = s.where(participantsdb.c.subjid==subj_id)
                s = s.values(status=DEBRIEFED)
                conn.execute(s)
            else:
                print "Error, more than one subject matches"
                return render_template('error.html')
            conn.close()
            return render_template('closepopup.html')
    return render_template('error.html')


#----------------------------------------------
# routes for displaying the database/editing it in html
#----------------------------------------------
@app.route('/list')
@requires_auth
def viewdata():
    s = select([participantsdb], use_labels=True)
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
# database management
#----------------------------------------------
def createdatabase(engine, metadata):

    # try to load tables from a file, if that fails create new tables
    try:
        participants = Table('participants', metadata, autoload=True)
    except: # can you put in the specific exception here?
        # ok will create the database
        print "ok will create the participant database"
        participants = Table('participants', metadata,
            Column('subjid', Integer, primary_key=True),
            Column('ipaddress', String(128)),
            Column('hitid', String(128)),
            Column('assignmentid', String(128)),
            Column('condition', Integer),
            Column('counterbalance', Integer),
            Column('beginhit', DateTime(), nullable=True),
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
        participants = Table('participants', metadata, autoload=True)
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

