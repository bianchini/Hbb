#!/usr/bin/env python

from sys import argv
import commands
import time
import re
import os
import string
import os.path
import math
import numpy as n

import ROOT

from ROOT import RooFit

import sys
sys.path.append('../../../python/')
sys.path.append('../../../../python/')
from utilities import get_sliding_edges
from parameters_cfi import luminosity

signal_to_range = {
    'Spin0_M550' : '400to800',
    'Spin0_M600' : '400to800',
    'Spin0_M650' : '400to800',
    'Spin0_M700' : '500to900',
    'Spin0_M750' : '500to900',
    'Spin0_M800' : '500to900',
    'Spin0_M850' : '600to1000',
    'Spin0_M900' : '600to1000',
    'Spin0_M1000' : '700to1400',
    'Spin0_M1100' : '700to1400',
    'Spin0_M1200' : '700to1400',
    'Spin2_M550' : '400to800',
    'Spin2_M600' : '400to800',
    'Spin2_M650' : '400to800',
    'Spin2_M700' : '500to900',
    'Spin2_M750' : '500to900',
    'Spin2_M800' : '500to900',
    'Spin2_M850' : '600to1000',
    'Spin2_M900' : '600to1000',
    'Spin2_M1000' : '700to1400',
    'Spin2_M1100' : '700to1400',
    'Spin2_M1200' : '700to1400',
}

signal_to_parameters = {
    #'Spin0_M550' : [[-10,10], [4.0, 20.0], [+0.01, +0.10], [35., 100.]],
    'Spin0_M550' : [[-10,10], [4.0, 20.0], [+0.00, +0.10], [35., 100.]],
    #'Spin0_M600' : [[-13,13], [7.0, 10.0], [+0.01, +0.10], [35., 100.]],
    'Spin0_M600' : [],
    'Spin0_M650' : [],
    'Spin0_M700' : [],
    'Spin0_M750' : [],
    'Spin0_M800' : [],
    'Spin0_M850' : [],
    'Spin0_M900' : [],
    'Spin0_M1000' : [],
    'Spin0_M1100' : [],
    'Spin0_M1200' : [],
    #'Spin2_M550' :  [[-10,10], [4.0, 20.0], [+0.01, +0.10], [35., 100.]],
    'Spin2_M550' :  [[-10,10], [4.0, 20.0], [+0.00, +0.10], [35., 100.]],
    'Spin2_M600' : [[-13,13]],
    'Spin2_M650' : [],
    'Spin2_M700' : [],
    'Spin2_M750' : [],
    'Spin2_M800' : [],
    'Spin2_M850' : [],
    'Spin2_M900' : [],
    'Spin2_M1000' : [],
    'Spin2_M1100' : [],
    'Spin2_M1200' : [],
}

signals_and_ranges=[ ["400to750", "Spin0_M550"], ["400to750","Spin2_M550"], 
                     ["425to800", "Spin0_M600"], ["425to800","Spin2_M600"], 
                     ["450to850", "Spin0_M650"], ["450to850","Spin2_M650"], 
                     ["475to900", "Spin0_M700"], ["475to900","Spin2_M700"], 
                     ["500to950", "Spin0_M750"], ["500to950","Spin2_M750"], 
                     ["525to1000", "Spin0_M800"], ["525to1000","Spin2_M800"], 
                     ["550to1050", "Spin0_M850"], ["550to1050","Spin2_M850"], 
                     ["575to1100", "Spin0_M900"], ["575to1100","Spin2_M900"], 
                     ["625to1200", "Spin0_M1000"], ["625to1200","Spin2_M1000"], 
                     ["675to1300", "Spin0_M1100"], ["675to1300","Spin2_M1100"], 
                     ["725to1400", "Spin0_M1200"], ["725to1400", "Spin2_M1200"] 
                     ]


signals_and_ranges_massComp=[ ["400to1200", "Spin0_M550"], ["400to750","Spin0_M550"], 
                              #["400to1200", "Spin0_M600"], ["425to800","Spin0_M600"], 
                              #["400to1200", "Spin0_M650"], ["450to850","Spin0_M650"], 
                              #["400to1200", "Spin0_M700"], ["475to900","Spin0_M700"], 
                              ["400to1200", "Spin0_M750"], ["500to950","Spin0_M750"], 
                              #["400to1200", "Spin0_M800"], ["525to1000","Spin0_M800"], 
                              #["400to1200", "Spin0_M850"], ["550to1050","Spin0_M850"], 
                              ["400to1200", "Spin0_M900"], ["575to1100","Spin0_M900"], 
                              #["400to1200", "Spin0_M1000"], ["625to1200","Spin0_M1000"], 
                              #["400to1200", "Spin0_M1100"], ["675to1300","Spin0_M1100"], 
                              ["400to1200", "Spin0_M1200"], ["725to1400", "Spin0_M1200"] 
                              ]

use_fixed_ranges = False
use_sliding_edges = True

wait_for_plot = False

if not wait_for_plot:
    ROOT.gROOT.SetBatch(True)

############################################################################################

def get_FWHM(pdf=None, x=ROOT.RooRealVar(), mass=750., mean=0., sigma=0.):
    xmin = mass-500.#x.getMin()
    xmax = mass+250.#x.getMax()
    step = (xmax-xmin)/1000
    xL = -1.
    xH = -1.
    maxval = 0.    
    xatmax = 0.
    for i in xrange(1000):
        x.setVal(step*i+xmin)
        val = pdf.getVal()
        if val>=maxval:
            maxval = val
            xatmax = x.getVal()

    for i in xrange(1000):
        x.setVal(step*i+xmin)
        val = pdf.getVal()
        if val>=maxval/2 and xL<0.:
            xL = x.getVal()
        if val<=maxval/2 and xH<0. and xL>0.:
            xH = x.getVal()
    print pdf.GetName()
    #print ("\tMax at %.1f; FWHM = [%.1f,%.1f] = %.0f" % (xatmax,xL,xH, xH-xL))
    print ("\tMean at %.1f; sigma = %0.f" % (mean,sigma))

############################################################################################

def get_RS_xsec(m=750, ktilde = 0.1):

    xsec = 0.0
    if m==550:
        xsec = 484.26 * 0.0304
    elif m==600:
        xsec = 321.12 * 0.03037
    elif m==650:
        xsec = 219.297 * 0.0303
    elif m==700:
        xsec = 152.216 * 0.030299
    elif m==750:
        xsec = 108.498 * 0.03026
    elif m==800:
        xsec = 78.4962 * 0.03024
    elif m==850:
        xsec = 57.884 * 0.03021
    elif m==900:
        xsec = 43.08 * 0.03019
    elif m==950:
        xsec = 32.697 * 0.03018
    elif m==1000:
        xsec = 24.966 * 0.030165
    elif m==1050:
        xsec = 19.261 * 0.03015
    elif m==1100:
        xsec = 15.04 * 0.03013
    elif m==1150:
        xsec = 11.87 * 0.03012
    elif m==1200:
        xsec = 9.3917 * 0.03011
    else:
        xsec = 0.0

    xsec *= math.pow(ktilde/0.1, 2)
    return xsec

############################################################################################

def get_eff(datacard="", sgn=""):
    f = ROOT.TFile.Open(datacard+".root", "READ")
    w = f.Get("Xbb_workspace")
    n = w.var("buk_pdf_sgn_"+sgn+"_norm").getVal()
    n /= (luminosity*1000)
    f.Close()
    return n

############################################################################################

