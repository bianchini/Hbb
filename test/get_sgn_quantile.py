from sys import argv
import ROOT
import sys
sys.path.append('./')
sys.path.append('../python/')

from parameters_cfi import *


import math

f = ROOT.TFile.Open("./plots/V7/Xbb_workspace_Had_MT_MinPt100_DH1p6_MassFSR_400to1500.root")


sgns = [ 'Spin0_M550','Spin0_M600', 'Spin0_M650', 'Spin0_M700', 'Spin0_M750', 'Spin0_M800', 'Spin0_M850', 'Spin0_M900', 'Spin0_M1000', 'Spin0_M1100', 'Spin0_M1200' ]

low = ROOT.TGraphAsymmErrors()
low.SetLineColor(ROOT.kBlue)
low.SetLineStyle(ROOT.kSolid)
low.SetLineWidth(2)
high = ROOT.TGraphAsymmErrors()
high.SetLineColor(ROOT.kBlue)
high.SetLineStyle(ROOT.kSolid)
high.SetLineWidth(2)

for isgn,sgn in enumerate(sgns):
    w = f.Get("Xbb_workspace")
    pdf = w.pdf('buk_pdf_sgn_'+sgn)
    mean = w.var('mean_sgn_'+sgn).getVal()
    x = w.var("x")
    x.setRange( "all", FitSgnCfg[sgn]['fit_range'][0], FitSgnCfg[sgn]['fit_range'][1] )
    norm = pdf.createIntegral(ROOT.RooArgSet(x), "all").getVal() 
    print norm
    step_size = 5
    ratio = 0.
    n_step = 0
    while (ratio<0.475):
        x.setRange("q", mean, mean+n_step*step_size)
        ratio =  pdf.createIntegral(ROOT.RooArgSet(x), "q").getVal()/norm
        print ("Step %d [%.0f,%.0f]: %.3f" % (n_step, mean,  mean+n_step*step_size, ratio))
        n_step += 1
        if (mean+n_step*step_size) > FitSgnCfg[sgn]['fit_range'][1]:
            break
    last_ratio = ratio
    x_high = (mean+n_step*step_size)

    ratio = 0.
    n_step = 0
    while (ratio<0.9):
        x.setRange("q", mean-n_step*step_size, mean)
        ratio =  pdf.createIntegral(ROOT.RooArgSet(x), "q").getVal()/norm + last_ratio
        print ("Step %d [%.0f,%.0f]: %.3f" % (n_step,  mean-n_step*step_size, mean, ratio))
        n_step += 1
        if (mean-n_step*step_size) < FitSgnCfg[sgn]['fit_range'][0]:
            break

    x_low = (mean-n_step*step_size)

    print ("[%.0f, %.0f]" % (x_low,x_high))
    low.SetPoint(isgn, float(sgn.split('_')[-1][1:]), x_low)
    high.SetPoint(isgn, float(sgn.split('_')[-1][1:]), x_high)

c = ROOT.TCanvas("c", "canvas", 500, 500) 
mg = ROOT.TMultiGraph()
mg.Add(low)
mg.Add(high)
mg.Draw("ALP")

raw_input()
