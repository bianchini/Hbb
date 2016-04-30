import ROOT
import os
from sys import argv
import sys
sys.path.append('./')

ROOT.gROOT.SetBatch(True)

ROOT.gSystem.Load("bias_study_C.so")

ROOT.bias_study("Xbb_workspace", "./plots/V2/", "Had_LT_MinPt150_DH1p6_MassFSR_550to1200", "buk",  "mass", argv[1], float(argv[2]), 1000)