def run_combine(datacard='', what='limit', params=[], is_blind=True):

    print "Running on datacard:", datacard

    if what=='limit':
        res = []
        if not os.path.exists("higgsCombine"+datacard+".Asymptotic.mH120.root"):
            if is_blind:
                os.system('combine -M Asymptotic --run expected '+datacard+'.txt'+' -n '+datacard)
            else:
                os.system('combine -M Asymptotic '+datacard+'.txt'+' -n '+datacard)
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

    elif what=='fit':
        [rMin,rMax] = [-20,20] if len(params)==0 else params[0]

        # do the S+B fits and B-only fits w/ bias
        command = ('combine -M MaxLikelihoodFit %s.txt --saveWorkspace --rMin %.0f --rMax %.0f ' % (datacard, rMin, rMax) )
        #  --minimizerStrategy 0
        if len(params)>1:
            command += ' --setPhysicsModelParameterRanges '
        (pdf,deg) = ('polydijet' if 'polydijet' in datacard else 'dijet', 2 if 'polydijet' in datacard else 2)
        for ip,p in enumerate(params):
            if ip==0:
                continue
            command += ('a%d_%s_deg%d_0=%.2f,%.2f' % (ip-1, pdf, deg, p[0], p[1]))
            if ip<len(params)-1:
                command += ':'
        print command
        os.system(command+(' -n _%s' % datacard))
        post_combine = ('mv MaxLikelihoodFitResult.root workspace_%s.root' % datacard)
        print post_combine
        os.system(post_combine)

        # do the S+B fits and B-only fits w/ bias
        command = ('combine -M MaxLikelihoodFit %s.txt --saveWorkspace --rMin %.3f --rMax %.3f ' % (datacard, -0.001, 0.001) )
        #  --minimizerStrategy 0
        if len(params)>1:
            command += ' --setPhysicsModelParameterRanges '
        (pdf,deg) = ('polydijet' if 'polydijet' in datacard else 'dijet', 2 if 'polydijet' in datacard else 2)
        for ip,p in enumerate(params):
            if ip==0:
                continue
            command += ('a%d_%s_deg%d_0=%.2f,%.2f' % (ip-1, pdf, deg, p[0], p[1]))
            if ip<len(params)-1:
                command += ':'
        command += (' --freezeNuisanceGroups signal')
        print command
        os.system(command+(' -n _%s_nobias' % datacard))
        post_combine = ('mv MaxLikelihoodFitResult.root workspace_%s_nobias.root' % datacard)
        print post_combine
        os.system(post_combine)

        return []

    else:
        return []


############################################################################################

def make_canvas_limit( results=[], out_name="", save_dir="./plots/Jun09/", is_blind=True, do_acceptance=False, overlay_obs=False, addRS=False):

    c = ROOT.TCanvas("c", "canvas", 600, 600) 
    c.SetLeftMargin(0.13)
    c.SetLogy()
    
    leg = ROOT.TLegend(0.42,0.54,0.88,0.88, "","brNDC")
    if overlay_obs:
        leg.SetHeader("X #rightarrow b#bar{b}, 95% CL upper limits")  
    else:
        if "Spin0" in out_name:
            leg.SetHeader("Spin-0, X #rightarrow b#bar{b}")  
        else:
            leg.SetHeader("Spin-2, X #rightarrow b#bar{b}")  

            
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.035)
    leg.SetFillColor(10)    

    mg = ROOT.TMultiGraph()
    expected = ROOT.TGraphAsymmErrors()
    expected2 = ROOT.TGraphAsymmErrors()
    onesigma = ROOT.TGraphAsymmErrors()
    twosigma = ROOT.TGraphAsymmErrors()
    observed = ROOT.TGraphAsymmErrors()
    observed2 = ROOT.TGraphAsymmErrors()
    theory = ROOT.TGraphAsymmErrors()

    expected.SetLineColor(ROOT.kBlack)
    expected.SetLineStyle(ROOT.kDashed)
    expected.SetLineWidth(2)

    expected2.SetLineColor(ROOT.kBlue)
    expected2.SetLineStyle(ROOT.kDashed)
    expected2.SetLineWidth(2)
    
    onesigma.SetLineWidth(0)
    onesigma.SetFillColor(ROOT.kGreen+1)
    onesigma.SetFillStyle(1001)
    
    twosigma.SetLineWidth(0)
    twosigma.SetFillColor(ROOT.kOrange)
    twosigma.SetFillStyle(1001)

    observed.SetLineColor(ROOT.kBlack)
    observed.SetLineStyle(ROOT.kSolid)
    observed.SetLineWidth(2)
    observed.SetMarkerStyle(ROOT.kFullCircle)
    observed.SetMarkerColor(ROOT.kBlack)

    observed2.SetLineColor(ROOT.kBlue)
    observed2.SetLineStyle(ROOT.kSolid)
    observed2.SetLineWidth(2)
    observed2.SetMarkerStyle(ROOT.kFullSquare)
    observed2.SetMarkerColor(ROOT.kBlue)

    theory.SetLineColor(ROOT.kMagenta)
    theory.SetLineStyle(ROOT.kSolid)
    theory.SetLineWidth(4)

    for ires,res in enumerate(results):
        mass_name = res[0]
        mass_results = res[1]
        accept = res[2]
        imass = float(mass_name.split('_')[-1][1:]) 
        xsec_th = get_RS_xsec(imass, 0.1)
        if do_acceptance:
            xsec_th *= accept
            for ir,r in enumerate(mass_results):
                #print ("%.3f --> %.3f" % (r, r*accept))
                r *= accept
                mass_results[ir] = r

        if not is_blind:
            if overlay_obs:
                if ires < len(results)/2:
                    print "Fill observed ", imass, mass_results[5]
                    observed.SetPoint(ires, imass, mass_results[5])
                else:
                    print "Fill observed2 ", imass, mass_results[5]
                    observed2.SetPoint(ires-len(results)/2, imass, mass_results[5])
                    expected2.SetPoint(ires-len(results)/2, imass, mass_results[2])
                    continue
            else:
                observed.SetPoint(ires, imass, mass_results[5])
                
        expected.SetPoint(ires, imass, mass_results[2])
        onesigma.SetPoint(ires, imass, mass_results[2])
        onesigma.SetPointError(ires, 0.0, 0.0, mass_results[2]-mass_results[1], mass_results[3]-mass_results[2])
        twosigma.SetPoint(ires, imass, mass_results[2])
        twosigma.SetPointError(ires, 0.0, 0.0, mass_results[2]-mass_results[0], mass_results[4]-mass_results[2])
        if addRS:
            theory.SetPoint(ires, imass, xsec_th)

    print "Expected (1)"
    expected.Print()
    print "Observed (1)"
    observed.Print()


    if not is_blind:
        if overlay_obs:        
            if addRS:
                leg.AddEntry(theory, "RS graviton, #tilde{#kappa}=0.1", "L")
            leg.AddEntry(observed, "Observed (spin-0)", "LP")
            leg.AddEntry(expected, "Expected (spin-0)", "L")
            leg.AddEntry(onesigma, "#pm1 std. deviation (spin-0)", "F")
            leg.AddEntry(twosigma, "#pm2 std. deviation (spin-0)", "F")
            leg.AddEntry(observed2, "Observed (spin-2)", "LP")
            leg.AddEntry(expected2, "Expected (spin-2)", "L")
        else:
            if addRS:
                leg.AddEntry(theory, "RS graviton, #tilde{#kappa}=0.1", "L")
            leg.AddEntry(observed, "Observed", "LP")
            leg.AddEntry(expected, "Expected", "L")
            leg.AddEntry(onesigma, "#pm1 std. deviation", "F")
            leg.AddEntry(twosigma, "#pm2 std. deviation", "F")

    mg.Add(twosigma)
    mg.Add(onesigma)
    mg.Add(expected)
    if addRS:
        mg.Add(theory)
    if overlay_obs:
        mg.Add(expected2)
    if not is_blind:
        mg.Add(observed)
        if overlay_obs:
            mg.Add(observed2)

    if do_acceptance: 
        mg.SetMinimum(0.05)
        mg.SetMaximum(10.)
    else:
        mg.SetMinimum(1. if not addRS else 0.5)
        mg.SetMaximum(50. if not addRS else 200)

    mg.Draw("ALP3")

    ROOT.TGaxis.SetMaxDigits(2)
    mg.GetXaxis().SetLabelSize(0.04)
    mg.GetYaxis().SetLabelSize(0.04)
    mg.GetXaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetTitleOffset(1.15)
    mg.GetXaxis().SetTitleOffset(0.85)
    mg.GetXaxis().SetTitle("m_{X} (GeV)")
    if do_acceptance:
        mg.GetYaxis().SetTitle("#sigma #times A #times #epsilon (pb)")
    else:
        mg.GetYaxis().SetTitle("#sigma #times BR(X#rightarrow b#bar{b}) (pb)")

    c.Update()
    pave_lumi = ROOT.TPaveText(0.484,0.89,0.92,0.96, "NDC")
    pave_lumi.SetFillStyle(0);
    pave_lumi.SetBorderSize(0);
    pave_lumi.SetTextAlign(32)
    pave_lumi.SetTextSize(0.04)
    pave_lumi.SetTextFont(42)
    pave_lumi.AddText(("%.2f fb^{-1} (2015)" % luminosity))
    pave_lumi.Draw()

    pave_cms = ROOT.TPaveText(0.16,0.82,0.42,0.89, "NDC")
    pave_cms.SetFillStyle(0);
    pave_cms.SetBorderSize(0);
    pave_cms.SetTextAlign(12)
    pave_cms.SetTextSize(0.05)
    pave_cms.AddText("CMS")
    pave_cms.Draw()

    pave_prel = ROOT.TPaveText(0.16,0.78,0.42,0.82, "NDC")
    pave_prel.SetFillStyle(0);
    pave_prel.SetBorderSize(0);
    pave_prel.SetTextAlign(12)
    pave_prel.SetTextSize(0.04)
    pave_prel.SetTextFont(52)
    pave_prel.AddText("Preliminary")
    pave_prel.Draw()

    leg.Draw()
    c.Modified()
    c.Draw()

    print "Press ENTER to continue"
    if wait_for_plot:
        raw_input()

    save_name = "limit_"+out_name
    if overlay_obs:
        save_name += "_together"

    if is_blind:
        save_name += "_blind"
    if do_acceptance:
        save_name += "_acc"
    if addRS:
        save_name += "_theory"

    for ext in ["png", "pdf"]:
            c.SaveAs(save_dir+"/"+save_name+"."+ext)


