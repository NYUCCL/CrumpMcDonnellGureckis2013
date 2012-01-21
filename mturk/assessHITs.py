
from boto.mturk.connection import MTurkConnection


#print mtc.get_account_balance()  # Tests the connection

def get_all_reviewable_hits( mtc ):
    page_size = 50;
    hits = mtc.get_reviewable_hits( page_size=page_size )
    print "Total results to fetch %s" % hits.TotalNumResults
    print "Request hits page %i" % 1
    total_pages = float( hits.TotalNumResults )/page_size
    int_total = int(total_pages)
    if total_pages - int_total > 0:
        total_pages = int_total+1
    else:
        total_pages = int_total
    pn = 1
    while pn < total_pages:
        pn += 1
        print "Request hits page %i" % pn
        temp_hits = mtc.get_reviewable_hits( page_size = page_size, page_number=pn )
        hits.extend( temp_hits )
    return hits


mtc = MTurkConnection(
    aws_access_key_id="EXAMPLE",
    aws_secret_access_key="EXAMPLE",
    host='mechanicalturk.amazonaws.com')

hits = get_all_reviewable_hits( mtc )
print hits
