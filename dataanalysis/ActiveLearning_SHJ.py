# -*- coding: utf-8 -*-
# <nbformat>3</nbformat>

# <headingcell level=1>

# ...:::''' Active Learning of Logical Rules ''':::...

# <markdowncell>

# Project by John McDonnell, Devin Domingo, Todd Gureckis
# 
# Document history:<br>
# *Version 1.0 - Todd Gureckis*

# <headingcell level=1>

# Connect to database

# <markdowncell>

# A little about the data.  It is all stored in a MySQL database on gureckislab.org.  To access the data you connect using SQLAlchemy and download.  There have been multiple version/changed to the experiment code.  Each database record includes a field (codeversion) which helps to sort that out.  As a summary (this should be updated):
# 
# - 1.0: Array of 8 items on each learning block, 16 samples per training block, paid $1 for completion
# - 2.0: Ran passive, type VI as in version 1.0 but added new instruction urging people not to quit and offered $10 lottery for finishers
# - 3.0: Ran passive, type VI again but after clicking on item during sampling other items are hidden (shuffling occurs while hidden)
# - 3.1: Ran passive, type II, IV, VI as in 3.0 but with only 8 samples per training block

# <codecell>

# import necessary libraries
from sqlalchemy import *
from pandas import *
from string import replace

# reload the utilities (if they have changed)
%run -i ActiveLearning_SHJ_Utilities.py

# define various constants
DATABASE = 'mysql://lab:2research@gureckislab.org:3306/active_learn_shj_turk'
TABLENAME = 'participants_v2'

# <codecell>

# connect to database and load relevant information
db, conn = connect_to_database(DATABASE, TABLENAME)
s = db.select()
#s = s.where(and_(db.c.codeversion=="1.0", db.c.status>=3, db.c.debriefed==1, db.c.endhit!=None, db.c.workerid!="TODD1"))
s = s.where(and_(db.c.status>=3, db.c.debriefed==1, db.c.endhit!=None, db.c.workerid!="TODD1"))
records = get_people(conn, s)

# <codecell>

# load up all the participants into a dictionary indexed by subjid
participants = {}
for i in range(len(records)):
    p = Participant(records[i])
    participants[p.subjid] = p
nsubj = len(participants.keys())
print "Number of subjects is ", nsubj

# <headingcell level=1>

# Plot a learning curve for each condition

# <codecell>

# a function to gather up the learning curves for different subsets of subjects and averages them
def get_avg_learn_curve(people, version, training, rule):
    allTest = []
    count=0
    for key in people.keys():
        p = people[key]
        #print p.traintype, p.rule, p.physicalaids
        if p.codeversion==version and p.physicalaids=='no' and p.traintype==training and p.rule==rule:
            allTest += [p.learnCurve]
            count += 1
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return DataFrame(allTest).mean()

# <codecell>

VERSION='1.0'
fig=plt.figure(figsize=(15,6))
ax=fig.add_subplot(121)
t1a=ax.plot(get_avg_learn_curve(participants, VERSION, 0, 0),'yo-',antialiased=True,markersize=3,linewidth=1)
t2a=ax.plot(get_avg_learn_curve(participants, VERSION, 0, 1),'ro-',antialiased=True,markersize=3,linewidth=1)
t3a=ax.plot(get_avg_learn_curve(participants, VERSION, 0, 2),'bo-',antialiased=True,markersize=3,linewidth=1)
t4a=ax.plot(get_avg_learn_curve(participants, VERSION, 0, 3),'co-',antialiased=True,markersize=3,linewidth=1)
t5a=ax.plot(get_avg_learn_curve(participants, VERSION, 0, 4),'mo-',antialiased=True,markersize=3,linewidth=1)
t6a=ax.plot(get_avg_learn_curve(participants, VERSION, 0, 5),'go-',antialiased=True,markersize=3,linewidth=1)
ax.legend( (t1a[0], t2a[0], t3a[0], t4a[0], t5a[0], t6a[0]), ('I','II', 'III', 'IV', 'V', 'VI') )
plt.axis([-1,20,0,1.0])
plt.ylabel('probability of error')
plt.xlabel('training blocks')

ax=fig.add_subplot(122)
t1p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 0),'yo-',antialiased=True,markersize=3,linewidth=1)
t2p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 1),'ro-',antialiased=True,markersize=3,linewidth=1)
t3p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 2),'bo-',antialiased=True,markersize=3,linewidth=1)
t4p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 3),'co-',antialiased=True,markersize=3,linewidth=1)
t5p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 4),'mo-',antialiased=True,markersize=3,linewidth=1)
t6p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 5),'go-',antialiased=True,markersize=3,linewidth=1)
ax.legend( (t1p[0], t2p[0], t3p[0], t4p[0], t5p[0], t6p[0]), ('I','II', 'III', 'IV', 'V', 'VI') )
plt.axis([-1,20,0,1.0])
plt.ylabel('probability of error')
plt.xlabel('training blocks')

plt.show()

# <headingcell level=1>

# Measure Avg. Blocks to Criterion

# <codecell>

# a function to gather up the block-to-criterion for different subsets of subjects and averages them
def get_avg_blocks_to_criterion(people, version, training, rule):
    allTest = []
    count=0
    for key in people.keys():
        p = people[key]
        #print p.traintype, p.rule, p.physicalaids
        if p.codeversion==version and p.physicalaids=='no' and p.traintype==training and p.rule==rule:
            allTest += [p.nBlocksToCriterion]
            count += 1
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return mean(allTest), std(allTest)/sqrt(count)

# <codecell>

VERSION = '1.0'

# plot parameters
ind = arange(6)
width=0.35

activeMs, activeSEs = array([get_avg_blocks_to_criterion(participants, VERSION, 0, i) for i in range(6)]).T
fig = plt.figure()
ax = fig.add_subplot(111)
activ = ax.bar(ind, activeMs, width, color='y', yerr=activeSEs)


passiveMs, passiveSEs = array([get_avg_blocks_to_criterion(participants, VERSION, 1, i) for i in range(6)]).T
passv = ax.bar(ind+width, passiveMs, width, color='c', yerr=passiveSEs)

ax.set_ylabel('Blocks')
ax.set_title('Avg. Blocks to Criterion')
ax.set_xticks(ind+width)
ax.set_xticklabels(('I','II','III','IV','V','VI'))

ax.legend( (activ[0], passv[0]), ('Active','Passive') )
plt.show()

# <codecell>


