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
from datetime import timedelta
import rpy2.robjects as R


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

# a function to gather up the learning curves for different subsets of subjects and averages them
def get_avg_learn_curve(people, version, training, rule):
    allTest = []
    count=0
    for key in people.keys():
        p = people[key]
        #print p.codeversion, p.traintype, p.rule, p.physicalaids
        if (p.codeversion=='5.3' or p.codeversion=='5.32') and p.physicalaids=='no' \
           and p.traintype==training and p.rule==rule: # and p.age<22:
            #print 
            allTest += [p.learnCurve[:10]]
            count += 1
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return DataFrame(allTest).mean()

# <codecell>


fig=plt.figure(figsize=(9,6))

ax=fig.add_subplot(121)
t1p=ax.plot([0.211, 0.025, .003, .000, .000, .000, .000, .000, .000, .000],'yo-',antialiased=True,markersize=3,linewidth=1)
t2p=ax.plot([0.378, 0.156, .083, .056, .031, .027, .028, .016, .016, .008],'ro-',antialiased=True,markersize=3,linewidth=1)
t4p=ax.plot([0.422, 0.295, .222, .172, .148, .109, .089, .063, .025, .031],'co-',antialiased=True,markersize=3,linewidth=1)
t6p=ax.plot([0.498, 0.341, .284, .245, .217, .192, .192, .177, .172, .128],'go-',antialiased=True,markersize=3,linewidth=1)
VERSION='5.32'
t1p2=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 0)[:10],'y--',antialiased=True,markersize=3,linewidth=1)
t2p2=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 1)[:10],'r--',antialiased=True,markersize=3,linewidth=1)
t4p2=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 3)[:10],'c--',antialiased=True,markersize=3,linewidth=1)
t6p2=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 5)[:10],'g--',antialiased=True,markersize=3,linewidth=1)
ax.legend( (t1p[0], t2p[0], t4p[0],t6p[0], t1p2[0], t2p2[0], t4p2[0], t6p2[0]), ('Nosof. I', 'Nosof. II','Nosof. IV', 'Nosof. VI', 'Intr. I (N=50)','Intr. II (N=50)', 'Instr. IV (N=50)', 'Instr. VI (N=50)') )
plt.axis([-1,10,0,0.7])
plt.ylabel('Probability of Error')
plt.xlabel('Training Blocks')

ax=fig.add_subplot(122)
t1p=ax.plot([0.211, 0.025, .003, .000, .000, .000, .000, .000, .000, .000],'yo-',antialiased=True,markersize=3,linewidth=1)
t2p=ax.plot([0.378, 0.156, .083, .056, .031, .027, .028, .016, .016, .008],'ro-',antialiased=True,markersize=3,linewidth=1)
t4p=ax.plot([0.422, 0.295, .222, .172, .148, .109, .089, .063, .025, .031],'co-',antialiased=True,markersize=3,linewidth=1)
t6p=ax.plot([0.498, 0.341, .284, .245, .217, .192, .192, .177, .172, .128],'go-',antialiased=True,markersize=3,linewidth=1)

t1p2=ax.plot([0.19, 0.045, .038, .02, .038, .000, .000, .000, .000, .000],'y--',antialiased=True,markersize=3,linewidth=1)
t2p2=ax.plot([0.36, 0.195, .155, .12, .13, .100, .07, .045, .065, .04],'r--',antialiased=True,markersize=3,linewidth=1)
t4p2=ax.plot([0.358, 0.21, .17, .13, .175, .12, .1, .09, .11, .08],'c--',antialiased=True,markersize=3,linewidth=1)
t6p2=ax.plot([0.46, 0.27, .24, .2, .23, .21, .17, .14, .172, .15],'g--',antialiased=True,markersize=3,linewidth=1)
ax.legend( (t1p[0], t2p[0], t4p[0],t6p[0], t1p2[0], t2p2[0], t4p2[0], t6p2[0]), ('Nosof. I', 'Nosof. II','Nosof. IV', 'Nosof. VI', 'Lewan. I','Lewan. II', 'Lewan. IV', 'Lewan. VI') )

plt.axis([-1,10,0,0.7])
plt.ylabel('Probability of Error')
plt.xlabel('Training Blocks')
plt.show()


fig=plt.figure(figsize=(9,13))

ax=fig.add_subplot(221)
t1p=ax.plot([0.211, 0.025, .003, .000, .000, .000, .000, .000, .000, .000],'yo-',antialiased=True,markersize=3,linewidth=1)
VERSION='5.3'
t1p2=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 0),'y--',antialiased=True,markersize=3,linewidth=1)
VERSION='4.0'
t1p1=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 0)[:10],'#333333',antialiased=True,markersize=3,linewidth=1)
ax.legend( (t1p[0], t1p1[0], t1p2[0]), ('Nosof. I', 'Exp. 1 - I (N=41)', 'Exp. 3 - I (N=50)') )
plt.axis([-1,10,0,0.7])
plt.title('Type I')
plt.ylabel('Probability of Error')
plt.xlabel('Training Blocks')


ax=fig.add_subplot(222)
t2p=ax.plot([0.378, 0.156, .083, .056, .031, .027, .028, .016, .016, .008],'ro-',antialiased=True,markersize=3,linewidth=1)
VERSION='5.3'
t2p2=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 1),'r--',antialiased=True,markersize=3,linewidth=1)
VERSION='4.0'
t2p1=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 1)[:10],'#333333',antialiased=True,markersize=3,linewidth=1)

