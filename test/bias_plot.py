#!/usr/bin/env python

from sys import argv
import commands
import json
import time
import re
import os
import string
import os.path

import ROOT

save = True

signal_to_range = {
    'Spin0_M550' : {
        'file' : '400to750_bias_dijet_deg2_Spin0_M550',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        'err' : 0.0,
        },
    'Spin0_M600' : {
        'file' : '425to800_bias_dijet_deg2_Spin0_M600',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        'err' : 0.0,
        },
    'Spin0_M650' : {
        'file' : '450to850_bias_dijet_deg2_Spin0_M650',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        'err' : 0.0,
        },
    'Spin0_M700' : {
        'file' : '475to900_bias_dijet_deg2_Spin0_M700',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        'err' : 0.0,
        },
    'Spin0_M750' : {
        'file' : '500to950_bias_dijet_deg2_Spin0_M750',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        'err' : 0.0,
        },
    'Spin0_M800' : {
        'file' : '525to1000_bias_dijet_deg2_Spin0_M800',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        'err' : 0.0,
        },
    'Spin0_M850' : {
        'file' : '550to1050_bias_dijet_deg2_Spin0_M850',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        'err' : 0.0,
        },
    'Spin0_M900' : {
        'file' : '575to1100_bias_dijet_deg2_Spin0_M900',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        'err' : 0.0,
        },
    'Spin0_M1000' : {
        'file' : '625to1200_bias_dijet_deg2_Spin0_M1000',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        'err' : 0.0,
        },
    'Spin0_M1100' : {
        'file' : '675to1300_bias_dijet_deg2_Spin0_M1100',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        'err' : 0.0,
        },
    'Spin0_M1200' : {
        'file' : '725to1400_bias_dijet_deg2_Spin0_M1200',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        'err' : 0.0,
        },
    }



def make_canvas_vs_pdf( dir_name="./plots/V6/",
                        save_dir="./plots/V6/",
                        save_name="bias_vs_pdf",
                        signals=[],
                        set_constant=-1):

    leg = ROOT.TLegend(0.10,0.70,0.80,0.89, "","brNDC")
    leg.SetHeader("Fit: dijet")  
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.04)
    leg.SetFillColor(10)    
    leg.SetNColumns(5)

    histos = []
    for isgn,sgn in enumerate(signals):

        h = ROOT.TH1F("h_"+str(isgn), "",  5, 0, 5)
        h.SetTitle("CMS Preliminary 2016 #sqrt{s}=13 TeV")

        f = ROOT.TFile.Open(dir_name+"/ftest_Xbb_workspace_Had_MT_MinPt100_DH1p6_MassFSR_"+signal_to_range[sgn]['file']+".root")
        if f==None:
            continue
        print "Opened file", f.GetName()

        h_bias = ROOT.TH2F("h_bias", "",  6,0, 6,100,-4,4)
        h_err = ROOT.TH2F("h_err", "",  6,0, 6,100,-4,4)
        h_err2 = ROOT.TH2F("h_err2", "",  6,0, 6,500,50,1500)

        toys = f.Get("toys")        
        toys.Draw("(ns_fit-ns_gen)/ns_err:alt>>h_bias","", "")
        toys.Draw("ns_err/ns_asy:alt>>h_err","", "")
        toys.Draw("ns_err:alt>>h_err2","", "")

        max_bias = 0.0
        max_bias_over_sgn = 0.0
        error = 0
        for bin in xrange(0, h.GetNbinsX()):
            b = bin if bin<4 else bin+1
            proj_bias = h_bias.ProjectionY("_py", b+1, b+1)
            proj_err = h_err.ProjectionY("_py", b+1, b+1)
            proj_err2 = h_err2.ProjectionY("_py", b+1, b+1)
            bias = proj_bias.GetMean()
            err = proj_err.GetMean()
            error = proj_err2.GetMean()
            if abs(bias)>max_bias and bin!=3:
                max_bias = abs(bias)
                max_bias_over_sgn = max_bias*err if set_constant<0 else set_constant*err
            h.SetBinContent( bin+1  , bias)
            h.SetBinError( bin+1 , proj_bias.GetMeanError())
            print bias,err
        
        signal_to_range[sgn]['max_bias'] = max_bias if set_constant<0 else set_constant
        signal_to_range[sgn]['max_bias_over_sgn'] = max_bias_over_sgn
        signal_to_range[sgn]['err'] = error

        h.SetMarkerColor(1+isgn)
        h.SetMarkerSize(1.5)
        h.SetLineColor(1)
        h.SetMarkerStyle(ROOT.kFullCircle)
        leg.AddEntry(h, ("%.0f GeV" % float(sgn[7:])), "P")
        histos.append(h)
        f.Close()
    
    c = ROOT.TCanvas("c", "canvas", 800, 600) 
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.1, 1, 1.0)     
    pad1.SetGridx()  
    pad1.SetGridy()  
    pad1.Draw()      
    pad1.cd()    
    
    for nh,h in enumerate(histos):
        h.Print()
        if nh==0:
            h.SetStats(0)
            h.SetMinimum(-3.0)
            h.SetMaximum(+3.0)
            h.GetXaxis().SetLabelSize(0.05)
            h.GetXaxis().SetBinLabel(1, "x^P(x)")
            h.GetXaxis().SetBinLabel(2, "P(x)*exp(x)")
            h.GetXaxis().SetBinLabel(3, "dijet")
            h.GetXaxis().SetBinLabel(4, "P(x)")
            #h.GetXaxis().SetBinLabel(4, "P(x)*dijet")
            h.GetXaxis().SetBinLabel(5, "exp^P(x)")
            h.GetYaxis().SetTitle("Mean of #frac{#hat{#mu}-#mu}{#sigma_{#mu}}")
            h.Draw("PE")      
        else:
            h.Draw("PESAME")
 
    pad1.cd()
    leg.Draw()
    print(json.dumps(signal_to_range, indent = 4))

    for ext in ["png", "pdf"]:
        if save:
            c.SaveAs(save_dir+"/"+save_name+"."+ext)
    raw_input()

