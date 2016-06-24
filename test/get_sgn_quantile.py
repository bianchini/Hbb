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
low.SetLineWidth(3)
high = ROOT.TGraphAsymmErrors()
high.SetLineColor(ROOT.kRed)
high.SetLineStyle(ROOT.kSolid)
high.SetLineWidth(3)
mu = ROOT.TGraphAsymmErrors()
mu.SetLineColor(ROOT.kBlack)
mu.SetLineStyle(ROOT.kDashed)
mu.SetLineWidth(3)

quantile_low = 0.10 
quantile_high = 0.025 

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
    while (ratio<(0.5 - quantile_high)):
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
    while (ratio<(1-quantile_low)):
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
    mu.SetPoint(isgn, float(sgn.split('_')[-1][1:]), mean)


pol1 = ROOT.TF1("pol1", "[0]*x + [1]", 550, 1200)
pol1.SetLineColor(ROOT.kBlue)
pol1.SetLineWidth(2)
pol1.SetLineStyle(ROOT.kDashed)
low.Fit(pol1,"R")

pol2 = ROOT.TF1("pol2", "[0]*x + [1]", 550, 1200)
pol2.SetLineColor(ROOT.kRed)
pol2.SetLineWidth(2)
pol2.SetLineStyle(ROOT.kDashed)
high.Fit(pol2,"R")

c = ROOT.TCanvas("c", "canvas", 500, 500) 
leg = ROOT.TLegend(0.13,0.65,0.55,0.88, "","brNDC")
leg.SetFillStyle(0)
leg.SetBorderSize(0)
leg.SetTextSize(0.04)
leg.SetFillColor(10)    
leg.AddEntry(mu, "#mu", "L")
leg.AddEntry(low, ("q=%.0f%%" % (quantile_low*100)), "L")
leg.AddEntry(high, ("q=%.1f%%" % (quantile_high*100)), "L")

mg = ROOT.TMultiGraph()
mg.Add(low)
mg.Add(high)
mg.Add(mu)
mg.Draw("ALP")

mg.GetXaxis().SetTitleSize(0.05)
mg.GetYaxis().SetTitleSize(0.05)
mg.GetYaxis().SetTitleOffset(0.85)
mg.GetXaxis().SetTitleOffset(0.85)
mg.GetXaxis().SetTitle("m_{X} (GeV)")
mg.GetYaxis().SetTitle("mass (GeV)")
leg.Draw()

raw_input()

for ext in ["png", "pdf"]:
    c.SaveAs("./plots/V7/signal_quantiles."+ext)