############################################################################################

def make_canvas_acceptance( results=[], out_name="", save_dir="./plots/Jun09/"):

    c = ROOT.TCanvas("c", "canvas", 600, 600) 
    c.SetLeftMargin(0.13)
    ROOT.TGaxis.SetMaxDigits(2)
    #c.SetLogy()
    
    leg = ROOT.TLegend(0.60,0.70,1.06,0.88, "","brNDC")
    leg.SetHeader("X #rightarrow b#bar{b}")  
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.04)
    leg.SetFillColor(10)    

    mg = ROOT.TMultiGraph()
    expected = ROOT.TGraphAsymmErrors()
    expected2 = ROOT.TGraphAsymmErrors()

    expected.SetLineColor(ROOT.kRed)
    expected.SetLineStyle(ROOT.kSolid)
    expected.SetLineWidth(4)

    expected2.SetLineColor(ROOT.kBlue)
    expected2.SetLineStyle(ROOT.kDashed)
    expected2.SetLineWidth(4)
    
    for ires,res in enumerate(results):
        mass_name = res[0]
        accept = res[2]*100
        imass = float(mass_name.split('_')[-1][1:]) 
        if ires < len(results)/2:            
            expected.SetPoint(ires, imass, accept)
        else:
            expected2.SetPoint(ires-len(results)/2, imass, accept)

    leg.AddEntry(expected, "Spin-0", "L")
    leg.AddEntry(expected2, "Spin-2", "L")

    mg.Add(expected)
    mg.Add(expected2)

    mg.SetMinimum(0.0)
    mg.SetMaximum(20)

    mg.Draw("ALP3")

    mg.GetXaxis().SetLabelSize(0.04)
    mg.GetYaxis().SetLabelSize(0.04)
    mg.GetXaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetTitleOffset(1.1)
    mg.GetXaxis().SetTitleOffset(0.85)
    mg.GetXaxis().SetTitle("m_{X} (GeV)")
    mg.GetYaxis().SetTitle("A #times #epsilon  (%)")

    c.Update()
    pave_lumi = ROOT.TPaveText(0.485,0.895,0.92,0.956, "NDC")
    pave_lumi.SetFillStyle(0);
    pave_lumi.SetBorderSize(0);
    pave_lumi.SetTextAlign(32)
    pave_lumi.SetTextSize(0.035)
    pave_lumi.AddText(("%.2f fb^{-1} (2015)" % luminosity))
    #pave_lumi.Draw()

    pave_cms = ROOT.TPaveText(0.16,0.82,0.42,0.89, "NDC")
    pave_cms.SetFillStyle(0);
    pave_cms.SetBorderSize(0);
    pave_cms.SetTextAlign(12)
    pave_cms.SetTextSize(0.05)
    pave_cms.AddText("CMS")
    pave_cms.Draw()

    pave_prel = ROOT.TPaveText(0.16,0.78,0.42,0.82, "NDC")
    pave_prel.SetFillStyle(0);
    pave_prel.SetBorderSize(0);
    pave_prel.SetTextAlign(12)
    pave_prel.SetTextSize(0.04)
    pave_prel.SetTextFont(52)
    pave_prel.AddText("Simulation")
    pave_prel.Draw()

    leg.Draw()
    c.Modified()
    c.Draw()

    print "Press ENTER to continue"
    if wait_for_plot:
        raw_input()

    save_name = "acceptance_"+out_name
    for ext in ["png", "pdf"]:
            c.SaveAs(save_dir+"/"+save_name+"."+ext)


############################################################################################

def make_limits(pdf='dijet', spin=0, save_dir="", is_blind=True, do_acceptance=False, overlay_obs=False, addRS=False):

    sgns = []
    for s in [0,2]:
        if not overlay_obs and s!=spin:
            continue
        for m in [550,600,650,700,750,800,850,900,1000,1100,1200]:
            sgns.append( 'Spin'+str(s)+'_M'+str(m) )

   
    tests = []
    results = []
    for cat_btag in ['Had_MT']:
        for cat_kin in ['MinPt100_DH1p6']:        
            for pdf_s in ['buk']:
                for pdf_b in [pdf]:
                    for mass in ['MassFSR']:
                        for sgn in sgns:        
                            if use_fixed_ranges:
                                range_name = signal_to_range[sgn]
                            elif use_sliding_edges:
                                mX = float(sgn.split('_')[-1][1:])
                                edges = get_sliding_edges(mass=mX)
                                range_name = ("%.0fto%.0f" % (edges[0],edges[1]))            
                            if "M550" in sgn:
                                pdf_b = "polydijet"
                            else:
                                pdf_b = pdf
                            tests.append(cat_btag+'_'+cat_kin+'_'+mass+'_'+range_name+'_'+pdf_s+'_'+pdf_b+'_'+sgn)

    print tests
    for itest,test in enumerate(tests):
        res = run_combine("Xbb_workspace_"+test, what='limit', is_blind=is_blind)

        test_split = test.split("_")
        dc_name = "Xbb_workspace_"+test_split[0]
        for t in test_split[1:6]:
            dc_name += ("_"+t)
        eff = get_eff(dc_name, test_split[-2]+"_"+(test_split[-1]).split(".")[0])
        print ("%s ==> %.3f" % (test_split[-2]+"_"+(test_split[-1]).split(".")[0], eff))

        if len(res)>0:
            results.append([test.split('_')[-1],res, eff])
            
    #make_canvas_limit( results=results, out_name=("Spin%d_%s" % (spin,pdf)), save_dir=save_dir, is_blind=is_blind, do_acceptance=do_acceptance, overlay_obs=overlay_obs, addRS=addRS)
    make_canvas_acceptance( results=results, out_name="together", save_dir=save_dir)

