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
# - 4.0: Ran classic nosofsky rep for type I, II, IV, and VI.

# <codecell>

# import necessary libraries
from sqlalchemy import *
from pandas import *
from string import replace

# reload the utilities (if they have changed)
%run -i ActiveLearning_SHJ_Utilities.py

# define various constants
DATABASE = 'mysql://released_data:shareit@gureckislab.org:3306/released_data'
TABLENAME = 'cmg_plot_2013_exp8_10'

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

from datetime import timedelta
# a function to gather up the learning curves for different subsets of subjects and averages them
def get_avg_learn_curve(people, version, training, rule):
    allTest = []
    count=0
    for key in people.keys():
        p = people[key]
        #print p.traintype, p.rule, p.physicalaids;#
        if p.codeversion==version and p.physicalaids=='no' and p.traintype==training and p.rule==rule and count_longest_run(p.dfTest['resp'])<16 and p.endhit - p.beginexp < timedelta(minutes=20):
            #print 
            allTest += [p.learnCurve]
            count += 1
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return DataFrame(allTest).mean()

# <codecell>

def count_longest_run(values):
    current_value = values[0]
    runs = []
    current_run = []
    current_run.append(values[0])
    for i in range(1,len(values)):
        if current_value == values[i]:
            current_run.append(values[i])
        else:
            current_value = values[i]
            runs.append(current_run)
            current_run = [current_value]
    lens = [len(i) for i in runs]
    return max(lens)

# <codecell>

VERSION='4.0'
fig=plt.figure(figsize=(15,6))

ax=fig.add_subplot(121)
t1p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 0),'yo-',antialiased=True,markersize=3,linewidth=1)
t2p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 1),'ro-',antialiased=True,markersize=3,linewidth=1)
t3p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 2),'bo-',antialiased=True,markersize=3,linewidth=1)
t4p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 3),'co-',antialiased=True,markersize=3,linewidth=1)
t5p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 4),'mo-',antialiased=True,markersize=3,linewidth=1)
t6p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 5),'go-',antialiased=True,markersize=3,linewidth=1)
ax.legend( (t1p[0], t2p[0], t3p[0], t4p[0], t5p[0], t6p[0]), ('I','II', 'III', 'IV', 'V', 'VI') )
plt.axis([-1,15,0,0.7])
plt.ylabel('probability of error')
plt.xlabel('training blocks')

#nosofsky comparison
ax=fig.add_subplot(122)
t1p=ax.plot([0.211, 0.025, .003, .000, .000, .000, .000, .000, .000, .000, .000, .000, .000, .000, .000],'yo-',antialiased=True,markersize=3,linewidth=1)
t2p=ax.plot([0.378, 0.156, .083, .056, .031, .027, .028, .016, .016, .008, .000, .002, .005, .003, .002],'ro-',antialiased=True,markersize=3,linewidth=1)
t3p=ax.plot([0.459, 0.286, .223, .145, .081, .078, .063, .033, .023, .016, .019, .009, .008, .013, .009],'bo-',antialiased=True,markersize=3,linewidth=1)
t4p=ax.plot([0.422, 0.295, .222, .172, .148, .109, .089, .063, .025, .031, .019, .025, .005, .000, .000],'co-',antialiased=True,markersize=3,linewidth=1)
t5p=ax.plot([0.472, 0.331, .230, .139, .106, .081, .067, .078, .048, .045, .050, .036, .031, .027, .016],'mo-',antialiased=True,markersize=3,linewidth=1)
t6p=ax.plot([0.498, 0.341, .284, .245, .217, .192, .192, .177, .172, .128, .139, .117, .103, .098, .106],'go-',antialiased=True,markersize=3,linewidth=1)
ax.legend( (t1p[0], t2p[0], t3p[0], t4p[0], t5p[0], t6p[0]), ('I','II', 'III', 'IV', 'V', 'VI') )
plt.axis([-1,15,0,0.7])
plt.ylabel('probability of error')
plt.xlabel('training blocks')

plt.show()

# <headingcell level=1>

# Measure Avg. Overall Accuracy

# <codecell>

# a function to gather up the block-to-criterion for different subsets of subjects and averages them
def get_overall_acc(people, version, training, rule):
    allTest = []
    count=0
    for key in people.keys():
        p = people[key]
        #print p.traintype, p.rule, p.physicalaids
        if p.codeversion==version and p.physicalaids=='no' and p.traintype==training and count_longest_run(p.dfTest['resp'])<16 and p.rule==rule and p.endhit - p.beginexp < timedelta(minutes=30):
            allTest += [1.0-p.meanOverallAcc]
            count += 1
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return mean(allTest), std(allTest)/sqrt(count)

# <codecell>

VERSION = '4.0'

# plot parameters
ind = arange(6)
width=0.35


fig = plt.figure()
ax = fig.add_subplot(111)


passiveMs, passiveSEs = array([get_overall_acc(participants, VERSION, 1, i) for i in range(6)]).T
passv = ax.bar(ind, passiveMs, width, color='c', yerr=passiveSEs)

#passiveMs = array([44.0, 85.4, 121.6, 127.0, 133.8, 189.2])/16.
#passv = ax.bar(ind+width, passiveMs, width, color='y')
ax.set_ylabel('Overall Accuracy')
ax.set_title('Overall Accuracy')
ax.set_xticks(ind+width)
ax.set_xticklabels(('I','II','III','IV','V','VI'))

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
        if p.codeversion==version and p.physicalaids=='no' and p.traintype==training and count_longest_run(p.dfTest['resp'])<16 and p.rule==rule and p.endhit - p.beginexp < timedelta(minutes=30):
            allTest += [p.nBlocksToCriterion]
            count += 1
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return mean(allTest), std(allTest)/sqrt(count)

