#!/usr/bin/env python

from sys import argv
import commands
import time
import re
import os
import string

import ROOT

def run(datacard, do_limit=True):

    print "Running on", datacard
    if do_limit:
        os.system('combine -M Asymptotic --run expected '+datacard+'.txt'+' -n '+datacard)
        f = ROOT.TFile.Open("higgsCombine"+datacard+".Asymptotic.mH120.root")
        t = f.Get("limit")
        res = []
        for iev in xrange(t.GetEntries()):
            t.GetEntry(iev)
            ev = t
            res.append(ev.limit)
        return res
    else:
        os.system('combine -M MaxLikelihoodFit '+datacard+'.txt'+' --plots -n '+datacard+' --rMin -10 --rMax +10')
        return []

##############################################


tests = []
for cat_btag in [
    #'Had_LT', 
    'Had_MT'
    ]:
    for cat_kin in [
        'MinPt150_DH1p6', 
        #'MinPt150_DH2p0', 
        #'MinPt180_DH1p6', 
        #'MinPt180_DH2p0',
        ]:        
        for pdf_s in ['buk']:
            for pdf_b in ['dijet']:
                for x_range in ['550to1200']:
                    for mass in ['MassFSR']:
                        for sgn in ['Spin0_M750']:
                            tests.append( cat_btag + '_' + cat_kin + '_' + mass + '_' + x_range + '_' + pdf_s + '_' + pdf_b + '_' + sgn)

out = ROOT.TFile.Open("limit.root", "RECREATE")
h = ROOT.TH1F("h", "Limits", len(tests), 0, len(tests))
h.SetMinimum(0.)
h.SetMaximum(4.0)
h.SetMarkerStyle(ROOT.kFullCircle)
h.SetMarkerColor(ROOT.kBlack)
h.SetMarkerSize(2)

print tests

for itest,test in enumerate(tests):
    res = run("Xbb_workspace_"+test, do_limit=False)
    if len(res)>=3:
        h.SetBinContent(itest+1, res[2])
        h.GetXaxis().SetBinLabel(itest+1, test)

out.cd()
h.Write("",ROOT.TObject.kOverwrite)
out.Close()