ax.legend( (t2p[0], t2p1[0], t2p2[0]), ('Nosof. II', 'Exp. 1 - II (N=38)', 'Exp. 3 - II (N=50)') )
plt.axis([-1,10,0,0.7])
plt.title('Type II')
plt.ylabel('Probability of Error')
plt.xlabel('Training Blocks')


ax=fig.add_subplot(223)
t4p=ax.plot([0.422, 0.295, .222, .172, .148, .109, .089, .063, .025, .031],'co-',antialiased=True,markersize=3,linewidth=1)
VERSION='5.3'
t4p2=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 3),'c--',antialiased=True,markersize=3,linewidth=1)
VERSION='4.0'
t4p1=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 3)[:10],'#333333',antialiased=True,markersize=3,linewidth=1)
ax.legend( (t4p[0], t4p1[0], t4p2[0]), ('Nosof. IV', 'Exp. 1 - II (N=39)', 'Exp. 3 - II (N=50)') )
plt.axis([-1,10,0,0.7])
plt.title('Type IV')
plt.ylabel('Probability of Error')
plt.xlabel('Training Blocks')

ax=fig.add_subplot(224)
t6p=ax.plot([0.498, 0.341, .284, .245, .217, .192, .192, .177, .172, .128],'go-',antialiased=True,markersize=3,linewidth=1)
VERSION='5.3'
t6p2=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 5),'g--',antialiased=True,markersize=3,linewidth=1)
VERSION='4.0'
t6p1=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 5)[:10],'#333333',antialiased=True,markersize=3,linewidth=1)
ax.legend( (t6p[0], t6p1[0], t6p2[0]), ('Nosof. VI', 'Exp. 1 - II (N=38)', 'Exp. 3 - II (N=50)') )
plt.axis([-1,10,0,0.7])
plt.title('Type VI')
plt.ylabel('Probability of Error')
plt.xlabel('Training Blocks')





plt.show() 

# <codecell>

print "hi"

# <codecell>


fig=plt.figure(figsize=(22,6))


#nosofsky comparison
ax=fig.add_subplot(161)
t1p=ax.plot([0.211, 0.025, .003, .000, .000, .000, .000, .000, .000, .000, .000, .000, .000, .000, .000],'yo-',antialiased=True,markersize=3,linewidth=1)
t2p=ax.plot([0.378, 0.156, .083, .056, .031, .027, .028, .016, .016, .008, .000, .002, .005, .003, .002],'ro-',antialiased=True,markersize=3,linewidth=1)
t3p=ax.plot([0.459, 0.286, .223, .145, .081, .078, .063, .033, .023, .016, .019, .009, .008, .013, .009],'bo-',antialiased=True,markersize=3,linewidth=1)
t4p=ax.plot([0.422, 0.295, .222, .172, .148, .109, .089, .063, .025, .031, .019, .025, .005, .000, .000],'co-',antialiased=True,markersize=3,linewidth=1)
t5p=ax.plot([0.472, 0.331, .230, .139, .106, .081, .067, .078, .048, .045, .050, .036, .031, .027, .016],'mo-',antialiased=True,markersize=3,linewidth=1)
t6p=ax.plot([0.498, 0.341, .284, .245, .217, .192, .192, .177, .172, .128, .139, .117, .103, .098, .106],'go-',antialiased=True,markersize=3,linewidth=1)
ax.legend( (t1p[0], t2p[0], t3p[0], t4p[0], t5p[0], t6p[0]), ('I','II', 'III', 'IV', 'V', 'VI') )
ax.set_title('Nosofsky et al. (1994) (N=120)')
plt.axis([-1,15,0,0.7])
plt.ylabel('Probability of Error')
plt.xlabel('Training Blocks')

VERSION='4.0'
ax=fig.add_subplot(162)
t1p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 0),'yo-',antialiased=True,markersize=3,linewidth=1)
t2p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 1),'ro-',antialiased=True,markersize=3,linewidth=1)
t3p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 2),'bo-',antialiased=True,markersize=3,linewidth=1)
t4p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 3),'co-',antialiased=True,markersize=3,linewidth=1)
t5p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 4),'mo-',antialiased=True,markersize=3,linewidth=1)
t6p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 5),'go-',antialiased=True,markersize=3,linewidth=1)
ax.legend( (t1p[0], t2p[0], t3p[0], t4p[0], t5p[0], t6p[0]), ('I','II', 'III', 'IV', 'V', 'VI') )
ax.set_title('Mechanical Turk Data (N=224)')
plt.axis([-1,15,0,0.7])
plt.ylabel('Probability of Error')
plt.xlabel('Training Blocks')

VERSION='4.2'
ax=fig.add_subplot(163)
#t1p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 0),'yo-',antialiased=True,markersize=3,linewidth=1)
t2p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 1),'ro-',antialiased=True,markersize=3,linewidth=1)
#t3p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 2),'bo-',antialiased=True,markersize=3,linewidth=1)
t4p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 3),'co-',antialiased=True,markersize=3,linewidth=1)
#t5p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 4),'mo-',antialiased=True,markersize=3,linewidth=1)
#t6p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 5),'go-',antialiased=True,markersize=3,linewidth=1)
ax.legend( ( t2p[0],t4p[0]), ('II (N=21)',  'IV (N=20)') )
ax.set_title('MT - Low incentive (N=41)')
plt.axis([-1,10,0,0.7])
plt.ylabel('Probability of Error')
plt.xlabel('Training Blocks')


