#!/usr/bin/env python
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


################################################################################

def submit(sample, first, last):
    scriptName = 'job_'+sample+'_'+str(first)+'_'+str(last)+'.sh'
    jobName    = 'job_'+sample+'_'+str(first)+'_'+str(last)
    outName    = sample+'_'+str(first)+'_'+str(last)
    f = open(scriptName,'w')
    f.write('#!/bin/bash\n\n')
    f.write('mkdir /scratch/bianchi/\n')
    f.write('cd /mnt/t3nfs01/data01/shome/bianchi/TTH-76X-heppy/CMSSW/src/TTH/MEIntegratorStandalone/test/macros\n')
    f.write('source /swshare/psit3/etc/profile.d/cms_ui_env.sh\n')
    f.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
    f.write('eval `scramv1 runtime -sh`\n')
    f.write('\n')    
    f.write('python run_histos.py '+sample+' '+str(first)+' '+str(last)+'\n')
    f.write('mv /scratch/bianchi/'+outName+'.root ./\n')    
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
    #["M750",1,20], 
    ["HT100to200", 1, 50], 
    #["HT200to300", 10, 25], 
    #["HT300to500", 10, 25], 
    #["HT500to700", 10, 25], 
    #["HT700to1000",10, 20], 
    #["HT1000to1500",7, 10], 
    #["HT1500to2000",7,  8], 
    #["HT2000toInf", 5,  6],
    ]:
    for it in xrange(sample[2]):
        first = it*sample[1]+1
        last = (it+1)*sample[1]
        submit(sample[0], first, last)
