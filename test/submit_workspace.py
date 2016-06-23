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
sys.path.append('../python/')

from utilities import get_sliding_edges

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


use_fixed_ranges = False
use_sliding_edges = True

x_ranges = {
    400 : [800.],
    500 : [900.],
    600 : [1000.],
    700 : [1400.],
}

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

            if use_fixed_ranges:
                for xmin in x_ranges.keys():
                    for xmax in x_ranges[xmin]:  
                        submit(cfg_cat_btag, cfg_cat_kin, cfg_name, xmin, xmax)
                        #exit(1)
            elif use_sliding_edges:
                for mass in [550,600,650,700,750,800,850,900,1000,1100,1200]:
                    [xmin,xmax] = get_sliding_edges(mass=mass)
                    submit(cfg_cat_btag, cfg_cat_kin, cfg_name, xmin, xmax) 
                    #exit(1)
            else:
                exit(1)
