from flask import Flask, render_template, request, Response, jsonify
from string import split
import os
import time
import datetime
import os.path
import sys
from sqlalchemy import *
from functools import wraps


app = Flask(__name__)

@app.route('/')
#@requires_auth
def indexroute():
    return render_template('index.html')

@app.route('/submitdata', methods=['POST'])
def submitdata():
    print request.form
    return jsonify({
        "reply": "So long and thanks for all the fish!",
        "otherfield": "more info" } )


@app.route('/<pagename>.html')
#@requires_auth
def regularpage(pagename=None):
    if pagename==None:
        print "error"
    else:
        return render_template(pagename+'.html')


###########################################################
# let's start
###########################################################
if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "Useage: python webapp.py [initdb/server]"
    elif len(sys.argv)>1:
        if sys.argv[1]=='initdb':
            print "initializing database TBD"
            pass
        elif sys.argv[1]=='server':
            print "starting webserver"
            # by default just launch webserver
            app.run(debug=False, port=5001)
            