############################################################################################

def run_fits(pdf='dijet', spin=0, save_dir=""):

    sgns = ['Spin'+str(spin)+'_M550', 
            'Spin'+str(spin)+'_M600', 
            'Spin'+str(spin)+'_M650', 
            'Spin'+str(spin)+'_M700', 
            'Spin'+str(spin)+'_M750', 'Spin'+str(spin)+'_M800', 'Spin'+str(spin)+'_M850', 'Spin'+str(spin)+'_M900', 'Spin'+str(spin)+'_M1000', 'Spin'+str(spin)+'_M1100', 'Spin'+str(spin)+'_M1200'
            ]
        
    tests = []
    results = []
    for cat_btag in ['Had_MT']:
        for cat_kin in ['MinPt100_DH1p6']:        
            for pdf_s in ['buk']:
                for pdf_b in [pdf]:
                    for mass in ['MassFSR']:
                        for sgn in sgns:        
                            if use_fixed_ranges:
                                range_name = signal_to_range[sgn]
                            elif use_sliding_edges:
                                mX = float(sgn.split('_')[-1][1:])
                                edges = get_sliding_edges(mass=mX)
                                range_name = ("%.0fto%.0f" % (edges[0],edges[1]))            
                            if "M550" in sgn:
                                pdf_b = "polydijet"
                            else:
                                pdf_b = pdf
                            tests.append(cat_btag+'_'+cat_kin+'_'+mass+'_'+range_name+'_'+pdf_s+'_'+pdf_b+'_'+sgn)


    print tests
    for itest,test in enumerate(tests):
        run_combine("Xbb_workspace_"+test, what='fit', params=signal_to_parameters[test.split('_')[-2]+'_'+test.split('_')[-1]], is_blind=False)

############################################################################################

def make_canvas_shapes( in_name="Had_MT_MinPt100_DH1p6", x_name="MassFSR", signals=[ ["425to800","Spin2_M600"] ], sgn_pdf="buk", out_name="", save_dir="../PostPreApproval/"):

    print signals

    c = ROOT.TCanvas("c", "canvas", 600, 600) 
    c.SetLeftMargin(0.13)
    ROOT.TGaxis.SetMaxDigits(2)
    
    #leg = ROOT.TLegend(0.42,0.70,0.88,0.88, "","brNDC")
    leg = ROOT.TLegend(0.50,0.65,1.06,0.88, "","brNDC")
    #leg.SetHeader("X #rightarrow b#bar{b}, m_{X}=%.0f...%.0f GeV" % (float((signals[0][1]).split("_")[-1][1:]),float((signals[-2][1]).split("_")[-1][1:]) ))  
    leg.SetHeader("#splitline{X #rightarrow b#bar{b}}{With FSR-recovery}")  
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.04)
    leg.SetFillColor(10)    

    pdfs = []
    for isgn,sgn in enumerate(signals):
        ws_file = ROOT.TFile.Open(save_dir+"Xbb_workspace_"+in_name+"_"+x_name+"_"+sgn[0]+".root")
        ws = ws_file.Get("Xbb_workspace")
        pdf = ws.pdf(sgn_pdf+"_pdf_sgn_"+sgn[1])
        pdfs.append(pdf)

    print pdfs

    frame1 = ROOT.RooPlot()
    ws_file = ROOT.TFile.Open(save_dir+"Xbb_workspace_"+in_name+"_"+x_name+"_"+signals[0][0]+".root")
    ws = ws_file.Get("Xbb_workspace")
    x = ws.var("x")
    x.setRange(400., 1400.)
    frame1 = x.frame(RooFit.Name("frame1"))
    frame1.SetTitle("")
    frame1.GetYaxis().SetTitle("pdf (1/GeV)")
    frame1.GetXaxis().SetTitle("m_{b#bar{b}} (GeV)")
    frame1.GetYaxis().SetTitleSize(0.05)
    frame1.GetYaxis().SetTitleOffset(1.1)
    frame1.GetXaxis().SetTitleOffset(0.85)
    frame1.GetYaxis().SetLabelSize(0.04)
    frame1.GetXaxis().SetTitleSize(0.05)
    frame1.GetXaxis().SetLabelSize(0.04)    

    for ipdf,pdf in enumerate(pdfs):
        [x_l, x_h] = [ float(signals[ipdf][0][:3]), float(signals[ipdf][0][5:]) ]
        color = ROOT.kRed-ipdf/2 if ipdf%2==0 else ROOT.kBlue-ipdf/2
        style = ROOT.kSolid if ipdf%2==0 else ROOT.kDashed
        pdf.plotOn(frame1, RooFit.LineWidth(3), RooFit.LineColor(color), RooFit.LineStyle(style),RooFit.Name(pdf.GetName()),
                   RooFit.Range(x_l,x_h))
        #leg.AddEntry( frame1.getCurve(pdf.GetName()),("m_{X}=%.0f GeV" % float(signals[ipdf][1].split("_")[-1][1:])) , "L" )
        if ipdf==0:
            leg.AddEntry( frame1.getCurve(pdf.GetName()), "Spin-0"  , "L" )
        elif ipdf==1:
            leg.AddEntry( frame1.getCurve(pdf.GetName()), "Spin-2"  , "L" )

    frame1.SetMaximum(0.095)
    frame1.Draw()        
    leg.Draw()
    pave_lumi = ROOT.TPaveText(0.485,0.895,0.92,0.956, "NDC")
    pave_lumi.SetFillStyle(0);
    pave_lumi.SetBorderSize(0);
    pave_lumi.SetTextAlign(32)
    pave_lumi.SetTextSize(0.035)
    pave_lumi.AddText(("%.2f fb^{-1} (2015)" % luminosity))
    #pave_lumi.Draw()

    pave_cms = ROOT.TPaveText(0.16,0.82,0.42,0.89, "NDC")
    pave_cms.SetFillStyle(0);
    pave_cms.SetBorderSize(0);
    pave_cms.SetTextAlign(12)
    pave_cms.SetTextSize(0.05)
    pave_cms.AddText("CMS")
    pave_cms.Draw()

    pave_prel = ROOT.TPaveText(0.16,0.78,0.42,0.82, "NDC")
    pave_prel.SetFillStyle(0);
    pave_prel.SetBorderSize(0);
    pave_prel.SetTextAlign(12)
    pave_prel.SetTextSize(0.04)
    pave_prel.SetTextFont(52)
    pave_prel.AddText("Simulation")
    pave_prel.Draw()

    print "Press ENTER to continue"
    if wait_for_plot:
        raw_input()

    save_name = "shapes_"+out_name
    for ext in ["png", "pdf"]:
            c.SaveAs(save_dir+"/"+save_name+"."+ext)


