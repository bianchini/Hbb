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

def submit(cfg_cat_btag='Had_LT', cfg_cat_kin='MinPt150_DH1p6', cfg_name='MassFSR', cfg_xmin=550., cfg_xmax=1200.):
    print "Running: submit_workspace.py"
    jobName = 'job_'+cfg_cat_btag+'_'+cfg_cat_kin+'_'+('%.0f' % cfg_xmin)+'_'+('%.0f' % cfg_xmax)
    scriptName = jobName+'.sh'
    f = open(scriptName,'w')
    f.write('#!/bin/bash\n\n')
    f.write('cd $HOME/TTH-76X-heppy/CMSSW/src/Hbb/test/\n')
    f.write('[ `echo $HOSTNAME | grep t3ui` ] && [ -r /mnt/t3nfs01/data01/swshare/psit3/etc/profile.d/cms_ui_env.sh ] && source /mnt/t3nfs01/data01/swshare/psit3/etc/profile.d/cms_ui_env.sh && echo \"UI features enabled\"\n')
    f.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
    f.write('eval `scramv1 runtime -sh`\n')
    f.write('\n')    
    f.write('python create_workspace.py '+cfg_cat_btag+' '+cfg_cat_kin+' '+cfg_name+' '+('%.0f' % cfg_xmin)+' '+('%.0f' % cfg_xmax)+'\n')
    f.close()
    os.system('chmod +x '+scriptName)
             
    submitToQueue = 'qsub -V -cwd -q all.q -N '+jobName+' '+scriptName
    print submitToQueue
    os.system(submitToQueue)
    time.sleep( 1.0 )

    print "@@@@@ END JOB @@@@@@@@@@@@@@@"


##########################################

for cfg_cat_btag in [
    #'Had_LT', 
    'Had_MT', 
    #'Had_TT',
    ]:
    for cfg_cat_kin in [
        #'MinPt150_DH1p6', 
        'MinPt100_DH1p6', 
        #'MinMaxPt100150_DH1p6', 
        #'MinPt150_DH2p0', 'MinPt150_DH1p1', 
        #'MinPt175_DH1p6', 'MinPt175_DH2p0', 'MinPt175_DH1p1',
        #'MinPt200_DH1p6', 'MinPt200_DH2p0', 'MinPt200_DH1p1',
        ]:
        for cfg_name in [
            'MassFSR',
            ]:
            for xmin in [
                #400., 425., 450.,
                500., 525., 550.
                ]:
                for xmax in [
                    900., 1000., 1200.,
                    ]:
                    submit(cfg_cat_btag, cfg_cat_kin, cfg_name, xmin, xmax)
                    #exit(1)