VERSION='4.3'
ax=fig.add_subplot(164)
#t1p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 0),'yo-',antialiased=True,markersize=3,linewidth=1)
t2p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 1),'ro-',antialiased=True,markersize=3,linewidth=1)
#t3p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 2),'bo-',antialiased=True,markersize=3,linewidth=1)
t4p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 3),'co-',antialiased=True,markersize=3,linewidth=1)
#t5p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 4),'mo-',antialiased=True,markersize=3,linewidth=1)
#t6p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 5),'go-',antialiased=True,markersize=3,linewidth=1)
ax.legend( ( t2p[0],t4p[0]), ('II (N=21)',  'IV (N=20)') )
ax.set_title('MT - High incentive (N=41)')
plt.axis([-1,10,0,0.7])
plt.ylabel('Probability of Error')
plt.xlabel('Training Blocks')


ax=fig.add_subplot(165)
VERSION='4.2'
t2p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 1),'ro-',antialiased=True,markersize=3,linewidth=1)
VERSION='4.0'
t3p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 1),'co-',antialiased=True,markersize=3,linewidth=1)
VERSION='4.3'
t4p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 1),'go-',antialiased=True,markersize=3,linewidth=1)
ax.legend( (t1p[0], t2p[0], t3p[0], t4p[0], t5p[0], t6p[0]), ('Low $ (N=21)','Medium $ (N=40)', 'High $ (N=21)') )
ax.set_title('Type II')
plt.axis([-1,16,0,0.7])
plt.ylabel('Probability of Error')
plt.xlabel('Training Blocks')

ax=fig.add_subplot(166)
VERSION='4.2'
t1p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 3),'ro-',antialiased=True,markersize=3,linewidth=1)
VERSION='4.0'
t2p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 3),'co-',antialiased=True,markersize=3,linewidth=1)
VERSION='4.3'
t3p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 3),'go-',antialiased=True,markersize=3,linewidth=1)
ax.legend( (t1p[0], t2p[0], t3p[0]), ('Low $ (N=20)','Medium $ (N=40)', 'High $ (N=20)') )
ax.set_title('Type IV')
plt.axis([-1,16,0,0.7])
plt.ylabel('Probability of Error')
plt.xlabel('Training Blocks')



plt.show()





fig=plt.figure(figsize=(8,6))

ax=fig.add_subplot(121)
VERSION='4.2'
t2p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 1),'ro-',antialiased=True,markersize=3,linewidth=1)
VERSION='4.0'
t3p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 1),'bo-',antialiased=True,markersize=3,linewidth=1)
VERSION='4.3'
t4p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 1),'co-',antialiased=True,markersize=3,linewidth=1)
VERSION='5.0'
t5p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 1),'go-',antialiased=True,markersize=3,linewidth=1)
VERSION='5.3'
t6p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 1),'yo-',antialiased=True,markersize=3,linewidth=1)
ax.legend( (t2p[0], t3p[0], t4p[0], t5p[0], t6p[0]), ('Low $ (N=21)','Medium $ (N=40)', 'High $ (N=21)', 'New Stims, Med $ (N=18)', 'Instr') )
ax.set_title('Type II')
plt.axis([-1,16,0,0.7])
plt.ylabel('Probability of Error')
plt.xlabel('Training Blocks')

ax=fig.add_subplot(122)
VERSION='4.2'
t1p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 3),'ro-',antialiased=True,markersize=3,linewidth=1)
VERSION='4.0'
t2p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 3),'bo-',antialiased=True,markersize=3,linewidth=1)
VERSION='4.3'
t3p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 3),'co-',antialiased=True,markersize=3,linewidth=1)
VERSION='5.3'
t6p=ax.plot(get_avg_learn_curve(participants, VERSION, 1, 3),'yo-',antialiased=True,markersize=3,linewidth=1)
ax.legend( (t1p[0], t2p[0], t3p[0], t6p[0]), ('Low $ (N=20)','Medium $ (N=40)', 'High $ (N=20)', 'Instr') )
ax.set_title('Type IV')
plt.axis([-1,16,0,0.7])
plt.ylabel('Probability of Error')
plt.xlabel('Training Blocks')
plt.show()

# <headingcell level=1>

# Measure Avg. Overall Accuracy

# <codecell>

def get_overall_acc(people, version, training, rule, hitid=None):
    allTest = get_overall_acc_raw(people, version, training, rule, hitid)
    return mean(allTest), std(allTest)/sqrt(len(allTest))

# a function to gather up the block-to-criterion for different subsets of subjects and averages them
def get_overall_acc_raw(people, version, training, rule, hitid=None):
    allTest = []
    count=0
    nblocks = 10
    for key in people.keys():
        p = people[key]
        #print p.traintype, p.rule, p.physicalaids
        if hitid!=None:
            if p.codeversion==version and p.hitid==hitid and p.physicalaids=='no' and p.traintype==training and p.rule==rule:
                overallacc = (sum(p.dfTest['hit'][:nblocks*16]) + (nblocks*16 - len(p.dfTest[:nblocks*16]))) / (nblocks*16.)
                allTest += [overallacc]
                count += 1
        else:
            if p.codeversion==version and p.physicalaids=='no' and p.traintype==training and p.rule==rule:
                overallacc = (sum(p.dfTest['hit'][:nblocks*16]) + (nblocks*16 - len(p.dfTest[:nblocks*16]))) / (nblocks*16.)
                allTest += [overallacc]
                count += 1
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return allTest

# <codecell>

# plot parameters
ind = arange(6)
width=0.2


fig = plt.figure()
ax = fig.add_subplot(111)


VERSION = '4.2'
passiveMs, passiveSEs = array([get_overall_acc(participants, VERSION, 1, i) for i in range(6)]).T
passv = ax.bar(ind, passiveMs, width, color='#90B4CC', yerr=passiveSEs)


