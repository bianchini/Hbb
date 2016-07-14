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
    'Spin0_M550' : [],
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
    'Spin2_M550' :  [[-10,10], [4.0, 20.0], [+0.01, +0.10], [35., 100.]],
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

use_fixed_ranges = False
use_sliding_edges = True

wait_for_plot = False

############################################################################################

def get_eff(datacard="", sgn=""):
    f = ROOT.TFile.Open(datacard+".root", "READ")
    w = f.Get("Xbb_workspace")
    n = w.var("buk_pdf_sgn_"+sgn+"_norm").getVal()
    n /= 2630.
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
        command = ('combine -M MaxLikelihoodFit %s.txt --saveWorkspace --rMin %.0f --rMax %.0f' % (datacard, rMin, rMax) )
        if len(params)>1:
            command += ' --setPhysicsModelParameterRanges '
        (pdf,deg) = ('polydijet' if 'polydijet' in datacard else 'dijet', 2 if 'polydijet' in datacard else 2)
        for ip,p in enumerate(params):
            if ip==0:
                continue
            command += ('a%d_%s_deg%d_0=%.2f,%.2f' % (ip, pdf, deg, p[0], p[1]))
            if ip<len(params)-1:
                command += ':'
        print command
        os.system(command+(' -n _%s' % datacard))
        post_combine = ('mv MaxLikelihoodFitResult.root workspace_%s.root' % datacard)
        print post_combine
        os.system(post_combine)

        # do the S+B fits and B-only fits w/ bias
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

def make_canvas( results=[], out_name="", save_dir="./plots/Jun09/", is_blind=True, do_acceptance=False):

    c = ROOT.TCanvas("c", "canvas", 600, 600) 
    c.SetLogy()
    
    leg = ROOT.TLegend(0.55,0.65,0.85,0.88, "","brNDC")
    if "Spin0" in out_name:
        leg.SetHeader("gg #rightarrow X(0^{+}) #rightarrow b#bar{b}")  
    else:
        leg.SetHeader("gg/q#bar{q} #rightarrow X(2^{+}) #rightarrow b#bar{b}")  
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.04)
    leg.SetFillColor(10)    

    mg = ROOT.TMultiGraph()
    expected = ROOT.TGraphAsymmErrors()
    onesigma = ROOT.TGraphAsymmErrors()
    twosigma = ROOT.TGraphAsymmErrors()
    observed = ROOT.TGraphAsymmErrors()

    expected.SetLineColor(ROOT.kBlack)
    expected.SetLineStyle(ROOT.kSolid)
    expected.SetLineWidth(2)
    
    onesigma.SetLineWidth(0)
    onesigma.SetFillColor(ROOT.kGreen)
    onesigma.SetFillStyle(1001)
    
    twosigma.SetLineWidth(0)
    twosigma.SetFillColor(ROOT.kYellow)
    twosigma.SetFillStyle(1001)

    observed.SetLineColor(ROOT.kBlack)
    observed.SetLineStyle(ROOT.kSolid)
    observed.SetLineWidth(2)
    observed.SetMarkerStyle(ROOT.kFullCircle)
    observed.SetMarkerColor(ROOT.kBlack)

    for ires,res in enumerate(results):
        mass_name = res[0]
        mass_results = res[1]
        accept = res[2]
        if do_acceptance:
            for ir,r in enumerate(mass_results):
                #print ("%.3f --> %.3f" % (r, r*accept))
                r *= accept
                mass_results[ir] = r

        imass = float(mass_name.split('_')[-1][1:]) 
        expected.SetPoint(ires, imass, mass_results[2])
        onesigma.SetPoint(ires, imass, mass_results[2])
        onesigma.SetPointError(ires, 0.0, 0.0, mass_results[2]-mass_results[1], mass_results[3]-mass_results[2])
        twosigma.SetPoint(ires, imass, mass_results[2])
        twosigma.SetPointError(ires, 0.0, 0.0, mass_results[2]-mass_results[0], mass_results[4]-mass_results[2])
        if not is_blind:
            observed.SetPoint(ires, imass, mass_results[5])

    expected.Print("")
    onesigma.Print("")
    twosigma.Print("")

    if not is_blind:
        leg.AddEntry(observed, "Observed", "LP")
    leg.AddEntry(expected, "Expected", "L")
    leg.AddEntry(onesigma, "Expected (68%)", "F")
    leg.AddEntry(twosigma, "Expected (95%)", "F")

    mg.Add(twosigma)
    mg.Add(onesigma)
    mg.Add(expected)
    if not is_blind:
        mg.Add(observed)

    if do_acceptance: 
        mg.SetMinimum(0.01)
        mg.SetMaximum(10.)
    else:
        mg.SetMinimum(1.)
        mg.SetMaximum(25.)

    mg.Draw("ALP3")

    mg.GetXaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetTitleOffset(0.85)
    mg.GetXaxis().SetTitleOffset(0.85)
    mg.GetXaxis().SetTitle("m_{X} (GeV)")
    if do_acceptance:
        mg.GetYaxis().SetTitle("95% CL limit on #sigma #times A #times #epsilon (pb)")
    else:
        mg.GetYaxis().SetTitle("95% CL limit on #sigma #times BR(X#rightarrow b#bar{b}) (pb)")

    c.Update()
    pave_lumi = ROOT.TPaveText(0.46,0.90,0.90,0.96, "NDC")
    pave_lumi.SetFillStyle(0);
    pave_lumi.SetBorderSize(0);
    pave_lumi.SetTextAlign(32)
    pave_lumi.SetTextSize(0.035)
    pave_lumi.AddText(("%.2f fb^{-1} (2015)" % luminosity))

    pave_lumi.Draw()
    pave_cms = ROOT.TPaveText(0.09,0.90,0.40,0.96, "NDC")
    pave_cms.SetFillStyle(0);
    pave_cms.SetBorderSize(0);
    pave_cms.SetTextAlign(12)
    pave_cms.SetTextSize(0.035)
    pave_cms.AddText("CMS preliminary")
    pave_cms.Draw()
    leg.Draw()
    c.Modified()

    if wait_for_plot:
        raw_input()

    save_name = "limit_"+out_name
    if is_blind:
        save_name += "_blind"
    if do_acceptance:
        save_name += "_acc"

    for ext in ["png", "pdf"]:
            c.SaveAs(save_dir+"/"+save_name+"."+ext)

