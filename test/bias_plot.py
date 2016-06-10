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


signal_to_range = {
    'Spin0_M650' : {
        'file' : '400to800_bias_polydijet_deg3',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        },
    'Spin0_M750-525to1200' : {
        'file' : '525to1200_bias_polydijet_deg3_data_obs_buk_Spin0_M750_xsec0',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        },
    'Spin0_M850-525to1200' : {
        'file' : '525to1200_bias_polydijet_deg3_data_obs_buk_Spin0_M850_xsec0',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        },
    'Spin0_M1000' : {
        'file' : '700to1400_bias_polydijet_deg3_data_obs_buk_Spin0_M1000_xsec0',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        },
    'Spin0_M1200' : {
        'file' : '700to1400_bias_polydijet_deg3_data_obs_buk_Spin0_M1200_xsec0',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        },
    'Spin0_M750' :{ 
        'file' : '525to900_bias_polydijet_deg3',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        },
    'Spin0_M850' : {
        'file' : '600to1000_bias_polydijet_deg3',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        },

    'Spin0_M750-400to900' : {
        'file' : '400to900_bias_polydijet_deg3',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        },
    'Spin0_M750-425to900' : {
        'file' : '425to900_bias_polydijet_deg3',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        },
    'Spin0_M750-450to900' : {
        'file' : '450to900_bias_polydijet_deg3',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        },
    'Spin0_M750-475to900' : {
        'file' : '475to900_bias_polydijet_deg3',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        },
    'Spin0_M750-500to900' : {
        'file' : '500to900_bias_polydijet_deg3',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        },
    'Spin0_M750-525to900' : {
        'file' : '525to900_bias_polydijet_deg3',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        },
    'Spin0_M750-550to900' : {
        'file' : '550to900_bias_polydijet_deg3',
        'max_bias' : 0.0,
        'max_bias_over_sgn' : 0.0,
        },

    }

def make_canvas( dir_name="./plots/V5/",
                 save_dir="./plots/Jun09/",
                 save_name="bias",
                 signals=[] ):

    leg = ROOT.TLegend(0.60,0.65,0.85,0.89, "","brNDC")
    leg.SetHeader("Fit: P(x)*dijet")  
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.04)
    leg.SetFillColor(10)    

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

        toys = f.Get("toys")        
        toys.Draw("(ns_fit-ns_gen)/ns_err:alt>>h_bias","", "")
        toys.Draw("ns_err/ns_asy:alt>>h_err","", "")

        max_bias = 0.0
        max_bias_over_sgn = 0.0
        for bin in xrange(0, h.GetNbinsX()):
            b = bin if bin<2 else bin+1
            proj_bias = h_bias.ProjectionY("_py", b+1, b+1)
            proj_err = h_err.ProjectionY("_py", b+1, b+1)
            bias = proj_bias.GetMean()
            err = proj_err.GetMean()
            if abs(bias)>max_bias and bin!=2:
                max_bias = abs(bias)
                max_bias_over_sgn = max_bias*err
            h.SetBinContent( bin+1  , bias)
            h.SetBinError( bin+1 , proj_bias.GetMeanError())
            print bias,err
        
        signal_to_range[sgn]['max_bias'] = max_bias
        signal_to_range[sgn]['max_bias_over_sgn'] = max_bias_over_sgn

        h.SetMarkerColor(1+isgn)
        h.SetMarkerSize(1.5)
        h.SetLineColor(1)
        h.SetMarkerStyle(ROOT.kFullCircle)
        leg.AddEntry(h, sgn, "P")
        histos.append(h)
        f.Close()
    
    c = ROOT.TCanvas("c", "canvas", 600, 600) 
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.1, 1, 1.0)     
    pad1.SetGridx()  
    pad1.SetGridy()  
    pad1.Draw()      
    pad1.cd()    
    
    for nh,h in enumerate(histos):
        h.Print()
        if nh==0:
            h.SetStats(0)
            h.SetMinimum(-2.0)
            h.SetMaximum(+2.0)
            h.GetXaxis().SetLabelSize(0.05)
            h.GetXaxis().SetBinLabel(1, "x^P(x)")
            h.GetXaxis().SetBinLabel(2, "P(x)*exp(x)")
            h.GetXaxis().SetBinLabel(3, "P(x)")
            h.GetXaxis().SetBinLabel(4, "P(x)*dijet")
            h.GetXaxis().SetBinLabel(5, "exp^P(x)")
            h.GetYaxis().SetTitle("Mean of #frac{#hat{#mu}-#mu}{#sigma_{#mu}}")
            h.Draw("PE")      
        else:
            h.Draw("PESAME")

    pad1.cd()
    leg.Draw()
    print(json.dumps(signal_to_range, indent = 4))
    #for x in signal_to_range.keys():
    #    print x
    #    for y in signal_to_range[x].keys():
    #        if "bias" in y:
    #            print ('\t%s: %.2f' % (y, signal_to_range[x][y]) )

    for ext in ["png", "pdf"]:
        c.SaveAs(save_dir+"/"+save_name+"."+ext)
    raw_input()


######################################################################################

make_canvas( dir_name="./plots/V5/", signals=['Spin0_M650','Spin0_M750', 'Spin0_M850', 'Spin0_M1000', 'Spin0_M1200'], save_dir="./plots/Jun09/", save_name="bias_sliding_windows")

#make_canvas( dir_name="./plots/V5/", signals=['Spin0_M750', 'Spin0_M850','Spin0_M750-525to1200', 'Spin0_M850-525to1200'])

#make_canvas( dir_name="./plots/V5/biases_6to10_0p02to0p08_35to100/", 
#             save_dir="./plots/Jun09/",
#             save_name="bias_Spin0_M750_Xto900",
#             signals=[#'Spin0_M750-400to900',
#                      'Spin0_M750-425to900', 'Spin0_M750-450to900', 'Spin0_M750-475to900', 'Spin0_M750-500to900', 'Spin0_M750-525to900', 'Spin0_M750-550to900'
#                      ]
#             )