VERSION = '4.0'
passiveMs, passiveSEs = array([get_overall_acc(participants, VERSION, 1, i) for i in range(6)]).T
passv = ax.bar(ind+width, passiveMs, width, color='#005490', yerr=passiveSEs)


VERSION = '4.3'
passiveMs, passiveSEs = array([get_overall_acc(participants, VERSION, 1, i) for i in range(6)]).T
passv = ax.bar(ind+width*2, passiveMs, width, color='#6C6C6C', yerr=passiveSEs)

VERSION = '5.3'
passiveMs, passiveSEs = array([get_overall_acc(participants, VERSION, 1, i) for i in range(6)]).T
passv = ax.bar(ind+width*3, passiveMs, width, color='#6C6C6C', yerr=passiveSEs)

passiveMs = array([0.86,  .67, 0.0, .65, 0.0, .59 ])
errs = array([0.021, 0.021, 0.0, 0.013, 0.0, 0.015 ])
passv = ax.bar(ind+width*4, passiveMs, width, color='#F5B81D', yerr=errs)


#passiveMs = array([44.0, 85.4, 121.6, 127.0, 133.8, 189.2])/16.
#passv = ax.bar(ind+width, passiveMs, width, color='y')
ax.set_ylabel('Overall Accuracy')
ax.set_title('Overall Accuracy')
ax.set_xticks(ind+width*2)
ax.set_xticklabels(('I','II','III','IV','V','VI'))
ax.legend( ('\"Low\" (\$1 + \$10 lottery)','\"Medium\" ($0.75)', '\"High\" ($2 + perf. bonus)','Love (2002)') , 'upper center')
plt.axis([-0.25,6,0,1.4])

plt.show()

print passiveSEs
print errs

# <codecell>

# plot parameters
ind = arange(2)
width=0.2


fig = plt.figure()
ax = fig.add_subplot(111)


VERSION = '4.2'
passiveMs, passiveSEs = array([get_overall_acc(participants, VERSION, 1, i) for i in [1,3]]).T
passv = ax.bar(ind+width, passiveMs, width, color='#90B4CC', yerr=passiveSEs)


VERSION = '4.0'
passiveMs, passiveSEs = array([get_overall_acc(participants, VERSION, 1, i) for i in [1,3]]).T
passv = ax.bar(ind, passiveMs, width, color='#005490', yerr=passiveSEs)


VERSION = '4.3'
passiveMs, passiveSEs = array([get_overall_acc(participants, VERSION, 1, i) for i in [1,3]]).T
passv = ax.bar(ind+width*2, passiveMs, width, color='#6C6C6C', yerr=passiveSEs)

passiveMs = array([.67, .65, ])
errs = array([0.021, 0.013, ])
passv = ax.bar(ind+width*3, passiveMs, width, color='#F5B81D', yerr=errs)


#passiveMs = array([44.0, 85.4, 121.6, 127.0, 133.8, 189.2])/16.
#passv = ax.bar(ind+width, passiveMs, width, color='y')
ax.set_ylabel('Overall Accuracy')
ax.set_title('Overall Accuracy')
ax.set_xticks(ind+width*2)
ax.set_xticklabels(('II','IV'))
ax.legend( ('\"Low\" (\$1 + \$10 lottery)','\"Medium\" ($0.75)', '\"High\" ($2 + perf. bonus)','Love (2002)') , 'upper center')
plt.axis([-0.25,2,0,1.3])

plt.show()

print passiveSEs
print errs

# <codecell>

# build up anova - like table
typeII, typeIV = array([get_overall_acc_raw(participants, VERSION, 1, i) for i in [1,3]])

anovatable = []
for vers in ['4.0', '4.2', '4.3']:
    for shjtype in [1, 3]:
        tmpd = get_overall_acc_raw(participants, vers, 1, shjtype)
        for score in tmpd:
            anovatable.append([vers, shjtype, score])

print anovatable

# <codecell>

VERSION = '4.0'
typeII, typeIV = array([get_overall_acc_raw(participants, VERSION, 1, i) for i in [1,3]])
print meandifferencetest(pair=False, alt='two.sided', groupa=typeII, groupb=typeIV)[0]
print meandifferencetest(pair=False, alt='two.sided', groupa=typeII, nullh=0.67)[0]
print meandifferencetest(pair=False, alt='two.sided', groupa=typeIV, nullh=0.65)[0]

VERSION = '4.2'
typeII, typeIV = array([get_overall_acc_raw(participants, VERSION, 1, i) for i in [1,3]])
print meandifferencetest(pair=False, alt='two.sided', groupa=typeII, groupb=typeIV)[0]
print meandifferencetest(pair=False, alt='two.sided', groupa=typeII, nullh=0.67)[0]
print meandifferencetest(pair=False, alt='two.sided', groupa=typeIV, nullh=0.65)[0]

VERSION = '4.3'
typeII, typeIV = array([get_overall_acc_raw(participants, VERSION, 1, i) for i in [1,3]])
print meandifferencetest(pair=False, alt='two.sided', groupa=typeII, groupb=typeIV)[0]
print meandifferencetest(pair=False, alt='two.sided', groupa=typeII, nullh=0.67)[0]
print meandifferencetest(pair=False, alt='two.sided', groupa=typeIV, nullh=0.65)[0]

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
        if p.codeversion==version and p.physicalaids=='no' and p.traintype==training and p.rule==rule \
            and count_longest_run(p.dfTest['resp'])<16 \
            and p.endhit - p.beginexp < timedelta(minutes=30) and median(p.dfTest['rt'])<2000:
            allTest += [p.nBlocksToCriterion]
            count += 1
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return mean(allTest), std(allTest)/sqrt(count)

# <codecell>

