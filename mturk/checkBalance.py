
from boto.mturk.connection import MTurkConnection

HOST = 'mechanicalturk.amazonaws.com'


mtc = MTurkConnection(
    aws_access_key_id="AKIAI5GNWGIA4KM76PRA",
    aws_secret_access_key="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",
    host=HOST)

print mtc.get_account_balance()  # Tests the connection