############################################################################################

def make_canvas_shapes_massComp( in_name="Had_MT_MinPt100_DH1p6", x_name1="Mass", x_name2="MassFSR" , signals=[ ["425to800","Spin0_M750"] ], sgn_pdf="buk", out_name="", save_dir="../PostPreApproval/"):

    c = ROOT.TCanvas("c", "canvas", 600, 600) 
    c.SetLeftMargin(0.13)
    ROOT.TGaxis.SetMaxDigits(2)
    
    leg = ROOT.TLegend(0.36,0.84,0.85,0.88, "","brNDC")
    leg.SetHeader(("X #rightarrow b#bar{b}, spin-0"))  
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.035)
    leg.SetFillColor(10)    

    leg1 = ROOT.TLegend(0.36,0.65,0.85,0.83, "","brNDC")
    leg1.SetHeader(("Without FSR-recovery"))  
    leg1.SetFillStyle(0)
    leg1.SetBorderSize(0)
    leg1.SetTextSize(0.035)
    leg1.SetFillColor(10)    

    leg2 = ROOT.TLegend(0.36,0.46,0.85,0.64, "","brNDC")
    leg2.SetHeader(("With FSR-recovery"))  
    leg2.SetFillStyle(0)
    leg2.SetBorderSize(0)
    leg2.SetTextSize(0.035)
    leg2.SetFillColor(10)    

    pdfs = []
    means = []
    sigmas = []
    for isgn,sgn in enumerate(signals):
        ws_file = ROOT.TFile.Open(save_dir+"Xbb_workspace_"+in_name+"_"+(x_name1 if isgn%2==0 else x_name2)+"_"+sgn[0]+".root")
        ws = ws_file.Get("Xbb_workspace")
        pdf = ws.pdf(sgn_pdf+"_pdf_sgn_"+sgn[1])
        xi = ws.var("x")
        mean = ws.var("mean_sgn_"+sgn[1]).getVal()
        sigma = ws.var("sigma_sgn_"+sgn[1]).getVal()
        #get_FWHM(pdf=pdf,x=xi,mass=float(sgn[1].split("_")[-1][1:]), mean=mean, sigma=sigma)
        means.append( mean )
        sigmas.append( sigma )
        pdfs.append(pdf)

    print pdfs
    print means
    print sigmas

    frame1 = ROOT.RooPlot()
    ws_file = ROOT.TFile.Open(save_dir+"Xbb_workspace_"+in_name+"_"+x_name1+"_"+signals[0][0]+".root")
    ws = ws_file.Get("Xbb_workspace")
    x = ws.var("x")
    x.setRange(400., 1400.)
    frame1 = x.frame(RooFit.Name("frame1"))
    frame1.SetTitle("")
    frame1.GetYaxis().SetTitle("pdf (1/GeV)")
    frame1.GetXaxis().SetTitle("m_{b#bar{b}} (GeV)")
    frame1.GetYaxis().SetTitleSize(0.05)
    frame1.GetYaxis().SetTitleOffset(1.1)
    frame1.GetXaxis().SetTitleOffset(0.85)
    frame1.GetYaxis().SetLabelSize(0.04)
    frame1.GetXaxis().SetTitleSize(0.05)
    frame1.GetXaxis().SetLabelSize(0.04)    

    for ipdf,pdf in enumerate(pdfs):
        [x_l, x_h] = [ float(signals[(ipdf+1 if ipdf%2==0 else ipdf)][0][:3]), float(signals[(ipdf+1 if ipdf%2==0 else ipdf)][0][5:]) ]
        color = ROOT.kRed-ipdf/2 if ipdf%2==0 else ROOT.kRed-ipdf/2
        style = ROOT.kSolid if ipdf%2==1 else ROOT.kDashed
        pdf.plotOn(frame1, RooFit.LineWidth(3), RooFit.LineColor(color), RooFit.LineStyle(style),RooFit.Name(pdf.GetName()),
                   RooFit.Range(x_l,x_h))
        delta = (sigmas[ipdf]/means[ipdf])*100
        if ipdf%2==0:
            print float(signals[ipdf][1].split("_")[-1][1:])
            print ("\tdelta-mu   : %.3f" % ((means[ipdf+1]-means[ipdf])/means[ipdf]))
            print ("\tdelta-sigma: %.3f" % ((sigmas[ipdf+1]-sigmas[ipdf])/sigmas[ipdf]))

        if ipdf%2==0:
            leg1.AddEntry( frame1.getCurve(pdf.GetName()),
                           ("m_{X}=%s%.0f GeV, #sigma_{m}/#mu_{m}=%.1f%%" % ("" if float(signals[ipdf][1].split("_")[-1][1:])>=1000. else " ", float(signals[ipdf][1].split("_")[-1][1:]), delta  )) , "L" )
        else:
            leg2.AddEntry( frame1.getCurve(pdf.GetName()),
                           ("m_{X}=%s%.0f GeV, #sigma_{m}/#mu_{m}=%.1f%%" % ("" if float(signals[ipdf][1].split("_")[-1][1:])>=1000. else " ", float(signals[ipdf][1].split("_")[-1][1:]), delta  )) , "L" )

    #frame1.SetMaximum(0.105)
    frame1.SetMaximum(0.12)
    frame1.Draw()        
    leg.Draw()
    leg1.Draw()
    leg2.Draw()
    pave_lumi = ROOT.TPaveText(0.485,0.895,0.92,0.956, "NDC")
    pave_lumi.SetFillStyle(0);
    pave_lumi.SetBorderSize(0);
    pave_lumi.SetTextAlign(32)
    pave_lumi.SetTextSize(0.035)
    pave_lumi.AddText(("%.2f fb^{-1} (2015)" % luminosity))
    #pave_lumi.Draw()

    pave_cms = ROOT.TPaveText(0.16,0.82,0.42,0.89, "NDC")
    pave_cms.SetFillStyle(0);
    pave_cms.SetBorderSize(0);
    pave_cms.SetTextAlign(12)
    pave_cms.SetTextSize(0.05)
    pave_cms.AddText("CMS")
    pave_cms.Draw()

    pave_prel = ROOT.TPaveText(0.16,0.78,0.42,0.82, "NDC")
    pave_prel.SetFillStyle(0);
    pave_prel.SetBorderSize(0);
    pave_prel.SetTextAlign(12)
    pave_prel.SetTextSize(0.04)
    pave_prel.SetTextFont(52)
    pave_prel.AddText("Simulation")
    pave_prel.Draw()

    print "Press ENTER to continue"
    if wait_for_plot:
        raw_input()

    save_name = "shapes_"+out_name
    for ext in ["png", "pdf"]:
            c.SaveAs(save_dir+"/"+save_name+"."+ext)

            
############################################################################################