VERSION = '5.3'

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
ax.legend( ('Mechanical Turk','Nosofsky et al. (1994)') , 'lower right')
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

VERSION='5.3'
print get_blocks_to_criterion_ind(participants, VERSION, 1, 1)
print mean(get_blocks_to_criterion_ind(participants, VERSION, 1, 1))

# <codecell>

VERSION='4.0'
fig = plt.figure(figsize=(12,9))
ax = fig.add_subplot(231)
n, bins, patches = ax.hist(get_blocks_to_criterion_ind(participants, VERSION, 1, 0),15, normed=0, facecolor='orange',alpha=0.75)
ax.set_title('Problem I')
ax.set_ylabel('Frequency')
ax.set_ylabel('Blocks to Criterion')
plt.axis([1,15.5,0,25])
ax = fig.add_subplot(232)
n, bins, patches = ax.hist(get_blocks_to_criterion_ind(participants, VERSION, 1, 1),15, normed=0, facecolor='orange',alpha=0.75)
ax.set_title('Problem II')
ax.set_ylabel('Frequency')
ax.set_ylabel('Blocks to Criterion')
plt.axis([1,15.5,0,25])
ax = fig.add_subplot(233)
n, bins, patches = ax.hist(get_blocks_to_criterion_ind(participants, VERSION, 1, 2),15, normed=0, facecolor='orange',alpha=0.75)
ax.set_title('Problem III')
ax.set_ylabel('Frequency')
ax.set_ylabel('Blocks to Criterion')
plt.axis([1,15.5,0,25])
ax = fig.add_subplot(234)
n, bins, patches = ax.hist(get_blocks_to_criterion_ind(participants, VERSION, 1, 3),15, normed=0, facecolor='orange',alpha=0.75)
ax.set_title('Problem IV')
ax.set_ylabel('Frequency')
ax.set_ylabel('Blocks to Criterion')
plt.axis([1,15.5,0,25])
ax = fig.add_subplot(235)
n, bins, patches = ax.hist(get_blocks_to_criterion_ind(participants, VERSION, 1, 4),15, normed=0, facecolor='orange',alpha=0.75)
ax.set_title('Problem V')
ax.set_ylabel('Frequency')
ax.set_ylabel('Blocks to Criterion')
plt.axis([1,15.5,0,25])
ax = fig.add_subplot(236)
n, bins, patches = ax.hist(get_blocks_to_criterion_ind(participants, VERSION, 1, 5),15, normed=0, facecolor='orange',alpha=0.75)
ax.set_title('Problem VI')
ax.set_ylabel('Frequency')
ax.set_ylabel('Blocks to Criterion')
plt.axis([1,15.5,0,25])
plt.show()

# <headingcell level=1>

# Proportion reaching criterion (comparison of incentives)

# <codecell>

# a function to gather up the block-to-criterion for different subsets of subjects and averages them
def get_proportion_reaching_criterion(people, version, training, rule, totalblocks, hitid=None):
    allTest = []
    count=0
    for key in people.keys():
        p = people[key]
        #print p.traintype, p.rule, p.physicalaids
        if hitid!=None:
            if p.codeversion==version and p.physicalaids=='no' and p.traintype==training and p.rule==rule and p.hitid==hitid:
                if p.nBlocksToCriterion < totalblocks:
                    allTest += [1]
                else:
                    # check if got criterion on last block
                    checkdata = p.dfTest['hit'][:32*totalblocks]
                    if sum(checkdata[-32:])==32:
                        allTest += [1]
                    else:
                        allTest += [0]
                count += 1
        else:
            if p.codeversion==version and p.physicalaids=='no' and p.traintype==training and p.rule==rule:
                if p.nBlocksToCriterion < totalblocks:
                    allTest += [1]
                else:
                    # check if got criterion on last block
                    checkdata = p.dfTest['hit'][:32*totalblocks]
                    if sum(checkdata[-32:])==32:
                        allTest += [1]
                    else:
                        allTest += [0]
                count += 1
            
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return mean(allTest)

# <codecell>

VERSION = "5.3"
print get_proportion_reaching_criterion(participants, VERSION, 1, 0, 10)
print get_proportion_reaching_criterion(participants, VERSION, 1, 1, 10)
print get_proportion_reaching_criterion(participants, VERSION, 1, 3, 10)
print get_proportion_reaching_criterion(participants, VERSION, 1, 5, 10)

# <codecell>

# plot parameters
ind = arange(6)
width=0.25

fig = plt.figure()
ax = fig.add_subplot(111)


VERSION = '4.2'
passiveMs = array([get_proportion_reaching_criterion(participants, VERSION, 1, i, 10) for i in range(6)]).T
passv = ax.bar(ind+width, passiveMs, width, color='#90B4CC')

VERSION = '4.0'
passiveMs = array([get_proportion_reaching_criterion(participants, VERSION, 1, i, 10) for i in range(6)]).T
passv = ax.bar(ind, passiveMs, width, color='#005490')

VERSION = '4.3'
passiveMs = array([get_proportion_reaching_criterion(participants, VERSION, 1, i, 10) for i in range(6)]).T
passv = ax.bar(ind+width*2, passiveMs, width, color='#6C6C6C')

ax.set_ylabel('Proportion Reaching Criterion')
ax.set_title('Proportion Reaching Criterion in 10 Blocks')
ax.set_xticks(ind+width*1.5)
ax.set_xticklabels(('I','II','III','IV','V','VI'))

ax.legend( ('\"Medium\" Incentive (\$1 + \$10 lottery)','\"Low\" Incentive ($0.75)', '\"High\" Incentive ($2 + performance bonus)') , 'upper center')
plt.axis([-0.5,6,0,1.5])