#####################################################################################

def make_canvas_vs_mass( save_dir="./plots/V6/",                         
                         save_name="bias_vs_mass",
                         signals=[],
                         do_fit=False):

    c = ROOT.TCanvas("c", "canvas", 800, 600) 
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.1, 1, 1.0)     
    pad1.SetGridx()  
    pad1.SetGridy()  
    pad1.Draw()      
    pad1.cd()    

    leg = ROOT.TLegend(0.30,0.60,0.65,0.89, "","brNDC")
    leg.SetHeader("Bias")  
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.04)
    leg.SetFillColor(10)    

    mg = ROOT.TMultiGraph()
    h = ROOT.TGraphAsymmErrors()
    h.SetLineColor(ROOT.kBlue)
    h.SetLineStyle(ROOT.kSolid)
    h.SetLineWidth(2)
    h.SetTitle("CMS Preliminary 2016 #sqrt{s}=13 TeV")

    for isgn,sgn in enumerate(signals):
        mass = float(sgn[7:])
        spin = float(sgn[4])
        h.SetPoint(isgn, mass, signal_to_range[sgn]['max_bias'] )

    leg.AddEntry(h, "Maximum bias", "L")
    mg.Add(h)

    mg.SetMinimum(0.)
    mg.SetMaximum(2.)

    mg.Draw("ALP3")
    mg.SetTitle("CMS Preliminary 2016 #sqrt{s}=13 TeV, L=2.63 fb^{-1}")
    mg.GetXaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetTitleOffset(0.85)
    mg.GetXaxis().SetTitle("Mass (GeV)")
    mg.GetYaxis().SetTitle("Mean of #frac{#hat{#mu}-#mu}{#sigma_{#mu}}")
    leg.Draw()

    if do_fit:
        func = ROOT.TF1("func", "[0]*TMath::Power((x-500)/1200, [1])", 550., 1200.)
        mg.Fit(func, "R")
        leg.AddEntry(func, ("Fit: %.2E[(x-500)/1200]^(%.2E)" % (func.GetParameter(0), func.GetParameter(1))), "L")

    for ext in ["png", "pdf"]:
        if save:
            c.SaveAs(save_dir+"/"+save_name+"."+ext)
    raw_input()