def make_canvas_fit( in_name="Had_MT_MinPt100_DH1p6", x_name="MassFSR", x_range="425to800", sgn="Spin2_M600", bkg_pdf="dijet", out_name="", save_dir="../PostPreApproval/", binWidth=5.0, xsec_vis=100., plot_bands=True, show_chi2=False, plot_2sigmas_only=False):

    c1 = ROOT.TCanvas("c1", "canvas", 600, 600) 
    
    c1.cd()
    pad1 = ROOT.TPad("pad1", "pad1", 0.02, 0.30, 1, 1.0)
    pad1.SetBottomMargin(0.02) 
    pad1.SetLeftMargin(0.13)
    pad1.Draw()      
    pad1.cd()    

    leg = ROOT.TLegend(0.55,(0.48 if plot_bands else (0.55 if not plot_2sigmas_only else 0.52)),0.88,0.88, "","brNDC")
    if "Spin0" in sgn:
        leg.SetHeader(("Spin-0, m_{X}=%.0f GeV" % (float(sgn.split('_')[-1][1:]))))  
    else:
        leg.SetHeader(("Spin-2, m_{X}=%.0f GeV" % (float(sgn.split('_')[-1][1:]))))  
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.05)
    leg.SetFillColor(10)    

    mlfit_file = ROOT.TFile.Open(save_dir+"mlfit_Xbb_workspace_"+in_name+"_"+x_name+"_"+x_range+"_buk_"+bkg_pdf+"_"+sgn+".root")
    mlfit_file_nobias = ROOT.TFile.Open(save_dir+"mlfit_Xbb_workspace_"+in_name+"_"+x_name+"_"+x_range+"_buk_"+bkg_pdf+"_"+sgn+"_nobias.root")

    res_s = mlfit_file.Get("fit_s")    
    res_b = mlfit_file_nobias.Get("fit_b")    

    ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
    ws_file = ROOT.TFile.Open(save_dir+"workspace_Xbb_workspace_"+in_name+"_"+x_name+"_"+x_range+"_buk_"+bkg_pdf+"_"+sgn+".root")
    ws_file_nobias = ROOT.TFile.Open(save_dir+"workspace_Xbb_workspace_"+in_name+"_"+x_name+"_"+x_range+"_buk_"+bkg_pdf+"_"+sgn+"_nobias.root")

    w_s = ws_file.Get("MaxLikelihoodFitResult")
    w_b = ws_file_nobias.Get("MaxLikelihoodFitResult")

    x = w_s.var("x")
    r = w_s.var("r")
    data_obs = w_s.data("data_obs")

    pdf_sgn = w_s.pdf("shapeSig_"+sgn+"_"+in_name)
    pdf_sgn_norm = w_s.var("shapeSig_"+sgn+"_"+in_name+"__norm")
    n_sgn_fit = w_s.obj("n_exp_final_bin"+in_name+"_proc_"+sgn)
    pdf_bkg = w_s.pdf("shapeBkg_bkg_"+in_name)
    n_bkg_fit = w_s.obj("n_exp_final_bin"+in_name+"_proc_bkg")
    pdf_bkg_b = w_b.pdf("shapeBkg_bkg_"+in_name)
    n_bkg_fit_b = res_b.floatParsFinal().find("shapeBkg_bkg_"+in_name+"__norm")
    
    n_sgn = ROOT.RooRealVar("n_sgn", "", n_sgn_fit.getVal())
    n_bkg = ROOT.RooRealVar("n_bkg", "", n_bkg_fit.getVal())
    n_bkg_b = ROOT.RooRealVar("n_bkg", "", n_bkg_fit_b.getVal())

    pdf_comb_ext = ROOT.RooAddPdf("pdf_comb_ext","", ROOT.RooArgList(pdf_sgn,pdf_bkg),  ROOT.RooArgList(n_sgn,n_bkg))

    new_binning = int(( "%.0f" % ((x.getMax()-x.getMin())/binWidth)))    
    h_rebinned = data_obs.createHistogram("h_data_obs_rebinned", x, RooFit.Binning( new_binning , x.getMin(), x.getMax()) )
    data_rebinned = ROOT.RooDataHist("data_obs_rebinned","", ROOT.RooArgList(x), h_rebinned, 1.0)
    
    frame1 = x.frame(RooFit.Name("frame1"))
    frame1.SetTitle("")
    frame1.GetYaxis().SetTitle(("Events / %.1f GeV" % h_rebinned.GetBinWidth(1)))
    frame1.GetYaxis().SetTitleSize(24)
    frame1.GetYaxis().SetTitleFont(43)
    frame1.GetYaxis().SetTitleOffset(1.18)
    frame1.GetYaxis().SetLabelFont(43) 
    frame1.GetYaxis().SetLabelSize(20)
    frame1.GetXaxis().SetTitleSize(0)
    frame1.GetXaxis().SetTitleFont(43)
    frame1.GetXaxis().SetLabelFont(43)
    frame1.GetXaxis().SetLabelSize(0)
    #ROOT.TGaxis.SetMaxDigits(2)

    hdummy = ROOT.TH1F("hdummy", "", h_rebinned.GetNbinsX(), h_rebinned.GetXaxis().GetXmin(), h_rebinned.GetXaxis().GetXmax())

    hbkg = ROOT.TH1F("hbkg", "", h_rebinned.GetNbinsX(), h_rebinned.GetXaxis().GetXmin(), h_rebinned.GetXaxis().GetXmax())
    hbkg.SetFillColor(ROOT.kAzure+1)
    hbkg.SetLineColor(ROOT.kAzure+1)
    hbkg.SetLineWidth(0)
    hbkg.SetFillStyle(3001)

    h1sigmaU = ROOT.TH1F("h1sigmaU", "", h_rebinned.GetNbinsX(), h_rebinned.GetXaxis().GetXmin(), h_rebinned.GetXaxis().GetXmax())
    h1sigmaU.SetFillColor(ROOT.kGreen+1)
    h1sigmaU.SetFillStyle(1001)

    h1sigmaD = ROOT.TH1F("h1sigmaD", "", h_rebinned.GetNbinsX(), h_rebinned.GetXaxis().GetXmin(), h_rebinned.GetXaxis().GetXmax())
    h1sigmaD.SetFillColor(ROOT.kGreen+1)
    h1sigmaD.SetFillStyle(1001)

    h2sigmaU = ROOT.TH1F("h2sigmaU", "", h_rebinned.GetNbinsX(), h_rebinned.GetXaxis().GetXmin(), h_rebinned.GetXaxis().GetXmax())
    h2sigmaU.SetFillColor(ROOT.kOrange)
    h2sigmaU.SetFillStyle(1001)

    h2sigmaD = ROOT.TH1F("h2sigmaD", "", h_rebinned.GetNbinsX(), h_rebinned.GetXaxis().GetXmin(), h_rebinned.GetXaxis().GetXmax())
    h2sigmaD.SetFillColor(ROOT.kOrange)
    h2sigmaD.SetFillStyle(1001)

    print "START plotting"
    print "\tPlot data_obs..."
    data_rebinned.plotOn(frame1, RooFit.Name("data_obs"))
    print "\tPlot bkg +/- 2 sigma..."
    pdf_bkg_b.plotOn(frame1, 
                     RooFit.VisualizeError(res_b, 2, ROOT.kTRUE), 
                     RooFit.LineColor(ROOT.kBlue), 
                     RooFit.LineStyle(ROOT.kSolid), 
                     RooFit.FillColor(ROOT.kOrange), RooFit.Name(pdf_bkg_b.GetName()+"_2sigma"), RooFit.Normalization(n_bkg_b.getVal() , ROOT.RooAbsReal.NumEvent), RooFit.MoveToBack() )
    print "\tPlot bkg +/- 1 sigma..."
    pdf_bkg_b.plotOn(frame1, 
                     RooFit.VisualizeError(res_b, 1, ROOT.kTRUE), 
                     RooFit.LineColor(ROOT.kBlue), 
                     RooFit.LineStyle(ROOT.kSolid), 
                     RooFit.FillColor(ROOT.kGreen+1), RooFit.Name(pdf_bkg_b.GetName()+"_1sigma") , RooFit.Normalization(n_bkg_b.getVal() , ROOT.RooAbsReal.NumEvent) )
    print "\tPlot bkg..."
    pdf_bkg_b.plotOn(frame1, RooFit.LineWidth(3), RooFit.LineColor(ROOT.kBlue), RooFit.LineStyle(ROOT.kSolid), 
                     RooFit.Name(pdf_bkg_b.GetName()), RooFit.Normalization(n_bkg_b.getVal() , ROOT.RooAbsReal.NumEvent) )
    print "\tPlot sgn+bkg..."
    pdf_comb_ext.plotOn(frame1, RooFit.LineWidth(3), RooFit.LineColor(ROOT.kRed), RooFit.LineStyle(ROOT.kDashed), RooFit.Name(pdf_comb_ext.GetName()) )
    print "\tPlot sgn..."
    pdf_sgn.plotOn(frame1, RooFit.LineWidth(3), RooFit.LineColor(46), RooFit.LineStyle(ROOT.kDotted), 
                   RooFit.Name(pdf_sgn.GetName()), RooFit.Normalization(pdf_sgn_norm.getVal()*xsec_vis , ROOT.RooAbsReal.NumEvent) )

    print "\tPlot data_obs..."
    data_rebinned.plotOn(frame1, RooFit.Name("data_obs"))
    print "END plotting"
    chi2_s = frame1.chiSquare(pdf_comb_ext.GetName(), "data_obs", 2+1 if bkg_pdf=='dijet' else 3+1 )
    chi2_b = frame1.chiSquare(pdf_bkg_b.GetName(), "data_obs", 2 if bkg_pdf=='dijet' else 3 )
    ndof = (data_rebinned.numEntries()-(2 if bkg_pdf=='dijet' else 3))
    print ROOT.TMath.Prob(chi2_b*ndof, ndof)
    leg.AddEntry(frame1.findObject("data_obs"), "Data", "PE")
    if show_chi2:
        leg.AddEntry(frame1.getCurve(pdf_bkg_b.GetName()),  ("Bkg. (#chi^{2}=%.2f)" % chi2_b), "L")
    else:
        leg.AddEntry(frame1.getCurve(pdf_bkg_b.GetName()),  ("Bkg."), "L")
    if plot_bands:
        leg.AddEntry(h1sigmaU, "#pm1 std. deviation", "F")
        leg.AddEntry(h2sigmaU, "#pm2 std. deviation", "F")
    elif plot_2sigmas_only:
        leg.AddEntry(h2sigmaU, "#pm2 std. deviation", "F")
        
    leg.AddEntry(frame1.getCurve(pdf_comb_ext.GetName()), ("Bkg. + signal"), "L")
    leg.AddEntry(frame1.getCurve(pdf_sgn.GetName()), ("Signal, #sigma=%.0f pb" % xsec_vis ), "L")
    frame1.SetMaximum( h_rebinned.GetMaximum()*2.0 )
    frame1.SetMinimum( h_rebinned.GetMinimum()*0.8 )
    pad1.SetLogy()
    print "Drawing frame1..."
    frame1.Draw()

    pave_lumi = ROOT.TPaveText(0.484,0.91,0.92,0.96, "NDC")
    pave_lumi.SetFillStyle(0);
    pave_lumi.SetBorderSize(0);
    pave_lumi.SetTextAlign(32)
    pave_lumi.SetTextSize(0.05)
    pave_lumi.SetTextFont(42)
    pave_lumi.AddText(("%.2f fb^{-1} (2015)" % luminosity))
    pave_lumi.Draw()

    pave_cms = ROOT.TPaveText(0.16,0.82,0.42,0.89, "NDC")
    pave_cms.SetFillStyle(0);
    pave_cms.SetBorderSize(0);
    pave_cms.SetTextAlign(12)
    pave_cms.SetTextSize(0.06)
    pave_cms.AddText("CMS")
    pave_cms.Draw()

    pave_prel = ROOT.TPaveText(0.16,0.76,0.42,0.82, "NDC")
    pave_prel.SetFillStyle(0);
    pave_prel.SetBorderSize(0);
    pave_prel.SetTextAlign(12)
    pave_prel.SetTextSize(0.05)
    pave_prel.SetTextFont(52)
    pave_prel.AddText("Preliminary")
    pave_prel.Draw()

    leg.Draw()
    c1.Modified()

    c1.cd()
    pad2 = ROOT.TPad("pad2", "pad2", 0.02, 0.02, 1, 0.28)
    pad2.SetTopMargin(0.02)
    pad2.SetLeftMargin(0.13)
    pad2.SetBottomMargin(0.35)
    pad2.SetGridx()   
    pad2.SetGridy() 
    pad2.Draw()
    pad2.cd()       
    frame2 = x.frame(RooFit.Name("frame2"))
    frame2.SetTitle("")
    frame2.GetYaxis().CenterTitle()
    if plot_bands: 
        frame2.GetYaxis().SetTitle("#frac{Data-Bkg.}{#sqrt{Bkg.}}")
    else:
         frame2.GetYaxis().SetTitle("#frac{Data-Bkg.}{#sigma_{Bkg.}}")
    frame2.GetYaxis().SetNdivisions(505)
    frame2.GetYaxis().SetTitleSize(24)
    frame2.GetYaxis().SetTitleFont(43)
    frame2.GetYaxis().SetTitleOffset(1.18)
    frame2.GetYaxis().SetLabelFont(43) 
    frame2.GetYaxis().SetLabelSize(20)
    frame2.GetXaxis().SetTitle("m_{b#bar{b}} (GeV)")
    frame2.GetXaxis().SetTitleSize(25)
    frame2.GetXaxis().SetTitleFont(43)
    frame2.GetXaxis().SetTitleOffset(3.5)
    frame2.GetXaxis().SetLabelFont(43) 
    frame2.GetXaxis().SetLabelSize(20)            
    hresid = frame1.pullHist("data_obs", pdf_bkg_b.GetName())
    hresid.GetYaxis().SetRangeUser(-4,4)

    sigma2 = frame1.getCurve(pdf_bkg_b.GetName()+"_2sigma")
    sigma1 = frame1.getCurve(pdf_bkg_b.GetName()+"_1sigma")
    nominal = frame1.getCurve(pdf_bkg_b.GetName())
    nominalX = nominal.GetX()
    nominalY = nominal.GetY()
    n1sigmaY = sigma1.GetY()
    n2sigmaY = sigma2.GetY()
    for i in xrange(nominal.GetN()): 
        x_i = nominalX[i]
        n_i = nominalY[i]
        n_1up_i = n1sigmaY[2*nominal.GetN()-i-1]
        n_1down_i = n1sigmaY[i]
        n_2up_i = n2sigmaY[2*nominal.GetN()-i-1]
        n_2down_i = n2sigmaY[i]
        bin_i = h1sigmaU.FindBin( x_i )
        if bin_i<=0 or bin_i>h1sigmaU.GetNbinsX(): 
            continue
        bin_width_i = h_rebinned.GetBinWidth( bin_i )
        n_data_i = h_rebinned.GetBinContent( bin_i )
        #h1sigmaU.SetBinContent( bin_i, (-n_i+n_1up_i)/math.sqrt( n_data_i ) )
        #h1sigmaD.SetBinContent( bin_i, (-n_i+n_1down_i)/math.sqrt( n_data_i ) )
        #h2sigmaU.SetBinContent( bin_i, (-n_i+n_2up_i)/math.sqrt( n_data_i ) )
        #h2sigmaD.SetBinContent( bin_i, (-n_i+n_2down_i)/math.sqrt( n_data_i ) )
        h1sigmaU.SetBinContent( bin_i, (-n_i+n_1up_i))
        h1sigmaD.SetBinContent( bin_i, (-n_i+n_1down_i))
        h2sigmaU.SetBinContent( bin_i, (-n_i+n_2up_i))
        h2sigmaD.SetBinContent( bin_i, (-n_i+n_2down_i))

    # redefine pulls here:
    bkg_int = pdf_bkg_b.createIntegral(ROOT.RooArgSet(x), "MassFSR").getVal()
    for bin_i in range(1,h_rebinned.GetNbinsX()+1):
        n_data_i = h_rebinned.GetBinContent( bin_i )
        x.setRange(("Bin%d" % bin_i), h_rebinned.GetBinLowEdge(bin_i), h_rebinned.GetBinLowEdge(bin_i)+bin_width_i)
        bkg_int_i = pdf_bkg_b.createIntegral(ROOT.RooArgSet(x), ("Bin%d" % bin_i)).getVal() / bkg_int * n_bkg_fit_b.getVal()
        pull_i = (n_data_i-bkg_int_i)/math.sqrt(bkg_int_i)
        if not plot_bands:
            new_err_i = math.sqrt(bkg_int_i + math.pow(h1sigmaU.GetBinContent( bin_i ),2))
            pull_i *= (math.sqrt(bkg_int_i)/new_err_i)
            print ("Error: %.3f --> %.3f" % (math.sqrt(bkg_int_i), new_err_i ))
        print ("Data: %d ---- Bkg: %.1f" % (n_data_i,bkg_int_i))
        hbkg.SetBinContent( bin_i, pull_i)
        hbkg.SetBinError( bin_i, 0.)
        hdummy.SetBinContent( bin_i, 0.)
        hdummy.SetBinError( bin_i, 0.)        
        h1sigmaU.SetBinContent( bin_i, h1sigmaU.GetBinContent( bin_i )/math.sqrt( bkg_int_i ) )
        h1sigmaD.SetBinContent( bin_i, h1sigmaD.GetBinContent( bin_i )/math.sqrt( bkg_int_i ) )
        h2sigmaU.SetBinContent( bin_i, h2sigmaU.GetBinContent( bin_i )/math.sqrt( bkg_int_i ) )
        h2sigmaD.SetBinContent( bin_i, h2sigmaD.GetBinContent( bin_i )/math.sqrt( bkg_int_i ) )
        
    if plot_bands:
        frame2.addTH1(h2sigmaU, "HIST")
        frame2.addTH1(h2sigmaD, "HIST")
        frame2.addTH1(h1sigmaU, "HIST")
        frame2.addTH1(h1sigmaD, "HIST")
    frame2.addTH1(hbkg, "HIST")
    frame2.addTH1(hdummy, "HIST")
    #frame2.addPlotable(hresid,"pE1")

    print "Drawing frame2..."
    frame2.Draw()
    frame2.GetYaxis().SetRangeUser(-4,4)    

    if not plot_bands:
        frame1.remove(pdf_bkg_b.GetName()+"_1sigma", ROOT.kFALSE)
        if not plot_2sigmas_only:
            frame1.remove(pdf_bkg_b.GetName()+"_2sigma", ROOT.kFALSE)
        pad1.cd()
        frame1.Draw()
        pave_lumi.Draw()
        pave_cms.Draw()
        pave_prel.Draw()
        leg.Draw()

    ROOT.TGaxis.SetMaxDigits(2)
    print "Drawing canvas..."
    c1.cd()
    c1.Draw()

    print "Press ENTER to continue"
    if wait_for_plot:
        raw_input()

    for ext in ["png", "pdf"]:
        c1.SaveAs("plot_"+in_name+"_"+"MassFSR"+"_"+sgn+out_name+"."+ext)

    ROOT.gDirectory.Remove(h1sigmaU)
    ROOT.gDirectory.Remove(h1sigmaD)
    ROOT.gDirectory.Remove(h2sigmaU)
    ROOT.gDirectory.Remove(h2sigmaD)
    ROOT.gDirectory.Remove(hbkg)
    ROOT.gDirectory.Remove(hdummy)
    ROOT.gDirectory.Remove(c1)
    ws_file.Close()
    mlfit_file.Close()
    ws_file_nobias.Close()
    mlfit_file_nobias.Close()

