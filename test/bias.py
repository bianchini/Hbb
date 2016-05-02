import ROOT
import os
from sys import argv
import sys
sys.path.append('./')

ROOT.gROOT.SetBatch(True)

ROOT.gSystem.Load("bias_study_C.so")

ROOT.bias_study("Xbb_workspace", "./plots/V2/", argv[1], "buk",  argv[2], argv[3], float(argv[4]), 1000, float(argv[5]), float(argv[6]))
