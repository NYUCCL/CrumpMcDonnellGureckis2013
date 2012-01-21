import datetime

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import LocaleRequirement, PercentAssignmentsApprovedRequirement, Qualifications

HOST = 'mechanicalturk.sandbox.amazonaws.com'



mtc = MTurkConnection(
    aws_access_key_id="EXAMPLE",
    aws_secret_access_key="EXAMPLE",
    host=HOST)

#print mtc.get_account_balance()  # Tests the connection

# TODO: what did we tell the IRB? Payment, etc.

# Configure portal
experimentPortalURL = "http://smash.psych.nyu.edu:5001/mturk"
frameheight = 600
mturkQuestion = ExternalQuestion( experimentPortalURL, 600 )

# Qualification:
quals = Qualifications()
quals.add( PercentAssignmentsApprovedRequirement('GreaterThanOrEqualTo', 95) )
quals.add( LocaleRequirement("Country", "US") )

# Specify all the HIT parameters
paramdict = dict(
    hit_type = None,
    question = mturkQuestion,
    lifetime = datetime.timedelta(1),  # How long the HIT will be available
    max_assignments = 1, # Total times it will be assigned, not max per turker
    title = "The Group Discovery Game (Psychology Experiment)",
    description = "Learn to group a set of objects",
    keywords = "psychology, learning, memory, cognition, experiment",
    reward = 1,
    duration = datetime.timedelta(1),
    approval_delay = None,
    annotation = None,  # Do we need this? Not clear on what it is.
    questions = None,
    qualifications = quals
)

myhit = mtc.create_hit(**paramdict )[0]
hitid = myhit.HITId