# <codecell>

VERSION = '4.0'

# plot parameters
ind = arange(6)
width=0.35


fig = plt.figure()
ax = fig.add_subplot(111)


passiveMs, passiveSEs = array([get_avg_blocks_to_criterion(participants, VERSION, 1, i) for i in range(6)]).T
passv = ax.bar(ind, passiveMs, width, color='c', yerr=passiveSEs)

passiveMs = array([44.0, 85.4, 121.6, 127.0, 133.8, 189.2])/16.
passv = ax.bar(ind+width, passiveMs, width, color='y')
ax.set_ylabel('Blocks')
ax.set_title('Avg. Blocks to Criterion')
ax.set_xticks(ind+width)
ax.set_xticklabels(('I','II','III','IV','V','VI'))

plt.show()

# <codecell>

# a function to gather up the block-to-criterion for different subsets of subjects and averages them
def get_blocks_to_criterion_ind(people, version, training, rule):
    allTest = []
    count=0
    for key in people.keys():
        p = people[key]
        #print p.traintype, p.rule, p.physicalaids
        if p.codeversion==version and p.physicalaids=='no' and p.traintype==training and p.rule==rule:# and count_longest_run(p.dfTest['resp'].values)<16  and p.endhit - p.beginexp < timedelta(minutes=30):
            #print p.nBlocksToCriterion, p.medianRT
            allTest += [p.nBlocksToCriterion]
            count += 1
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return allTest

# <codecell>

print get_blocks_to_criterion_ind(participants, VERSION, 1, 0)
print get_blocks_to_criterion_ind(participants, VERSION, 1, 1)
print get_blocks_to_criterion_ind(participants, VERSION, 1, 2)
print get_blocks_to_criterion_ind(participants, VERSION, 1, 3)
print get_blocks_to_criterion_ind(participants, VERSION, 1, 4)
print get_blocks_to_criterion_ind(participants, VERSION, 1, 5)

# <codecell>

fig = plt.figure(figsize=(9,9))
ax = fig.add_subplot(231)
n, bins, patches = ax.hist(get_blocks_to_criterion_ind(participants, VERSION, 1, 0),15, normed=0, facecolor='orange',alpha=0.75)
ax = fig.add_subplot(232)
n, bins, patches = ax.hist(get_blocks_to_criterion_ind(participants, VERSION, 1, 1),15, normed=0, facecolor='orange',alpha=0.75)
ax = fig.add_subplot(233)
n, bins, patches = ax.hist(get_blocks_to_criterion_ind(participants, VERSION, 1, 2),15, normed=0, facecolor='orange',alpha=0.75)
ax = fig.add_subplot(234)
n, bins, patches = ax.hist(get_blocks_to_criterion_ind(participants, VERSION, 1, 3),15, normed=0, facecolor='orange',alpha=0.75)
ax = fig.add_subplot(235)
n, bins, patches = ax.hist(get_blocks_to_criterion_ind(participants, VERSION, 1, 4),15, normed=0, facecolor='orange',alpha=0.75)
ax = fig.add_subplot(236)
n, bins, patches = ax.hist(get_blocks_to_criterion_ind(participants, VERSION, 1, 5),15, normed=0, facecolor='orange',alpha=0.75)


plt.show()

# <headingcell level=1>

# Rated Difficulty/Engagement

# <codecell>

# a function to gather up the block-to-criterion for different subsets of subjects and averages them
def get_avg_difficulty(people, version, training, rule):
    allTest = []
    count=0
    for key in people.keys():
        p = people[key]
        #print p.traintype, p.rule, p.physicalaids
        if p.codeversion==version and p.physicalaids=='no' and p.traintype==training and count_longest_run(p.dfTest['resp'])<16 and p.rule==rule and p.endhit - p.beginexp < timedelta(minutes=30):
            allTest += [p.difficulty]
            count += 1
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return mean(allTest), std(allTest)/sqrt(count)


# a function to gather up the block-to-criterion for different subsets of subjects and averages them
def get_avg_engagement(people, version, training, rule):
    allTest = []
    count=0
    for key in people.keys():
        p = people[key]
        #print p.traintype, p.rule, p.physicalaids
        if p.codeversion==version and p.physicalaids=='no' and p.traintype==training and count_longest_run(p.dfTest['resp'])<16 and p.rule==rule and p.endhit - p.beginexp < timedelta(minutes=30):
            allTest += [p.engagement]
            count += 1
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return mean(allTest), std(allTest)/sqrt(count)

# <codecell>

VERSION = '4.0'

# plot parameters
ind = arange(6)
width=0.35


fig = plt.figure()
ax = fig.add_subplot(111)


diffMs, diffSEs = array([get_avg_difficulty(participants, VERSION, 1, i) for i in range(6)]).T
diffv = ax.bar(ind, diffMs, width, color='c', yerr=diffSEs)

engageMs, engageSEs = array([get_avg_engagement(participants, VERSION, 1, i) for i in range(6)]).T
engv = ax.bar(ind+width, engageMs, width, color='y', yerr=engageSEs)

ax.set_ylabel('Rating')
ax.set_title('Difficulty/Engagement')
ax.set_xticks(ind+width)
ax.set_xticklabels(('I','II','III','IV','V','VI'))

plt.show()

# <codecell>

people

# <codecell>


