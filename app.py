from flask import Flask, render_template, request, Response, jsonify
from string import split
import os
import time
import datetime
import os.path
from random import choice
import sys
from sqlalchemy import *
from functools import wraps

# constants
DATABASE = 'mysql://lab:2research@gureckislab.org:3306/active_learn_shj_turk'   # 'sqlite:///:memory:' - tests in memory
NUMCONDS = 12
STARTED = 1
COMPLETED = 2
CREDITED = 3
# open this up no matter if running in server or initdb mode

app = Flask(__name__)


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

def get_people(conn, s):
    people={}
    i=0
    for row in conn.execute(s):
        print row
        person = {}
        for field in ['participants_subjid', 'participants_hitid', 'participants_assignmentid', 
                        'participants_condition', 'participants_beginhit', 'participants_endhit',
                        'participants_status', 'participants_datafile']:
            person[field] = row[field]
        people[i] = person
        i+=1
    return [people, i]

@app.route('/mturk', methods=['GET','POST'])
def mturkroute():
    # this just is a way-stop along the way to the experiment code
    if request.method == 'GET':
        if request.args.has_key('hitId') and request.args.has_key('assignmentId'):
            hitID = request.args['hitId']
            assignmentID = request.args['assignmentId']
            print hitID, assignmentID
            return render_template('mturkindex.html', hitid = hitID, assignmentid = assignmentID)
        else:
            return render_template('error.html')

@app.route('/exp', methods=['GET','POST'])
def start_exp():
    # this serves up the experiment applet
    if request.method == 'GET':
        if request.args.has_key('hitId') and request.args.has_key('assignmentId'):
            hitID = request.args['hitId']
            assignmentID = request.args['assignmentId']
            print hitID, assignmentID
            conn = engine.connect()
            
            # get a histogram of completed conditions
            s = select([participantsdb.c.condition], participantsdb.c.endhit!=null, from_obj=[participantsdb])
            result = conn.execute(s)
            counts = [0]*NUMCONDS            
            for row in result:
                counts[row[0]]+=1
            
            # choose randomly from the ones that have the least in them (so will tend to fill in evenly)
            indicies = [i for i, x in enumerate(counts) if x == min(counts)]
            subj_cond = choice(indicies)
            
            # set condition here and insert into database
            result = conn.execute(participantsdb.insert(),
                hitid = hitID,
                assignmentid = assignmentID,
                condition = subj_cond,
                status = STARTED,
                beginhit = datetime.datetime.now()
            )
            myid = result.inserted_primary_key[0]
            
            conn.close()
            return render_template('exp.html', subj_num = myid, traintype = 0 if subj_cond<6 else 1, rule = subj_cond%6, dimorder = myid%24, dimvals = myid%16)
        else:
            return render_template('error.html')



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


@app.route('/save', methods=['POST'])
def savedata():
    pass
    # if request.method == 'POST':
    #     conn = engine.connect()
    #     field = request.form['id']
    #     value = request.form['value']
    #     print field, value
    #     [tmp, field, id] = split(field,'_')
    #     id = int(id)
    #     s = participantsdb.update()
    #     s = s.where(participantsdb.c.subjid==id)
    #     if field=='status':
    #         s = s.values(status=value)
    #     conn.execute(s)
    #     return value


@app.route('/<pagename>')
#@requires_auth
def regularpage(pagename=None):
    if pagename==None:
        print "error"
    else:
        return render_template(pagename)


def createdatabase(engine, metadata):

    # try to load tables from a file, if that fails create new tables
    try:
        participants = Table('participants', metadata, autoload=True)
    except: # can you put in the specific exception here?
        # ok will create the database
        print "ok will create the participant database"
        participants = Table('participants', metadata,
            Column('subjid', Integer, primary_key=True),
            Column('hitid', String(128)),
            Column('assignmentid', String(128)),
            Column('condition', Integer),
            Column('beginhit', DateTime(), nullable=True),
            Column('endhit', DateTime(), nullable=True),
            Column('status', Integer, default = 1),
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
            print "initializing database TBD"
            createdatabase(engine, metadata)
            pass
        elif sys.argv[1]=='server':
            print "starting webserver"
            participantsdb = loaddatabase(engine, metadata)
            # by default just launch webserver
            app.run(debug=True, host='0.0.0.0', port=5001)
