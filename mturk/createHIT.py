import datetime

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import LocaleRequirement, PercentAssignmentsApprovedRequirement, Qualifications

HOST = 'mechanicalturk.amazonaws.com'


mtc = MTurkConnection(
    aws_access_key_id="EXAMPLE",
    aws_secret_access_key="EXAMPLE",
    host=HOST)

# Configure portal
experimentPortalURL = "http://smash.psych.nyu.edu:5001/mturk"
frameheight = 600
mturkQuestion = ExternalQuestion( experimentPortalURL, 600 )

# Qualification:
quals = Qualifications();
quals.add( PercentAssignmentsApprovedRequirement("GreaterThanOrEqualTo", "95") )
quals.add( LocaleRequirement("EqualTo", "US") )
#quals.add( NumberHitsApprovedRequirement("GreaterThanOrEqualTo", "100") )

# Specify all the HIT parameters
paramdict = dict(
    hit_type = None,
    question = mturkQuestion,
    lifetime = datetime.timedelta(1),  # How long the HIT will be available
    max_assignments = 32, # Total times it will be assigned, not max per turker
    title = "Paid volunteers needed for an online experiment in Psychology (bonus available)",
    description = "Learn to categorize a set of cards over a series of training trials.",
    keywords = "New York University, psychology experiment, category learning",
    reward = 1,
    duration = datetime.timedelta(hours=2),
    approval_delay = None,
    annotation = None,  # Do we need this? Not clear on what it is.
    questions = None,
    qualifications = quals
)

myhit = mtc.create_hit(**paramdict )[0]
hitid = myhit.HITId

print mtc.get_account_balance()  # Tests the connection
