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

def submit(cfg_fname="Xbb_workspace_Had_MT_MinPt100_DH1p6_MassFSR_400to1200", cfg_pdf_alt_name="dijet", cfg_pdf_fit_name="dijet", cfg_n_bins=-1, cfg_pdf_sgn_name="buk", cfg_sgn_name="Spin0_M750", cfg_sgn_xsec=0., cfg_ntoys=100, cfg_nproc=0):
    print "Running: submit_bias.py"
    jobName    = 'job_'+cfg_pdf_alt_name+'_'+cfg_pdf_fit_name+'_'+str(nproc)
    scriptName = jobName+'.sh'
    f = open(scriptName,'w')
    f.write('#!/bin/bash\n\n')
    f.write('cd $HOME/TTH-76X-heppy/CMSSW/src/Hbb/test/\n')
    f.write('[ `echo $HOSTNAME | grep t3ui` ] && [ -r /mnt/t3nfs01/data01/swshare/psit3/etc/profile.d/cms_ui_env.sh ] && source /mnt/t3nfs01/data01/swshare/psit3/etc/profile.d/cms_ui_env.sh && echo \"UI features enabled\"\n')
    f.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
    f.write('eval `scramv1 runtime -sh`\n')
    f.write('\n')    
    f.write('python bias_study.py '+cfg_fname+' '+cfg_pdf_alt_name+' '+cfg_pdf_fit_name+' '+str(cfg_n_bins)+' '+cfg_pdf_sgn_name+' '+cfg_sgn_name+' '+str(cfg_sgn_xsec)+' '+str(cfg_ntoys)+' '+str(cfg_nproc)+'\n')
    f.close()
    os.system('chmod +x '+scriptName)
             
    submitToQueue = 'qsub -V -cwd -q all.q -N '+jobName+' '+scriptName
    print submitToQueue
    os.system(submitToQueue)
    time.sleep( 0.5 )

    print "@@@@@ END JOB @@@@@@@@@@@@@@@"


##########################################

fnames =  [
    #['Xbb_workspace_Had_MT_MinPt100_DH1p6_MassFSR_400to800',  ["Spin0_M550", "Spin0_M600","Spin0_M650"] ],
    #['Xbb_workspace_Had_MT_MinPt100_DH1p6_MassFSR_500to900',  ["Spin0_M700", "Spin0_M750", "Spin0_M800"] ],
    #['Xbb_workspace_Had_MT_MinPt100_DH1p6_MassFSR_600to1000', ["Spin0_M850", "Spin0_M900"] ],
    #['Xbb_workspace_Had_MT_MinPt100_DH1p6_MassFSR_700to1400', ["Spin0_M1000", "Spin0_M1100", "Spin0_M1200"] ],
]

sgns = ['Spin0_M550', 'Spin0_M600', 'Spin0_M650', 'Spin0_M700', 'Spin0_M750', 'Spin0_M800', 'Spin0_M850', 'Spin0_M900', 'Spin0_M1000', 'Spin0_M1100', 'Spin0_M1200']
for sgn in sgns:        
    mX = float(sgn.split('_')[-1][1:])
    edges = get_sliding_edges(mass=mX)
    range_name = ("%.0fto%.0f" % (edges[0],edges[1]))            
    fnames.append( ['Xbb_workspace_Had_MT_MinPt100_DH1p6_MassFSR_'+range_name, [sgn]] )


for fname in fnames:
    for pdf_alt_name in [
        'polydijet',
        #'pow',
        #'exp',
        #'polyexp',
        #'pol',        
        ]:
        for pdf_fit_name in [
            #'polyexp', 
            'polydijet', 
            #'dijet'
            ]:
            for sgn_name in fname[1]:
                for nproc in xrange(1):
                    submit(cfg_fname=fname[0], cfg_pdf_alt_name=pdf_alt_name, cfg_pdf_fit_name=pdf_fit_name, 
                           cfg_n_bins=-1, 
                           cfg_pdf_sgn_name="buk", cfg_sgn_name=sgn_name, 
                           cfg_sgn_xsec=0., 
                           cfg_ntoys=0, 
                           cfg_nproc=nproc)
                    #exit(1)
