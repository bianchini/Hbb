from sys import argv
import commands
import time
import re
import os
import string
from os import listdir

import sys
sys.path.append('./')

#spin = 'GluGluSpin0ToBBbar_W_1p0_M_X_TuneCUEP8M1_13TeV_pythia8'
spin = 'RSGravitonToBBbar_kMpl01_M_X_TuneCUEP8M1_13TeV_pythia8'

def create(mass=750 , width=0.01):

    fin = open( spin+'_cfi.py' , 'r')
    fout = open( spin.replace('_X_', '_'+str(mass)+'_')+'_cfi.py', 'w')

    for line in fin:
        if 'm0' in line:
            fout.write(line.rstrip('\',\n')+("%.0f" % mass)+'\', \n')
        elif 'mWidth' in line:
            fout.write(line.rstrip('\',\n')+("%.1f" % (mass*width))+'\', \n')
        else:
            fout.write(line)

    fout.close()
    fin.close()
    
##################

def create_GENSIM_cfg( mass ):
    command = 'cmsDriver.py Configuration/GenProduction/python/'+(spin.replace('_X_', '_'+str(mass)+'_'))+'_cfi.py'+' --fileout file:GEN-SIM.root --mc --eventcontent RAWSIM --customise SLHCUpgradeSimulations/Configuration/postLS1Customs.customisePostLS1,Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM --conditions MCRUN2_71_V1::All --beamspot Realistic50ns13TeVCollision --step GEN,SIM --magField 38T_PostLS1 --python_filename GEN-SIM_'+str(mass)+'_cfg.py --no_exec -n 3'
    print command
    os.system(command)

#################

def create_GENSIM_crab( mass, unitsPerJob, totalUnits ):

    fin = open( 'crab_GEN-SIM_cfg.py.ex', 'r')
    fout = open( 'crab_GEN-SIM_'+str(mass)+'_cfg.py', 'w')

    for line in fin:
        if 'requestName' in line:
            fout.write(line.rstrip('\n')+' \'gen-sim_'+spin+'_'+str(mass)+'\'\n')
        elif 'psetName' in line:
            fout.write(line.rstrip('\n')+' \'GEN-SIM_'+str(mass)+'_cfg.py\'\n')
        elif 'unitsPerJob' in line:
            fout.write(line.rstrip('\n')+' '+str(unitsPerJob)+'\n')
        elif 'totalUnits' in line:
            fout.write(line.rstrip('\n')+' '+str(totalUnits)+'\n')
        elif 'outputPrimaryDataset' in line:
            fout.write(line.rstrip('\n')+' \''+(spin.replace('_X_', '_'+str(mass)+'_'))+'\'\n')
        else:
            fout.write(line)
    fout.close()
    fin.close()

#################################

def submit_GENSIM_crab(mass):
    command = 'crab submit -c '+'crab_GEN-SIM_'+str(mass)+'_cfg.py'
    print command
    os.system(command)


#################################

def sequence_GENSIM(mass):
    create(mass)
    create_GENSIM_cfg(mass)
    create_GENSIM_crab(mass, 1000, 100000)
    #submit_GENSIM_crab(mass)

#################################

def create_DR1_cfg( mass ):
    command = 'cmsDriver.py step1 --filein file:GEN-SIM.root --fileout file:DIGI-RECO_step1.root --pileup_input "dbs:/MinBias_TuneCUETP8M1_13TeV-pythia8/RunIISummer15GS-MCRUN2_71_V1-v2/GEN-SIM" --mc --eventcontent RAWSIM --pileup 2015_25ns_FallMC_matchData_PoissonOOTPU --datatier GEN-SIM-RAW --conditions 76X_mcRun2_asymptotic_v12 --step DIGI,L1,DIGI2RAW,HLT:@frozen25ns --era Run2_25ns --python_filename DIGI-RECO_1_'+str(mass)+'_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n -1' 
    print command
    os.system(command)

#################################

def create_DR1_crab( mass, dataset):

    fin = open( 'crab_DR1_cfg.py.ex', 'r')
    fout = open( 'crab_DR1_'+str(mass)+'_cfg.py', 'w')

    for line in fin:
        if 'requestName' in line:
            fout.write(line.rstrip('\n')+' \'dr1_'+spin+'_'+str(mass)+'\'\n')
        elif 'psetName' in line:
            fout.write(line.rstrip('\n')+' \'DIGI-RECO_1_'+str(mass)+'_cfg.py\'\n')
        elif 'inputDataset' in line:
            fout.write(line.rstrip('\n')+' '+dataset+'\n')
        else:
            fout.write(line)
    fout.close()
    fin.close()

#################################

def submit_DR1_crab(mass):
    command = 'crab submit -c '+'crab_DR1_'+str(mass)+'_cfg.py'
    print command
    #os.system(command)

#################################

def sequence_DR1(mass):
    create_DR1_crab(mass, '')
    submit_DR1_crab(mass)

################################

# finally, we run:
for mass in [ 
    #650,
    #750, 
    #850,
    #1000,
    #1200,
    700
    ]:
    sequence_GENSIM(mass)
    #sequence_DR1(mass)
