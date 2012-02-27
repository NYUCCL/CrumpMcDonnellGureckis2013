
from boto.mturk.connection import MTurkConnection

HOST = 'mechanicalturk.amazonaws.com'


mtc = MTurkConnection(
    aws_access_key_id="EXAMPLE",
    aws_secret_access_key="EXAMPLE",
    host=HOST)

print mtc.get_account_balance()  # Tests the connection