plt.show()

# <headingcell level=1>

# Proportion reaching criterion

# <codecell>

# a function to gather up the block-to-criterion for different subsets of subjects and averages them
def get_proportion_reaching_criterion(people, version, training, rule):
    allTest = []
    count=0
    for key in people.keys():
        p = people[key]
        #print p.traintype, p.rule, p.physicalaids
        if p.codeversion==version and p.physicalaids=='no' and p.traintype==training and p.rule==rule \
            and count_longest_run(p.dfTest['resp'])<16 \
            and p.endhit - p.beginexp < timedelta(minutes=30) and median(p.dfTest['rt'])<2000:
            if p.nBlocksToCriterion < 15:
                allTest += [1]
            else:
                # check if got criterion on last block
                if sum(p.dfTest['hit'][-32:])==32:
                    allTest += [1]
                else:
                    allTest += [0]
            count += 1
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return mean(allTest)

# <codecell>

print get_proportion_reaching_criterion(participants, '4.0',1,0)
print get_proportion_reaching_criterion(participants, '4.0',1,1)
print get_proportion_reaching_criterion(participants, '4.0',1,2)
print get_proportion_reaching_criterion(participants, '4.0',1,3)
print get_proportion_reaching_criterion(participants, '4.0',1,4)
print get_proportion_reaching_criterion(participants, '4.0',1,5)


VERSION = '4.0'

# plot parameters
ind = arange(6)
width=0.35


fig = plt.figure()
ax = fig.add_subplot(111)


passiveMs = array([get_proportion_reaching_criterion(participants, VERSION, 1, i) for i in range(6)]).T
passv = ax.bar(ind, passiveMs, width, color='c')

ax.set_ylabel('Proportion Reaching Criterion')
ax.set_title('Proportion Reaching Criterion')
ax.set_xticks(ind+width/2)
ax.set_xticklabels(('I','II','III','IV','V','VI'))
plt.axis([-0.5,6,0,1])
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
        if p.codeversion==version and p.physicalaids=='no' and p.traintype==training and p.rule==rule and p.endhit - p.beginexp < timedelta(minutes=30):
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
        if p.codeversion==version and p.physicalaids=='no' and p.traintype==training and p.rule==rule and p.endhit - p.beginexp < timedelta(minutes=30):
            allTest += [p.engagement]
            count += 1
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return mean(allTest), std(allTest)/sqrt(count)

# <codecell>

VERSION = '4.0'

# plot parameters
ind = arange(6)
width=0.35


fig = plt.figure(figsize=(8,6))
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

# <headingcell level=1>

# Demographics

# <codecell>

# a function to gather up the block-to-criterion for different subsets of subjects and averages them
def get_age(people, version, training, rule):
    allTest = []
    count=0
    for key in people.keys():
        p = people[key]
        #print p.traintype, p.rule, p.physicalaids
        if p.codeversion==version and p.physicalaids=='no' and p.traintype==training and p.rule==rule:
            allTest += [p.age]
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return allTest

MALE = 0
FEMALE = 1
NORESPONSE = -1
SOMEHIGHSCHOOL = 0
HIGHSCHOOL = 1
SOMECOLLEGE = 2
BA = 3
SOMEGRAD = 4
MA = 5
PHD = 6

# a function to gather up the block-to-criterion for different subsets of subjects and averages them
def get_gender(people, version, training, rule):
    allTest = []
    count=0
    for key in people.keys():
        p = people[key]
        #print p.traintype, p.rule, p.physicalaids
        if p.codeversion==version and p.physicalaids=='no' and p.traintype==training and p.rule==rule:
            if p.gender == 'male':
                val = MALE
            elif p.gender == 'female':
                val = FEMALE
            else:
                val = NORESPONSE
            allTest += [val]
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return allTest

# a function to gather up the block-to-criterion for different subsets of subjects and averages them
def get_education(people, version, training, rule):
    allTest = []
    count=0
    for key in people.keys():
        p = people[key]
        #print p.traintype, p.rule, p.physicalaids
        if p.codeversion==version and p.physicalaids=='no' and p.traintype==training and p.rule==rule:
            if p.education == "somehs":
                val = SOMEHIGHSCHOOL
            elif p.education == "highschool":
                val = HIGHSCHOOL
            elif p.education == "somecollege":
                val = SOMECOLLEGE
            elif p.education == "bachelors":
                val = BA
            elif p.education == "somegrad":
                val = SOMEGRAD
            elif p.education == "masters":
                val = MA
            elif p.education == "doctor":
                val = PHD
            else:
                val = NORESPONSE
            allTest += [val]
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return allTest


# a function to gather up the learning curves for different subsets of subjects and averages them
def get_avg_learn_curve_by_education(people, version, edu, training, rule):
    allTest = []
    count=0
    for key in people.keys():
        p = people[key]
        #print p.codeversion, p.traintype, p.rule, p.physicalaids
        if p.codeversion==version and p.physicalaids=='no' \
           and p.traintype==training and p.rule==rule and p.education==edu:
            #print 
            allTest += [p.learnCurve]
            count += 1
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return DataFrame(allTest).mean()


def get_avg_learn_curve_by_age(people, version, minage, maxage, training, rule):
    allTest = []
    count=0
    for key in people.keys():
        p = people[key]
        #print p.codeversion, p.traintype, p.rule, p.physicalaids
        if p.codeversion==version and p.physicalaids=='no' \
           and p.traintype==training and p.rule==rule and (p.age>=minage and p.age<maxage):
            #print 
            allTest += [p.learnCurve]
            count += 1
    print "Condition ", training, ":", rule, " has ", count, " participants."
    return DataFrame(allTest).mean()