############################################################################################

def make_fits(spin=0, pdf='dijet', save_dir=""):

    sgns = ['Spin'+str(spin)+'_M550', 
            'Spin'+str(spin)+'_M600', 
            'Spin'+str(spin)+'_M650', 
            'Spin'+str(spin)+'_M700', 
            'Spin'+str(spin)+'_M750', 'Spin'+str(spin)+'_M800', 'Spin'+str(spin)+'_M850', 'Spin'+str(spin)+'_M900', 'Spin'+str(spin)+'_M1000', 'Spin'+str(spin)+'_M1100', 
        'Spin'+str(spin)+'_M1200'
            ]
        
    sgn_to_binWidth = {
        '550' : 12.5,
        '600' : 12.5,
        '650' : 12.5,
        '700' : 12.5,
        '750' : 12.5,
        '800' : 12.5,
        '850' : 12.5,
        '900' : 12.5,
        '1000' : 12.5,
        '1100' : 12.5,
        '1200' : 12.5,
    }

    sgn_to_xsec_vis = {
        '550' : 200,
        '600' : 150,
        '650' : 100,
        '700' : 75,
        '750' : 50,
        '800' : 50,
        '850' : 30,
        '900' : 30,
        '1000' : 20,
        '1100' : 15,
        '1200' : 10,
    }



    tests = []
    results = []
    for cat_btag in ['Had_MT']:
        for cat_kin in ['MinPt100_DH1p6']:        
            for pdf_s in ['buk']:
                for pdf_b in [pdf]:
                    for mass in ['MassFSR']:
                        for sgn in sgns:        
                            mX = float(sgn.split('_')[-1][1:])
                            if use_fixed_ranges:
                                range_name = signal_to_range[sgn]
                            elif use_sliding_edges:
                                edges = get_sliding_edges(mass=mX)
                                range_name = ("%.0fto%.0f" % (edges[0],edges[1]))            
                            if "M550" in sgn:
                                pdf_b = "polydijet"
                            else:
                                pdf_b = pdf
                            make_canvas_fit( in_name=cat_btag+"_"+cat_kin, x_name=mass, x_range=range_name, sgn=sgn, bkg_pdf=pdf_b, out_name="", save_dir=save_dir, binWidth=sgn_to_binWidth[("%.0f" % mX)], xsec_vis=sgn_to_xsec_vis[("%.0f" % mX)], plot_bands=False, plot_2sigmas_only=True)

############################################################################################

for spin in [0]:
    #run_fits(pdf='dijet', spin=spin, save_dir="../PostPreApproval/")                            
    #make_fits(spin=spin, pdf='dijet', save_dir="../PostPreApproval/")
    print "make_fits() for spin", spin

for spin in [0]:
    for is_blind in [False]:
        for do_acceptance in [False]:
            for overlay_obs in [True]:
                for addRS in [True]:
                    make_limits(pdf="dijet", spin=spin, save_dir="../PostPreApproval/", is_blind=is_blind, do_acceptance=do_acceptance, overlay_obs=overlay_obs, addRS=addRS)
                    print "make_limits() for spin", spin

#make_canvas_shapes( in_name="Had_MT_MinPt100_DH1p6", x_name="MassFSR", signals=signals_and_ranges, sgn_pdf="buk", out_name="", save_dir="../PostPreApproval/")
#make_canvas_shapes_massComp( in_name="Had_MT_MinPt100_DH1p6", x_name1="Mass", x_name2="MassFSR", signals=signals_and_ranges_massComp, sgn_pdf="buk", out_name="MassVsMassFSR", save_dir="../PostPreApproval/")
