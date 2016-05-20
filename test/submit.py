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
    f.write('mkdir -pv /scratch/$USER/'+(sample+'/' if run=="run_tree_skimmer" else '')+'\n')
    f.write('[ $? -ne 0 ] && echo \"Couldn\'t create dir /scratch/$USER/'+(sample+'/' if run=="run_tree_skimmer" else '')+'\" && exit 1\n')
    f.write('cd $HOME/TTH-76X-heppy/CMSSW/src/Hbb/test/\n')
    f.write('[ `echo $HOSTNAME | grep t3ui` ] && [ -r /mnt/t3nfs01/data01/swshare/psit3/etc/profile.d/cms_ui_env.sh ] && source /mnt/t3nfs01/data01/swshare/psit3/etc/profile.d/cms_ui_env.sh && echo \"UI features enabled\"\n')
    f.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
    f.write('eval `scramv1 runtime -sh`\n')
    f.write('\n')    
    f.write('python '+run+'.py '+sample+' '+str(first)+' '+str(last)+' '+str(postfix)+'\n')
    if run=="run_tree_skimmer":
        f.write('mkdir '+sample+'\n')
        f.write('mv /scratch/$USER/'+sample+'/'+outName+'.root ./'+sample+'/'+'\n')    
    else:
        f.write('mv /scratch/$USER/'+outName+'.root ./'+'\n')    

    f.close()
    os.system('chmod +x '+scriptName)
             
    submitToQueue = 'qsub -V -cwd -q all.q -N '+jobName+' '+scriptName
    print submitToQueue
    os.system(submitToQueue)
    time.sleep( 1.0 )

    print "@@@@@ END JOB @@@@@@@@@@@@@@@"


##########################################

# [name, files_per_sample, njobs, offset [OPTIONAL]]
for sample in [

    # run_tree_skimmer:
    #["Run2015D",3, 71],
    #["Run2015C",1, 3],
    #["M750",1,20], 
    #["HT100to200", 2, 25], 
    #["HT200to300", 20, 13], 
    #["HT300to500", 20, 13], 
    #["HT500to700", 20, 13], 
    #["HT700to1000",5, 40], 
    #["HT1000to1500",14, 5], 
    #["HT1500to2000",8,  7], 
    #["HT2000toInf", 10,  3],
    #["Spin0_M650", 1, 1],
    #["Spin0_M750", 1, 1],
    #["Spin0_M850", 1, 1],
    #["Spin0_M1000", 1, 1],
    #["Spin0_M1200", 1, 1],
    #["Spin2_M650", 1, 1],
    #["Spin2_M750", 1, 1],
    #["Spin2_M850", 1, 1],
    #["Spin2_M1000", 1, 1],
    #["Spin2_M1200", 1, 1],
    #["TT_ext3",4,100,0],
    #["ST_t_atop", 5, 5],
    #["ST_t_top", 5, 8],
    #["ST_tW_atop", 4, 4],
    #["ST_tW_top", 4, 4],

    # run_histos:
    #["HT100to200", -1, 1], 
    #["HT200to300", -1, 1], 
    #["HT300to500", -1, 1], 
    #["HT500to700", -1, 1], 
    #["HT700to1000",-1, 1], 
    #["HT1000to1500",-1, 1], 
    #["HT1500to2000",-1, 1], 
    #["HT2000toInf", -1, 1],
    #["Run2015D", -1, 1],
    #["Run2015C", -1, 1],
    ["TT_ext3",-1,1],
    #["ST_t_atop", -1,1],
    #["ST_t_top", -1,1],
    #["ST_tW_atop", -1,1],
    #["ST_tW_top", -1,1],
    #["Spin0_M650", -1, 1],
    #["Spin0_M750", -1, 1],
    #["Spin0_M850", -1, 1],
    #["Spin0_M1000", -1, 1],
    #["Spin0_M1200", -1, 1],
    #["Spin2_M650", -1, 1],
    #["Spin2_M750", -1, 1],
    #["Spin2_M850", -1, 1],
    #["Spin2_M1000", -1, 1],
    #["Spin2_M1200", -1, 1],
    ##["M750",-1, 1], 
    ]:
    for it in xrange(sample[2]):
        postfix = it+1
        first = it*sample[1]+1 + (sample[3] if len(sample)>3 else 0)
        last = (it+1)*sample[1] + (sample[3] if len(sample)>3 else 0)
        submit(sample[0], first if sample[1]>=0 else -1, last, postfix)
        #exit(1)