# <codecell>

fig = plt.figure(figsize=(6,6))
ax = fig.add_subplot(111)
VERSION='5.3'
VERSION2='5.32'
TYPE = 5
a,b= [get_overall_acc_raw(participants, VERSION, 1, TYPE)+get_overall_acc_raw(participants, VERSION2, 1, TYPE), get_age(participants, VERSION, 1, TYPE)+get_age(participants, VERSION2, 1, TYPE)]

#ax.scatter(b,a,s=20);
m,c = polyfit(b,a, 1) 
print m,c
ax.plot(b, a, 'yo',b,m*array(b)+c,'--k')

plt.show()

# <codecell>

genders=get_gender(participants, "5.3", 1, 0)+get_gender(participants, "5.3", 1, 1)+get_gender(participants, "5.3", 1, 3)+get_gender(participants, "5.3", 1, 5)
print "percent female = ", sum(genders)/float(len(genders))

# plot parameters
ind = arange(2)
width=0.35


fig = plt.figure()
ax = fig.add_subplot(111)


genderCs = [sum(genders)/float(len(genders)), (len(genders)-sum(genders))/float(len(genders))]
passv = ax.bar(ind, genderCs, width, color='c')

ax.set_ylabel('Proportion each gender')
ax.set_title('Gender Breakdown')
ax.set_xticks(ind+width/2)
ax.set_xticklabels(('Female','Male'))
plt.axis([-0.25,1.5,0,1])
plt.show()

# <codecell>

education=get_education(participants, "5.3", 1, 0)+get_education(participants, "5.3", 1, 1)+get_education(participants, "5.3", 1, 3)+get_education(participants, "5.3", 1, 5)+get_education(participants, "5.32", 1, 0)+get_education(participants, "5.32", 1, 1)+get_education(participants, "5.32", 1, 3)+get_education(participants, "5.32", 1, 5)
education


# plot parameters
ind = arange(8)
width=0.35


fig = plt.figure()
ax = fig.add_subplot(111)


educationCs=[len(filter(lambda x: x==NORESPONSE, education)),
len(filter(lambda x: x==SOMEHIGHSCHOOL, education)),
len(filter(lambda x: x==HIGHSCHOOL, education)),
len(filter(lambda x: x==SOMECOLLEGE, education)),
len(filter(lambda x: x==BA, education)),
len(filter(lambda x: x==SOMEGRAD, education)),
len(filter(lambda x: x==MA, education)),
len(filter(lambda x: x==PHD, education))]
passv = ax.bar(ind, array(educationCs)/float(len(education)), width, color='c')

ax.set_ylabel('Proportion each group')
ax.set_title('Education Breakdown')
ax.set_xticks(ind+width/2)
ax.set_xticklabels(('No Response','Some H.S.', 'H.S.', 'Some college', 'BA/BS', 'Some grad', 'MA', 'PHD'), rotation='vertical')
#labels = pylab.getp(pylab.gca(),'xticklabels')
plt.axis([-0.25,8.5,0,0.5])
plt.show()

# <codecell>

fig = plt.figure(figsize=(8,6))
ax=fig.add_subplot(111)
VERSION='5.3'
TYPE = 3
t1p2=ax.plot(get_avg_learn_curve_by_education(participants, VERSION, "somehs", 1, TYPE),'r--',antialiased=True,markersize=3,linewidth=1)
t2p2=ax.plot(get_avg_learn_curve_by_education(participants, VERSION, "highschool", 1, TYPE),'g--',antialiased=True,markersize=3,linewidth=1)
t3p2=ax.plot(get_avg_learn_curve_by_education(participants, VERSION, "somecollege", 1, TYPE),'b--',antialiased=True,markersize=3,linewidth=1)
t4p2=ax.plot(get_avg_learn_curve_by_education(participants, VERSION, "bachelors", 1, TYPE),'p--',antialiased=True,markersize=3,linewidth=1)
t5p2=ax.plot(get_avg_learn_curve_by_education(participants, VERSION, "somegrad", 1, TYPE),'y--',antialiased=True,markersize=3,linewidth=1)
t6p2=ax.plot(get_avg_learn_curve_by_education(participants, VERSION, "masters", 1, TYPE),'k--',antialiased=True,markersize=3,linewidth=1)
t7p2=ax.plot(get_avg_learn_curve_by_education(participants, VERSION, "doctor", 1, TYPE),'o--',antialiased=True,markersize=3,linewidth=1)
ax.legend( (t1p2[0], t2p2[0], t3p2[0], t4p2[0], t5p2[0], t6p2[0], t7p2[0]), ('<H.S. (N=1)','H.S. (N=4)','<B.A. (N=16)','B.A (N=15)','<M.A. (N=6)','M.A. (N=8)','DR (N=0)') )
plt.axis([-1,10,0,0.7])
plt.title('Type II')
plt.ylabel('Probability of Error')
plt.xlabel('Training Blocks')
plt.show()

# <codecell>

ages=get_age(participants, "5.3", 1, 0)+get_age(participants, "5.3", 1, 1)+get_age(participants, "5.3", 1, 3)+get_age(participants, "5.3", 1, 5)+get_age(participants, "5.32", 1, 0)+get_age(participants, "5.32", 1, 1)+get_age(participants, "5.32", 1, 3)+get_age(participants, "5.32", 1, 5)

print "mean age is ", mean(ages)

# plot parameters
ind = arange(7)
width=0.35


fig = plt.figure()
ax = fig.add_subplot(111)


