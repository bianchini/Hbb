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
        os.system('combine -M Asymptotic '+datacard+'.txt'+' -n '+datacard)
        f = ROOT.TFile.Open("higgsCombine"+datacard+".Asymptotic.mH120.root")
        t = f.Get("limit")
        res = []
        for iev in xrange(t.GetEntries()):
            t.GetEntry(iev)
            ev = t
            res.append(ev.limit)
        return res
    else:
        os.system('combine -M MaxLikelihoodFit '+datacard+'.txt'+' --plots -n '+datacard)
        return []

##############################################


tests = []
for cat in ['Had_MT_MinPt200_DH2p0','Had_MT_MinPt200_DH1p6', 'Had_MT_MinPt150_DH2p0', 'Had_MT_MinPt150_DH1p6']:
    for pdf in ['mass_pdf_bkg']:
        for x_range in ['550to1200']:
            for mass in ['MassFSR', 'MassAK08']:
                tests.append( cat + '_' + mass + '_' + x_range + '_buk_pdf_sgn_' + pdf)

out = ROOT.TFile.Open("limit.root", "RECREATE")
h = ROOT.TH1F("h", "Limits", len(tests), 0, len(tests))
h.SetMinimum(0.)
h.SetMaximum(2.5)
h.SetMarkerStyle(ROOT.kFullCircle)
h.SetMarkerColor(ROOT.kBlack)
h.SetMarkerSize(2)

for itest,test in enumerate(tests):
    res = run("Xbb_workspace_"+test)
    h.SetBinContent(itest+1, res[2])
    h.GetXaxis().SetBinLabel(itest+1, test)

out.cd()
h.Write("",ROOT.TObject.kOverwrite)
out.Close()
