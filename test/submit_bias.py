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

################################################################################

def submit(pdf,xsec, cat='Had_LT_MinPt150_DH1p6_MassFSR_550to1200'):
    print "Running: submit_bias.py"
    scriptName = 'job_'+pdf+'_'+str(xsec)+'.sh'
    jobName    = 'job_'+pdf+'_'+str(xsec)
    f = open(scriptName,'w')
    f.write('#!/bin/bash\n\n')
    f.write('cd $HOME/TTH-76X-heppy/CMSSW/src/Hbb/test/\n')
    f.write('[ `echo $HOSTNAME | grep t3ui` ] && [ -r /mnt/t3nfs01/data01/swshare/psit3/etc/profile.d/cms_ui_env.sh ] && source /mnt/t3nfs01/data01/swshare/psit3/etc/profile.d/cms_ui_env.sh && echo \"UI features enabled\"\n')
    f.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
    f.write('eval `scramv1 runtime -sh`\n')
    f.write('\n')    
    f.write('python bias.py '+pdf+' '+str(xsec)+' '+cat+'\n')
    f.close()
    os.system('chmod +x '+scriptName)
             
    submitToQueue = 'qsub -V -cwd -q all.q -N '+jobName+' '+scriptName
    print submitToQueue
    os.system(submitToQueue)
    time.sleep( 1.0 )

    print "@@@@@ END JOB @@@@@@@@@@@@@@@"


##########################################

for cat in ['Had_LT_MinPt150_DH1p6_MassFSR_540to1200', 
            'Had_LT_MinPt150_DH1p6_MassFSR_550to1200', 
            'Had_LT_MinPt150_DH1p6_MassFSR_560to1200',
            'Had_LT_MinPt150_DH1p6_MassFSR_570to1200',
            'Had_LT_MinPt150_DH1p6_MassFSR_550to1300',
            'Had_LT_MinPt150_DH1p6_MassFSR_550to1400'
            ]:
    for pdf in ["mass", "pol", "pow", "polyexp", "exp"]:
        for xsec in [1.]:
            submit(pdf, xsec, cat)
