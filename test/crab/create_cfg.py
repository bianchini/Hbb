from sys import argv
import commands
import time
import re
import os
import string
from os import listdir

import sys
sys.path.append('./')

spin = 'GluGluSpin0ToBBbar_W_1p0_M_X_TuneCUEP8M1_13TeV_pythia8'
#spin = 'RSGravitonToBBbar_kMpl01_M_X_TuneCUEP8M1_13TeV_pythia8'

debug = True

datasets = {
    'GluGluSpin0ToBBbar_W_1p0_M_X_TuneCUEP8M1_13TeV_pythia8' : {
        '650' : {
            'DR1' : "",
            'DR2' : "",
            'MiniAODv2' : "",
            },
        '750' : {
            'DR1' : "",
            'DR2' : "",
            'MiniAODv2' : "",
            },
        '850' : {
            'DR1' : "",
            'DR2' : "",
            'MiniAODv2' : "",
            },
        '1000' : {
            'DR1' : "",
            'DR2' : "",
            'MiniAODv2' : "",
            },
        '1200' : {
            'DR1' : "",
            'DR2' : "",
            'MiniAODv2' : "",
            },
        },

    'RSGravitonToBBbar_kMpl01_M_X_TuneCUEP8M1_13TeV_pythia8' :{
        '650' : {
            'DR1' : "",
            'DR2' : "",
            'MiniAODv2' : "",
            },
        '750' : {
            'DR1' : "",
            'DR2' : "",
            'MiniAODv2' : "",
            },
        '850' : {
            'DR1' : "",
            'DR2' : "",
            'MiniAODv2' : "",
            },
        '1000' : {
            'DR1' : "",
            'DR2' : "",
            'MiniAODv2' : "",
            },
        '1200' : {
            'DR1' : "",
            'DR2' : "",
            'MiniAODv2' : "",
            },
        }
}

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
    if debug:
        return
    os.system(command)


#################################

def sequence_GENSIM(mass):
    create(mass)
    create_GENSIM_cfg(mass)
    create_GENSIM_crab(mass, 1000, 100000)
    submit_GENSIM_crab(mass)

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
    if debug:
        return
    os.system(command)

#################################

def sequence_DR1(mass):
    create_DR1_cfg(mass)
    create_DR1_crab(mass, datasets[spin][str(mass)]['DR1'] )
    submit_DR1_crab(mass)

#################################

def create_DR2_cfg( mass ):
    command = 'cmsDriver.py step2 --filein file:DIGI-RECO_step1.root --fileout file:DIGI-RECO.root --mc --eventcontent AODSIM,DQM --runUnscheduled --datatier AODSIM,DQMIO --conditions 76X_mcRun2_asymptotic_v12 --step RAW2DIGI,L1Reco,RECO,EI,DQM:DQMOfflinePOGMC --era Run2_25ns --python_filename DIGI-RECO_2_'+str(mass)+'_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 1'
    print command
    os.system(command)

#################################

def create_DR2_crab( mass, dataset):

    fin = open( 'crab_DR2_cfg.py.ex', 'r')
    fout = open( 'crab_DR2_'+str(mass)+'_cfg.py', 'w')

    for line in fin:
        if 'requestName' in line:
            fout.write(line.rstrip('\n')+' \'dr2_'+spin+'_'+str(mass)+'\'\n')
        elif 'psetName' in line:
            fout.write(line.rstrip('\n')+' \'DIGI-RECO_2_'+str(mass)+'_cfg.py\'\n')
        elif 'inputDataset' in line:
            fout.write(line.rstrip('\n')+' '+dataset+'\n')
        else:
            fout.write(line)
    fout.close()
    fin.close()

#################################

def submit_DR2_crab(mass):
    command = 'crab submit -c '+'crab_DR2_'+str(mass)+'_cfg.py'
    print command
    if debug:
        return
    os.system(command)

#################################

def sequence_DR2(mass):
    create_DR2_cfg(mass)
    create_DR2_crab(mass, datasets[spin][str(mass)]['DR2'] )
    submit_DR2_crab(mass)

#################################

def create_MiniAODv2_cfg( mass ):
    command = 'cmsDriver.py step1 --filein file:DIGI-RECO.root --fileout file:MiniAODv2.root --mc --eventcontent MINIAODSIM --runUnscheduled --datatier MINIAODSIM --conditions 76X_mcRun2_asymptotic_v12 --step PAT --era Run2_25ns --python_filename MiniAODv2_'+str(mass)+'_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n -1'
    print command
    os.system(command)

#################################

def create_MiniAODv2_crab( mass, dataset):

    fin = open( 'crab_MiniAODv2_cfg.py.ex', 'r')
    fout = open( 'crab_MiniAODv2_'+str(mass)+'_cfg.py', 'w')

    for line in fin:
        if 'requestName' in line:
            fout.write(line.rstrip('\n')+' \'miniAODv2_'+spin+'_'+str(mass)+'\'\n')
        elif 'psetName' in line:
            fout.write(line.rstrip('\n')+' \'MiniAODv2_'+str(mass)+'_cfg.py\'\n')
        elif 'inputDataset' in line:
            fout.write(line.rstrip('\n')+' '+dataset+'\n')
        else:
            fout.write(line)
    fout.close()
    fin.close()

#################################

def submit_MiniAODv2_crab(mass):
    command = 'crab submit -c '+'crab_MiniAODv2_'+str(mass)+'_cfg.py'
    print command
    if debug:
        return
    os.system(command)

#################################

def sequence_MiniAODv2(mass):
    create_MiniAODv2_cfg(mass)
    create_MiniAODv2_crab(mass, datasets[spin][str(mass)]['MiniAODv2'] )
    submit_MiniAODv2_crab(mass)

################################


# finally, we run:
for mass in [ 
    #650,
    750, 
    #850,
    #1000,
    #1200,
    ]:
    if argv[1]=='GENSIM':
        sequence_GENSIM(mass)
    elif argv[1]=='DR1':
        sequence_DR1(mass)
    elif argv[1]=='DR2':
        sequence_DR2(mass)
    elif argv[1]=='MiniAODv2':
        sequence_MiniAODv2(mass)
