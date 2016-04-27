from sys import argv
import commands
import time
import re
import os
import string
from os import listdir

import sys
sys.path.append('./')


def create(mass=750 , width=0.01):

    fin = open( 'GluGluSpin0ToBBbar_W_1p0_M_X_TuneCUEP8M1_13TeV_pythia8_cfi.py', 'r')
    fout = open( 'GluGluSpin0ToBBbar_W_1p0_M_'+str(mass)+'_TuneCUEP8M1_13TeV_pythia8_cfi.py', 'w')

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
    command = 'cmsDriver.py Configuration/GenProduction/python/'+'GluGluSpin0ToBBbar_W_1p0_M_'+str(mass)+'_TuneCUEP8M1_13TeV_pythia8_cfi.py'+' --fileout file:GEN-SIM.root --mc --eventcontent RAWSIM --customise SLHCUpgradeSimulations/Configuration/postLS1Customs.customisePostLS1,Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM --conditions MCRUN2_71_V1::All --beamspot Realistic50ns13TeVCollision --step GEN,SIM --magField 38T_PostLS1 --python_filename GEN-SIM_'+str(mass)+'_cfg.py --no_exec -n 3'
    print command
    os.system(command)

#################

def create_GENSIM_crab( mass, unitsPerJob, totalUnits ):

    fin = open( 'crab_GEN-SIM_cfg.py', 'r')
    fout = open( 'crab_GEN-SIM_'+str(mass)+'_cfg.py', 'w')

    for line in fin:
        if 'requestName' in line:
            fout.write(line.rstrip('\n')+' \'gen-sim_'+str(mass)+'\'\n')
        elif 'psetName' in line:
            fout.write(line.rstrip('\n')+' \'GEN-SIM_'+str(mass)+'_cfg.py\'\n')
        elif 'unitsPerJob' in line:
            fout.write(line.rstrip('\n')+' '+str(unitsPerJob)+'\n')
        elif 'totalUnits' in line:
            fout.write(line.rstrip('\n')+' '+str(totalUnits)+'\n')
        elif 'outputPrimaryDataset' in line:
            fout.write(line.rstrip('\n')+' \'GluGluSpin0ToBBbar_W_1p0_M_'+str(mass)+'_TuneCUEP8M1_13TeV_pythia8\'\n')
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

def sequence(mass):
    create(mass)
    create_GENSIM_cfg(mass)
    create_GENSIM_crab(mass, 1000, 100000)
    submit_GENSIM_crab(mass)

################################

for mass in [750]:
    sequence(mass)