#####################################################################################

def make_canvas_vs_mass_err( save_dir="./plots/V6/",                         
                             save_name="bias_vs_mass",
                             signals=[]):

    c = ROOT.TCanvas("c", "canvas", 800, 600) 
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.1, 1, 1.0)     
    pad1.SetGridx()  
    pad1.SetGridy()  
    pad1.Draw()      
    pad1.cd()    

    leg = ROOT.TLegend(0.30,0.60,0.65,0.89, "","brNDC")
    leg.SetHeader("Error")  
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.04)
    leg.SetFillColor(10)    

    mg = ROOT.TMultiGraph()
    h = ROOT.TGraphAsymmErrors()
    h.SetLineColor(ROOT.kBlue)
    h.SetLineStyle(ROOT.kSolid)
    h.SetLineWidth(2)
    h.SetTitle("CMS Preliminary 2016 #sqrt{s}=13 TeV")

    for isgn,sgn in enumerate(signals):
        mass = float(sgn[7:])
        spin = float(sgn[4])
        h.SetPoint(isgn, mass, signal_to_range[sgn]['err'] )

    leg.AddEntry(h, "Error", "L")
    mg.Add(h)

    mg.SetMinimum(0.)
    mg.SetMaximum(1500.)

    mg.Draw("ALP3")
    mg.SetTitle("CMS Preliminary 2016 #sqrt{s}=13 TeV, L=2.63 fb^{-1}")
    mg.GetXaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetTitleOffset(0.85)
    mg.GetXaxis().SetTitle("Mass (GeV)")
    mg.GetYaxis().SetTitle("Error")
    leg.Draw()

    for ext in ["png", "pdf"]:
        if save:
            c.SaveAs(save_dir+"/"+save_name+"."+ext)
    raw_input()
    
######################################################################################

def make_canvas_vs_mass_biasOmass( save_dir="./plots/V6/",                         
                                   save_name="biasOmass_vs_mass",
                                   signals=[],
                                   do_fit=True):

    c = ROOT.TCanvas("c", "canvas", 800, 600) 
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.1, 1, 1.0)     
    pad1.SetGridx()  
    pad1.SetGridy()  
    pad1.Draw()      
    pad1.cd()    

    leg = ROOT.TLegend(0.30,0.60,0.65,0.89, "","brNDC")
    leg.SetHeader("Bias")  
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.04)
    leg.SetFillColor(10)    

    mg = ROOT.TMultiGraph()
    h = ROOT.TGraphAsymmErrors()
    h.SetLineColor(ROOT.kBlue)
    h.SetLineStyle(ROOT.kSolid)
    h.SetLineWidth(2)
    h.SetTitle("CMS Preliminary 2016 #sqrt{s}=13 TeV")

    for isgn,sgn in enumerate(signals):
        mass = float(sgn[7:])
        spin = float(sgn[4])
        h.SetPoint(isgn, mass, signal_to_range[sgn]['max_bias_over_sgn'] )

    leg.AddEntry(h, "Maximum bias in units of #mu(1 pb)", "L")
    mg.Add(h)

    mg.SetMinimum(0.)
    mg.SetMaximum(5.)

    mg.Draw("ALP3")
    mg.SetTitle("CMS Preliminary 2016 #sqrt{s}=13 TeV, L=2.63 fb^{-1}")
    mg.GetXaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetTitleOffset(0.85)
    mg.GetXaxis().SetTitle("Mass (GeV)")
    mg.GetYaxis().SetTitle("Bias")

    if do_fit:
        func = ROOT.TF1("func", "[0]*TMath::Power((x-500)/1200, [1])", 550., 1200.)
        mg.Fit(func, "R")
        leg.AddEntry(func, ("Fit: %.2E[(x-500)/1200]^(%.2E)" % (func.GetParameter(0), func.GetParameter(1))), "L")

    leg.Draw()

    for ext in ["png", "pdf"]:
        if save:
            c.SaveAs(save_dir+"/"+save_name+"."+ext)
    raw_input()

######################################################################################