############################################################################################

def make_limit_plot(pdf='dijet', spin=0, save_dir="", is_blind=True, do_acceptance=False):

    sgns = ['Spin'+str(spin)+'_M550', 'Spin'+str(spin)+'_M600', 'Spin'+str(spin)+'_M650', 'Spin'+str(spin)+'_M700', 'Spin'+str(spin)+'_M750', 'Spin'+str(spin)+'_M800', 'Spin'+str(spin)+'_M850', 'Spin'+str(spin)+'_M900', 'Spin'+str(spin)+'_M1000', 'Spin'+str(spin)+'_M1100', 'Spin'+str(spin)+'_M1200']
        
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
            
    make_canvas( results=results, out_name=("Spin%d_%s" % (spin,pdf)), save_dir=save_dir, is_blind=is_blind, do_acceptance=do_acceptance)

############################################################################################

def make_fits(pdf='dijet', spin=0, save_dir=""):

    sgns = [#'Spin'+str(spin)+'_M550', 
            'Spin'+str(spin)+'_M600', 
            #'Spin'+str(spin)+'_M650', 'Spin'+str(spin)+'_M700', 'Spin'+str(spin)+'_M750', 'Spin'+str(spin)+'_M800', 'Spin'+str(spin)+'_M850', 'Spin'+str(spin)+'_M900', 'Spin'+str(spin)+'_M1000', 'Spin'+str(spin)+'_M1100', 'Spin'+str(spin)+'_M1200'
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

def make_fit_plot( in_name="Had_MT_MinPt100_DH1p6", x_name="MassFSR", x_range="425to800", sgn="Spin2_M600", bkg_pdf="dijet", out_name="", save_dir="../PostPreApproval/", binWidth=5.0, xsec_vis=100., plot_bands=True):

    c1 = ROOT.TCanvas("c1", "canvas", 600, 600) 
    
    c1.cd()
    pad1 = ROOT.TPad("pad1", "pad1", 0.02, 0.30, 1, 1.0)
    pad1.SetBottomMargin(0.02) 
    pad1.SetLeftMargin(0.13)
    pad1.Draw()      
    pad1.cd()    

    leg = ROOT.TLegend(0.50,0.48,0.85,0.88, "","brNDC")
    if "Spin0" in sgn:
        leg.SetHeader(("Spin-0, m_{X}=%.0f GeV" % (float(sgn.split('_')[-1][1:]))))  
    else:
        leg.SetHeader(("Spin-2, m_{X}=%.0f GeV" % (float(sgn.split('_')[-1][1:]))))  
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.06)
    leg.SetFillColor(10)    

    mlfit_file = ROOT.TFile.Open("mlfit_Xbb_workspace_"+in_name+"_"+x_name+"_"+x_range+"_buk_"+bkg_pdf+"_"+sgn+".root")
    mlfit_file_nobias = ROOT.TFile.Open("mlfit_Xbb_workspace_"+in_name+"_"+x_name+"_"+x_range+"_buk_"+bkg_pdf+"_"+sgn+"_nobias.root")

    res_s = mlfit_file.Get("fit_s")    
    res_b = mlfit_file_nobias.Get("fit_b")    

    ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
    ws_file = ROOT.TFile.Open("workspace_Xbb_workspace_"+in_name+"_"+x_name+"_"+x_range+"_buk_"+bkg_pdf+"_"+sgn+".root")
    ws_file_nobias = ROOT.TFile.Open("workspace_Xbb_workspace_"+in_name+"_"+x_name+"_"+x_range+"_buk_"+bkg_pdf+"_"+sgn+"_nobias.root")

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
    n_bkg_fit_b = w_b.obj("n_exp_final_bin"+in_name+"_proc_bkg")
    
    n_sgn = ROOT.RooRealVar("n_sgn", "", n_sgn_fit.getVal())
    n_bkg = ROOT.RooRealVar("n_bkg", "", n_bkg_fit.getVal())
    n_bkg_b = ROOT.RooRealVar("n_bkg", "", n_bkg_fit_b.getVal())

    pdf_comb_ext = ROOT.RooAddPdf("pdf_comb_ext","", ROOT.RooArgList(pdf_sgn,pdf_bkg),  ROOT.RooArgList(n_sgn,n_bkg))

    h_rebinned = data_obs.createHistogram("h_data_obs_rebinned", x, RooFit.Binning( int((x.getMax()-x.getMin())/binWidth) , x.getMin(), x.getMax()) )
    data_rebinned = ROOT.RooDataHist("data_obs_rebinned","", ROOT.RooArgList(x), h_rebinned, 1.0)
    
    frame1 = x.frame(RooFit.Name("frame1"))
    frame1.SetTitle("")
    frame1.GetYaxis().SetTitle(("Events / %.1f GeV" % binWidth))
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

    h1sigmaU = ROOT.TH1F("h1sigmaU", "", h_rebinned.GetNbinsX(), h_rebinned.GetXaxis().GetXmin(), h_rebinned.GetXaxis().GetXmax())
    h1sigmaU.SetFillColor(ROOT.kGreen)
    h1sigmaU.SetFillStyle(1001)

    h1sigmaD = ROOT.TH1F("h1sigmaD", "", h_rebinned.GetNbinsX(), h_rebinned.GetXaxis().GetXmin(), h_rebinned.GetXaxis().GetXmax())
    h1sigmaD.SetFillColor(ROOT.kGreen)
    h1sigmaD.SetFillStyle(1001)

    h2sigmaU = ROOT.TH1F("h2sigmaU", "", h_rebinned.GetNbinsX(), h_rebinned.GetXaxis().GetXmin(), h_rebinned.GetXaxis().GetXmax())
    h2sigmaU.SetFillColor(ROOT.kYellow)
    h2sigmaU.SetFillStyle(1001)

    h2sigmaD = ROOT.TH1F("h2sigmaD", "", h_rebinned.GetNbinsX(), h_rebinned.GetXaxis().GetXmin(), h_rebinned.GetXaxis().GetXmax())
    h2sigmaD.SetFillColor(ROOT.kYellow)
    h2sigmaD.SetFillStyle(1001)

    print "START plotting"
    print "\tPlot data_obs..."
    data_rebinned.plotOn(frame1, RooFit.Name("data_obs"))
    if plot_bands:
        print "\tPlot bkg +/- 2 sigma..."
        pdf_bkg_b.plotOn(frame1, 
                         RooFit.VisualizeError(res_b, 2, ROOT.kTRUE), 
                         RooFit.LineColor(ROOT.kBlue), 
                         RooFit.LineStyle(ROOT.kSolid), 
                         RooFit.FillColor(ROOT.kYellow), RooFit.Name(pdf_bkg_b.GetName()+"_2sigma"), RooFit.Normalization(n_bkg_b.getVal() , ROOT.RooAbsReal.NumEvent), RooFit.MoveToBack() )
        print "\tPlot bkg +/- 1 sigma..."
        pdf_bkg_b.plotOn(frame1, 
                         RooFit.VisualizeError(res_b, 1, ROOT.kTRUE), 
                         RooFit.LineColor(ROOT.kBlue), 
                         RooFit.LineStyle(ROOT.kSolid), 
                         RooFit.FillColor(ROOT.kGreen), RooFit.Name(pdf_bkg_b.GetName()+"_1sigma") , RooFit.Normalization(n_bkg_b.getVal() , ROOT.RooAbsReal.NumEvent) )
    print "\tPlot bkg..."
    pdf_bkg_b.plotOn(frame1, RooFit.LineWidth(2), RooFit.LineColor(ROOT.kBlue), RooFit.LineStyle(ROOT.kSolid), 
                     RooFit.Name(pdf_bkg_b.GetName()), RooFit.Normalization(n_bkg_b.getVal() , ROOT.RooAbsReal.NumEvent) )
    print "\tPlot sgn+bkg..."
    pdf_comb_ext.plotOn(frame1, RooFit.LineWidth(2), RooFit.LineColor(ROOT.kRed), RooFit.LineStyle(ROOT.kSolid), RooFit.Name(pdf_comb_ext.GetName()) )
    print "\tPlot sgn..."
    pdf_sgn.plotOn(frame1, RooFit.LineWidth(2), RooFit.LineColor(ROOT.kMagenta), RooFit.LineStyle(ROOT.kDashed), 
                   RooFit.Name(pdf_sgn.GetName()), RooFit.Normalization(pdf_sgn_norm.getVal()*xsec_vis , ROOT.RooAbsReal.NumEvent) )

    print "\tPlot data_obs..."
    data_rebinned.plotOn(frame1, RooFit.Name("data_obs"))
    print "END plotting"
    chi2_s = frame1.chiSquare(pdf_comb_ext.GetName(), "data_obs", 2+1 if bkg_pdf=='dijet' else 3+1 )
    chi2_b = frame1.chiSquare(pdf_comb_ext.GetName(), "data_obs", 2 if bkg_pdf=='dijet' else 3 )
    leg.AddEntry(frame1.findObject("data_obs"), "Data", "PE")
    leg.AddEntry(frame1.getCurve(pdf_bkg_b.GetName()),  ("Bkg. (#chi^{2}=%.2f)" % chi2_b), "L")
    leg.AddEntry(h1sigmaU, "1#sigma bkg. unc.", "F")
    leg.AddEntry(h2sigmaU, "2#sigma bkg. unc.", "F")
    leg.AddEntry(frame1.getCurve(pdf_comb_ext.GetName()), ("Bkg. + signal"), "L")
    leg.AddEntry(frame1.getCurve(pdf_sgn.GetName()), ("Signal, #sigma=%.0f pb" % xsec_vis ), "L")
    frame1.SetMaximum( h_rebinned.GetMaximum()*2.0 )
    frame1.SetMinimum( h_rebinned.GetMinimum()*0.8 )
    pad1.SetLogy()
    print "Drawing frame1..."
    frame1.Draw()

    #ROOT.gPad.Update()
    #sigma2 = frame1.getCurve(pdf_bkg_b.GetName()+"_2sigma")
    #sigma1 = frame1.getCurve(pdf_bkg_b.GetName()+"_1sigma")
    #nominal = frame1.getCurve(pdf_bkg_b.GetName())
    #n2sigma = n.zeros(2sigma.GetN(), dtype=float)
    #nominalX = nominal.GetX()
    #nominalY = nominal.GetY()
    #n1sigmaY = sigma1.GetY()
    #n2sigmaY = sigma2.GetY()
    #for i in xrange(nominal.GetN()):
    #    if i%3!=0:
    #        continue
    #    print ("%.1f: %.1f [%.1f, %.1f]" % (nominalX[i], nominalY[i], n1sigmaY[i], n1sigmaY[2*nominal.GetN()-i-1] ))
    #    print ("     :       [%.1f, %.1f]" % (n2sigmaY[i], n2sigmaY[2*nominal.GetN()-i-1] ))
    #for obj in ROOT.gPad.GetListOfPrimitives():
    #    print obj.GetName()        

    pave_lumi = ROOT.TPaveText(0.484,0.90,0.92,0.96, "NDC")
    pave_lumi.SetFillStyle(0);
    pave_lumi.SetBorderSize(0);
    pave_lumi.SetTextAlign(32)
    pave_lumi.SetTextSize(0.045)
    #pave_lumi.SetTextFont(43)
    pave_lumi.AddText(("%.2f fb^{-1} (2015)" % luminosity))
    pave_lumi.Draw()

    pave_cms = ROOT.TPaveText(0.13,0.83,0.42,0.89, "NDC")
    pave_cms.SetFillStyle(0);
    pave_cms.SetBorderSize(0);
    pave_cms.SetTextAlign(12)
    pave_cms.SetTextSize(0.05)
    #pave_cms.SetTextFont(43)
    pave_cms.AddText("CMS Preliminary")
    pave_cms.Draw()    
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
    frame2.GetYaxis().SetTitle("#frac{Data-Bkg.}{#sqrt{Data}}")
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
    #hresid2.SetLineStyle(ROOT.kSolid)
    #hresid2.SetLineColor(ROOT.kRed)
    #hresid2.SetLineWidth(2)
    #hresid2.GetYaxis().SetRangeUser(-4,4)
    #h_hresid2 = ROOT.TH1F("h_hresid2", "", frame2.GetNbinsX(), frame2.GetXaxis().GetXmin(), frame2.GetXaxis().GetXmax())
    #hresid2 = frame1.pullHist("data_obs", pdf_bkg_b.GetName())
    #pdf_comb_ext_int = pdf_comb_ext.createIntegral(ROOT.RooArgSet(x), "MassFSR").getVal() 
    #for b in xrange(frame2.GetNbinsX()):
    #    n_data = h_rebinned.GetBinContent(b+1)
    #    x.setVal( h_rebinned.GetBinCenter(b+1) )        
    #    sb = pdf_comb_ext.getVal()/pdf_comb_ext_int * (n_sgn.getVal()+n_bkg.getVal()) * h_rebinned.GetBinWidth(b+1)
    #    hresid2.SetBinContent(b+1, (-sb+n_data)/math.sqrt(n_data))
    #    print n_data, sb
    #    h_hresid2.SetBinContent(b+1, hresid2.Eval( frame2.GetXaxis().GetBinCenter(b+1) ) )

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
        h1sigmaU.SetBinContent( bin_i, (-n_i+n_1up_i)/math.sqrt( n_data_i ) )
        h1sigmaD.SetBinContent( bin_i, (-n_i+n_1down_i)/math.sqrt( n_data_i ) )
        h2sigmaU.SetBinContent( bin_i, (-n_i+n_2up_i)/math.sqrt( n_data_i ) )
        h2sigmaD.SetBinContent( bin_i, (-n_i+n_2down_i)/math.sqrt( n_data_i ) )
    frame2.addTH1(h2sigmaU, "HIST")
    frame2.addTH1(h2sigmaD, "HIST")
    frame2.addTH1(h1sigmaU, "HIST")
    frame2.addTH1(h1sigmaD, "HIST")

    frame2.addPlotable(hresid,"pE1")

    print "Drawing frame2..."
    frame2.Draw()
    frame2.GetYaxis().SetRangeUser(-4,4)    

    ROOT.TGaxis.SetMaxDigits(2)
    print "Drawing canvas..."
    c1.cd()
    c1.Draw()

    print "Press ENTER to continue"
    raw_input()

    #c1.SaveAs("tmp.png")
    ROOT.gDirectory.Remove(h1sigmaU)
    ROOT.gDirectory.Remove(h1sigmaD)
    ROOT.gDirectory.Remove(h2sigmaU)
    ROOT.gDirectory.Remove(h2sigmaD)
    ROOT.gDirectory.Remove(c1)
    ws_file.Close()
    mlfit_file.Close()
    ws_file_nobias.Close()
    mlfit_file_nobias.Close()

############################################################################################


#make_fits(pdf='dijet', spin=2, save_dir="../PostPreApproval/")

make_fit_plot()

#make_limit_plot(pdf="dijet", spin=0, save_dir="../PostPreApproval/", is_blind=True, do_acceptance=False)
#make_limit_plot(pdf="dijet", spin=2, save_dir="../PostPreApproval/", is_blind=True, do_acceptance=False)
#make_limit_plot(pdf="dijet", spin=0, save_dir="../PostPreApproval/", is_blind=False, do_acceptance=False)
#make_limit_plot(pdf="dijet", spin=2, save_dir="../PostPreApproval/", is_blind=False, do_acceptance=False)

#make_limit_plot(pdf="dijet", spin=0, save_dir="../PostPreApproval/", is_blind=True, do_acceptance=True)
#make_limit_plot(pdf="dijet", spin=2, save_dir="../PostPreApproval/", is_blind=True, do_acceptance=True)
#make_limit_plot(pdf="dijet", spin=0, save_dir="../PostPreApproval/", is_blind=False, do_acceptance=True)
#make_limit_plot(pdf="dijet", spin=2, save_dir="../PostPreApproval/", is_blind=False, do_acceptance=True)