ageCs=[len(filter(lambda x: x<18, ages)),
len(filter(lambda x: x>=18 and x<25, ages)),
len(filter(lambda x: x>=25 and x<35, ages)),
len(filter(lambda x: x>=35 and x<45, ages)),
len(filter(lambda x: x>=45 and x<55, ages)),
len(filter(lambda x: x>=55 and x<65, ages)),
len(filter(lambda x: x>=65, ages))]
passv = ax.bar(ind, array(ageCs)/float(len(ages)), width, color='c')

ax.set_ylabel('Proportion each group')
ax.set_title('Age Breakdown')
ax.set_xticks(ind+width/2)
ax.set_xticklabels(('<18','18-24', '25-34', '35-44', '45-54', '55-64', '65+'))
#labels = pylab.getp(pylab.gca(),'xticklabels')
plt.axis([-0.25,7.5,0,0.5])
plt.show()

# <codecell>

fig = plt.figure(figsize=(8,6))
ax=fig.add_subplot(111)
VERSION='5.32'
TYPE=1
t1p2=ax.plot(get_avg_learn_curve_by_age(participants, VERSION, -2, 18, 1, TYPE),'ro-',antialiased=True,markersize=3,linewidth=1)
t2p2=ax.plot(get_avg_learn_curve_by_age(participants, VERSION, 18, 24, 1, TYPE),'go-',antialiased=True,markersize=3,linewidth=1)
t3p2=ax.plot(get_avg_learn_curve_by_age(participants, VERSION, 24, 34, 1, TYPE),'bo-',antialiased=True,markersize=3,linewidth=1)
t4p2=ax.plot(get_avg_learn_curve_by_age(participants, VERSION, 35, 44, 1, TYPE),'mo-',antialiased=True,markersize=3,linewidth=1)
t5p2=ax.plot(get_avg_learn_curve_by_age(participants, VERSION, 45, 54, 1, TYPE),'yo-',antialiased=True,markersize=3,linewidth=1)
t6p2=ax.plot(get_avg_learn_curve_by_age(participants, VERSION, 55, 64, 1, TYPE),'ko-',antialiased=True,markersize=3,linewidth=1)
t7p2=ax.plot(get_avg_learn_curve_by_age(participants, VERSION, 65, 100, 1, TYPE),'co-',antialiased=True,markersize=3,linewidth=1)
ax.legend( (t1p2[0], t2p2[0], t3p2[0], t4p2[0], t5p2[0], t6p2[0], t7p2[0]), ('<18 (N=0)','18-24 (N=17)','25-34 (N=16)','35-44 (N=15)','45-54 (N=6)','55-64 (N=8)','65+ (N=0)') )
plt.axis([-1,10,0,0.7])
plt.title('Type II')
plt.ylabel('Probability of Error')
plt.xlabel('Training Blocks')
plt.show()

# <headingcell level=1>

# Reaction time analysis

# <codecell>

# a function to gather up the learning curves for different subsets of subjects and averages them
def get_median_rt(people, version, training):
    allTest = []
    count=0
    for key in people.keys():
        p = people[key]
        #print p.traintype, p.rule, p.physicalaids;#
        if p.codeversion==version and p.physicalaids=='no' \
           and p.traintype==training:
                #and count_longest_run(p.dfTest['resp'])<16 \
            #and p.endhit - p.beginexp < timedelta(minutes=30):
            #print 
            allTest += [median(p.dfTest['rt'])]
            count += 1
    print "Condition ", training, ": has ", count, " participants."
    return allTest

# <codecell>

fig = plt.figure(figsize=(12,9))
ax = fig.add_subplot(111)
n, bins, patches = ax.hist(get_median_rt(participants, '4.0', 1), 100, normed=0, facecolor='orange',alpha=0.75)
ax.set_title('Problem I')
ax.set_ylabel('Frequency')
ax.set_ylabel('Blocks to Criterion')
plt.axis([1,7500,0,100])
plt.show()

# <headingcell level=1>

# Number of drop outs

# <codecell>

# connect to database and load relevant information
db, conn = connect_to_database(DATABASE, TABLENAME)
s = db.select()
s = s.where(and_(db.c.beginexp!=None, db.c.codeversion=="5.3", db.c.datafile!=None))
records = get_people(conn, s)

# <codecell>

# load up all the participants into a dictionary indexed by subjid
participants = {}
for i in range(len(records)):
    p = Participant(records[i], process=False)
    participants[p.subjid] = p
nsubj = len(participants.keys())
print "Number of subjects is ", nsubj

# <codecell>

(47+55)-(41+41)

# <codecell>

def get_dropouts(people, version, training, rule):
    count = countb = 0
    for key in people.keys():
        p = people[key]
        if p.codeversion==version and p.traintype==training and p.rule==rule and p.endhit==None:
            count += 1
        elif p.codeversion==version and p.traintype==training and p.rule==rule and p.endhit!=None:
            countb += 1
    return count, countb




VERSION = '4.0'

# plot parameters
ind = arange(6)
width=0.35


fig = plt.figure()
ax = fig.add_subplot(111)


dropouts = [get_dropouts(participants, '4.2', 1, i)[0] for i in range(6)]
passv = ax.bar(ind, dropouts, width, color='c')
print dropouts
#passiveMs = array([44.0, 85.4, 121.6, 127.0, 133.8, 189.2])/16.
#passv = ax.bar(ind+width, passiveMs, width, color='y')
ax.set_ylabel('# of Dropouts')
ax.set_title('Drop-outs per condition')
ax.set_xticks(ind+width/2.)
ax.set_xticklabels(('I','II','III','IV','V','VI'))
plt.axis([-0.5,6,0,12])
plt.show()

# <codecell>


