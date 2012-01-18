import datetime

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import LocaleRequirement, PercentAssignmentsApprovedRequirement

HOST = 'mechanicalturk.sandbox.amazonaws.com'



mtc = MTurkConnection(
    aws_access_key_id="AKIAI5GNWGIA4KM76PRA",
    aws_secret_access_key="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",
    host=HOST)

#print mtc.get_account_balance()  # Tests the connection

# TODO: what did we tell the IRB? Payment, etc.

# Configure portal
experimentPortalURL = "http://smash.psych.nyu.edu:5001/mturk"
frameheight = 600
mturkQuestion = ExternalQuestion( experimentPortalURL, 600 )

# Qualification:
#qualifications = [
#    PercentAssignmentsApprovedRequirement(),
#    LocaleRequirement
#]

# Specify all the HIT parameters
paramdict = dict(
    hit_type = None,
    question = mturkQuestion,
    lifetime = datetime.timedelta(1),  # How long the HIT will be available
    max_assignments = 1, # Total times it will be assigned, not max per turker
    title = "Paid volunteers needed for an online experiment in Psychology",
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
