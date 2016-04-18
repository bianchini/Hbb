#!/usr/bin/env python

from sys import argv
import commands
import time
import re
import os
import string
from os import listdir
from os.path import isfile, join

import FWCore.ParameterSet.Config as cms

import sys
sys.path.append('./')

# options are "run_tree_skimmer" "run_histos"
run = argv[1]

################################################################################

def submit(sample, first, last, postfix):
    print "Running: submit.py "+run
    scriptName = 'job_'+sample+'_'+str(first)+'_'+str(last)+'.sh'
    jobName    = 'job_'+sample+'_'+str(first)+'_'+str(last)
    outName = ""
    if run=="run_histos":
        if first>=0:
            outName = sample+'_'+str(first)+'_'+str(last)
        else:
            outName = sample
    if run=="run_tree_skimmer":
        outName = "tree_"+str(postfix)
    f = open(scriptName,'w')
    f.write('#!/bin/bash\n\n')
    f.write('mkdir /scratch/bianchi/'+(sample+'/' if run=="run_tree_skimmer" else '')+'\n')
    f.write('cd $HOME/TTH-76X-heppy/CMSSW/src/Hbb/test/\n')
    f.write('source /swshare/psit3/etc/profile.d/cms_ui_env.sh\n')
    f.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
    f.write('eval `scramv1 runtime -sh`\n')
    f.write('\n')    
    f.write('python '+run+'.py '+sample+' '+str(first)+' '+str(last)+' '+str(postfix)+'\n')
    if run=="run_tree_skimmer":
        f.write('mkdir '+sample+'\n')
        f.write('mv /scratch/bianchi/'+sample+'/'+outName+'.root ./'+sample+'/'+'\n')    
    else:
        f.write('mv /scratch/bianchi/'+outName+'.root ./'+'\n')    

    f.close()
    os.system('chmod +x '+scriptName)
             
    submitToQueue = 'qsub -V -cwd -q all.q -N '+jobName+' '+scriptName
    print submitToQueue
    os.system(submitToQueue)
    time.sleep( 1.0 )

    print "@@@@@ END JOB @@@@@@@@@@@@@@@"


##########################################

# [name, files_per_sample, njobs]
for sample in [
    #["Run2015D",3, 71],
    #["M750",1,20], 
    #["HT100to200", 1, 50], 
    #["HT200to300", 10, 25], 
    #["HT300to500", 10, 25], 
    #["HT500to700", 10, 25], 
    #["HT700to1000",10, 20], 
    #["HT1000to1500",7, 10], 
    #["HT1500to2000",4,  13], 
    #["HT2000toInf", 5,  6],

    ["M750",-1, 1], 
    ["HT100to200", -1, 1], 
    ["HT200to300", -1, 1], 
    ["HT300to500", -1, 1], 
    ["HT500to700", -1, 1], 
    ["HT700to1000",-1, 1], 
    ["HT1000to1500",-1, 1], 
    ["HT1500to2000",-1, 1], 
    ["HT2000toInf", -1, 1],
    ["Run2015D", -1, 1],
    ]:
    for it in xrange(sample[2]):
        postfix = it+1
        first = it*sample[1]+1
        last = (it+1)*sample[1]
        submit(sample[0], first if sample[1]>=0 else -1, last, postfix)
        #exit(1)
