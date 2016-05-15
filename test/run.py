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
        res = []
        os.system('combine -M Asymptotic --run expected '+datacard+'.txt'+' -n '+datacard)
        f = ROOT.TFile.Open("higgsCombine"+datacard+".Asymptotic.mH120.root")
        if f==None or f.IsZombie():
            return res
        t = f.Get("limit")
        if t==None:
            f.Close()
            return res
        for iev in xrange(t.GetEntries()):
            t.GetEntry(iev)
            ev = t
            res.append(ev.limit)
        f.Close()
        return res
    else:
        os.system('combine -M MaxLikelihoodFit '+datacard+'.txt'+' --plots -n '+datacard+' --rMin -10 --rMax +10')
        return []

##############################################


tests = []
for cat_btag in [
    'Had_LT', 
    'Had_MT',
    'Had_TT'
    ]:
    for cat_kin in [
        'MinPt150_DH1p1', 
        'MinPt150_DH1p6', 
        'MinPt150_DH2p0', 
        'MinPt175_DH1p1', 
        'MinPt175_DH1p6', 
        'MinPt175_DH2p0',
        'MinPt200_DH1p1', 
        'MinPt200_DH1p6', 
        'MinPt200_DH2p0', 
        ]:        
        for pdf_s in ['buk']:
            for pdf_b in ['dijet']:
                for x_range in ['550to1200']:
                    for mass in ['MassFSR']:
                        for sgn in ['Spin0_M750']:
                            tests.append( cat_btag + '_' + cat_kin + '_' + mass + '_' + x_range + '_' + pdf_s + '_' + pdf_b + '_' + sgn)

print tests

results = []
for itest,test in enumerate(tests):
    res = run("Xbb_workspace_"+test, do_limit=True)
    if len(res)>0:
        results.append([test,res])


c = ROOT.TCanvas("c", "canvas", 1200, 400) 
pad1 = ROOT.TPad("pad1", "pad1", 0, 0.1, 1, 1.0)     
#pad1.SetBottomMargin(0) 
pad1.SetGridx()  
pad1.SetGridy()  
pad1.Draw()      
pad1.cd()    

h = ROOT.TH1F("h", "Expected 95% CL limits", len(results), 0, len(results))
h.SetStats(0)
h.SetMinimum(2.)
h.SetMaximum(5.0)
h.SetMarkerStyle(ROOT.kFullCircle)
h.SetMarkerColor(ROOT.kBlue)
h.SetMarkerSize(2)
h.SetLineColor(ROOT.kBlue)
h.SetLineWidth(3)
for ires,res in enumerate(results):
    if len(res[1])>=3:
        h.SetBinContent(ires+1, res[1][2])
        h.GetXaxis().SetBinLabel(ires+1, res[0][4:21])
h.Draw("L")
c.SaveAs("limit.png")