def make_canvas_vs_xsec( dir_name="./plots/V6/",
                         save_dir="./plots/V6/",
                         save_name="bias_vs_xsec",
                         sgn="Spin0_M750",
                         do_fit=False):

    leg = ROOT.TLegend(0.10,0.70,0.80,0.89, "","brNDC")
    leg.SetHeader(sgn)  
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.04)
    leg.SetFillColor(10)    

    f = ROOT.TFile.Open(dir_name+"/linearity/ftest_Xbb_workspace_Had_MT_MinPt100_DH1p6_MassFSR_"+signal_to_range[sgn]['file']+".root")
    if f==None:
        return
    print "Opened file", f.GetName()

    toys = f.Get("toys")        
    toys.Draw("(ns_fit-ns_gen)/ns_err:ns_asy>>h_bias","alt==fit", "prof")    
    ROOT.gDirectory.Get("h_bias").GetYaxis().SetTitle("Mean of (N_{S}^{fit}-N_{S}^{gen})/#sigma_{S}^{fit}")
    ROOT.gDirectory.Get("h_bias").GetYaxis().SetTitleSize(0.05)
    ROOT.gDirectory.Get("h_bias").GetYaxis().SetTitleOffset(0.90)
    ROOT.gDirectory.Get("h_bias").GetXaxis().SetTitleOffset(0.80)
    ROOT.gDirectory.Get("h_bias").GetXaxis().SetTitleSize(0.05)
    ROOT.gDirectory.Get("h_bias").GetXaxis().SetTitle("N_{S}^{gen}")
    ROOT.gDirectory.Get("h_bias").GetYaxis().SetRangeUser(-0.50, 0.50)
    #ROOT.gDirectory.Get("h_bias").GetXaxis().SetLimits(200,1500)
    ROOT.gDirectory.Get("h_bias").SetLineWidth(4)
    ROOT.gDirectory.Get("h_bias").SetTitle("")
    ROOT.gDirectory.Get("h_bias").SetLineColor(ROOT.kBlue)
    ROOT.gStyle.SetOptStat(0)

    leg.AddEntry(ROOT.gDirectory.Get("h_bias"), "Injected signal" , "L")
    leg.Draw()

    if do_fit:
        func = ROOT.TF1("func", "[0]+[1]*x", 200., 1500)
        ROOT.gDirectory.Get("h_bias").Fit(func, "R")
 

    raw_input()

    for ext in ["png", "pdf"]:
        if save:
            ROOT.gPad.SaveAs(save_dir+"/"+save_name+"."+ext)


######################################################################################

signals=[
    'Spin0_M550', 
    'Spin0_M600', 
    'Spin0_M650', 
    'Spin0_M700', 
    'Spin0_M750', 
    'Spin0_M800',
    'Spin0_M850', 
    'Spin0_M900', 
    'Spin0_M1000', 
    'Spin0_M1100', 
    'Spin0_M1200'
    ]

#make_canvas_vs_xsec( dir_name="./plots/PostPreApproval//", save_dir="./plots/PostPreApproval//", sgn="Spin0_M750", save_name="bias_vs_xsec_M750")
#make_canvas_vs_xsec( dir_name="./plots/PostPreApproval//", save_dir="./plots/PostPreApproval//", sgn="Spin0_M1000", save_name="bias_vs_xsec_M1000")

make_canvas_vs_pdf( dir_name="./plots/PostPreApproval/ftest/", save_dir="./plots/PostPreApproval/", signals=signals, save_name="bias_vs_pdf_deg2_sliding_windows", set_constant=-1.0)
#make_canvas_vs_mass(save_dir="./plots/PostPreApproval/ftest/", signals=signals, save_name="bias_vs_mass_deg2_sliding_windows", do_fit=False)
make_canvas_vs_mass_err(save_dir="./plots/PostPreApproval/ftest/", signals=signals, save_name="bias_vs_mass_err_deg2_sliding_windows")
#make_canvas_vs_mass_biasOmass(save_dir="./plots/PostPreApproval/", signals=signals, save_name="biasOmass_vs_mass_deg2_sliding_windows", do_fit=True)


