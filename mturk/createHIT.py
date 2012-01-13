import datetime

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion

HOST = 'mechanicalturk.sandbox.amazonaws.com'

mtc = MTurkConnection(host=HOST)

#print mtc.get_account_balance()  # Tests the connection

# TODO: what did we tell the IRB? Payment, etc.

# Configure portal
experimentPortalURL = "http://0.0.0.0:5001/mturk"
frameheight = 600
mturkQuestion = ExternalQuestion( experimentPortalURL, 600 )

# Specify all the HTI parameters
paramdict = dict(
    hit_type = None,
    question = mturkQuestion,
    lifetime = datetime.timedelta(1),  # How long the HIT will be available
    max_assignments = 1, # Total times it will be assigned, not max per turker
    title = "Psychology Experiment: Category learning",
    description = "Learn to categorize a set of cards over a series of training trials.",
    keywords = "New York University, psychology experiment, category learning",
    reward = 1,
    duration = datetime.timedelta(1),
    approval_delay = None,
    annotation = None,  # Do we need this? Not clear on what it is.
    questions = None,
    qualifications = None
)

myhit = mtc.create_hit(**paramdict )[0]
hitid = myhit.HITId
