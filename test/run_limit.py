#!/usr/bin/env python

from sys import argv
import commands
import time
import re
import os
import string
import os.path

import ROOT

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
    'Spin0_M850' : [[6.0, 18.0],  [-0.01,10.0], [22.0, 300.0]],
    'Spin0_M900' : [],
    'Spin0_M1000' : [],
    'Spin0_M1100' : [],
    'Spin0_M1200' : [],
    'Spin2_M550' : [],
    'Spin2_M600' : [],
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

############################################################################################

def run_combine(datacard='', what='limit', params=[]):

    print "Running on datacard:", datacard

    if what=='limit':
        res = []
        if not os.path.exists("higgsCombine"+datacard+".Asymptotic.mH120.root"):
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

    elif what=='fit':
        #command = 'combine -M MaxLikelihoodFit '+datacard+'.txt'+' --plots -n '+datacard+' --rMin -10 --rMax +10'
        command = 'combine -M MaxLikelihoodFit '+datacard+'.txt'+' -n '+datacard+' --rMin -10 --rMax +10 --plot '
        if len(params)>0:
            command += ' --setPhysicsModelParameterRanges '
        for ip,p in enumerate(params):
            command += ('a%d_polydijet_deg2_0=%.2f,%.2f' % (ip, p[0], p[1]))
            if ip<len(params)-1:
                command += ':'
        print command
        os.system(command)
        return []

    else:
        return []


############################################################################################

def make_postfit(mlfit="mlfit.root", plot="Had_MT_MinPt100_DH1p6_fit_b"):

    c = ROOT.TCanvas("c", "canvas", 500, 500) 
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.1, 1, 1.0)     
    pad1.SetGridx()  
    pad1.SetGridy()  
    pad1.Draw()      
    pad1.cd()    
    
    f = ROOT.TFile.Open(mlfit)
    p = f.Get(plot)



############################################################################################

def make_canvas( results=[], out_name="", save_dir="./plots/Jun09/" ):

    c = ROOT.TCanvas("c", "canvas", 500, 500) 
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.1, 1, 1.0)     
    pad1.SetGridx()  
    pad1.SetGridy()  
    pad1.Draw()      
    pad1.cd()    
    
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
    
    expected.SetLineColor(ROOT.kBlack)
    expected.SetLineStyle(ROOT.kSolid)
    expected.SetLineWidth(2)
    
    onesigma.SetLineWidth(0)
    onesigma.SetFillColor(ROOT.kGreen)
    onesigma.SetFillStyle(1001)
    
    twosigma.SetLineWidth(0)
    twosigma.SetFillColor(ROOT.kYellow)
    twosigma.SetFillStyle(1001)

    for ires,res in enumerate(results):
        mass_name = res[0]
        mass_results = res[1]
        imass = float(mass_name.split('_')[-1][1:]) 
        expected.SetPoint(ires, imass, mass_results[2])
        onesigma.SetPoint(ires, imass, mass_results[2])
        onesigma.SetPointError(ires, 0.0, 0.0, mass_results[2]-mass_results[1], mass_results[3]-mass_results[2])
        twosigma.SetPoint(ires, imass, mass_results[2])
        twosigma.SetPointError(ires, 0.0, 0.0, mass_results[2]-mass_results[0], mass_results[4]-mass_results[2])

    expected.Print("")
    onesigma.Print("")
    twosigma.Print("")

    leg.AddEntry(expected, "Expected", "L")
    leg.AddEntry(onesigma, "68%", "F")
    leg.AddEntry(twosigma, "95%", "F")
    
    mg.Add(twosigma)
    mg.Add(onesigma)
    mg.Add(expected)

    mg.SetMinimum(0.)
    mg.SetMaximum(20.)

    mg.Draw("ALP3")
    mg.SetTitle("CMS Preliminary 2016 #sqrt{s}=13 TeV, L=2.63 fb^{-1}")
    mg.GetXaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetTitleOffset(0.85)
    mg.GetXaxis().SetTitle("Mass (GeV)")
    mg.GetYaxis().SetTitle("#sigma #times BR(X#rightarrow b#bar{b}) (pb) at 95% CL")
    leg.Draw()

    raw_input()

    for ext in ["png", "pdf"]:
        c.SaveAs(save_dir+"/limit_"+out_name+"."+ext)

############################################################################################

def make_canvas_split( results=[], out_name="", save_dir="./plots/Jun09/" ):

    c = ROOT.TCanvas("c", "canvas", 500, 500) 
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.1, 1, 1.0)     
    pad1.SetGridx()  
    pad1.SetGridy()  
    pad1.Draw()      
    pad1.cd()    
    
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
    expected =[]
    onesigma = []
    twosigma = []
    for ig,g in enumerate(results):
        ex = ROOT.TGraphAsymmErrors()
        ex.SetName(("expected_%d" % ig))
        ex.SetLineColor(ROOT.kBlack)
        ex.SetLineStyle(ROOT.kSolid)
        ex.SetLineWidth(2)
        expected.append( ex )
        on = ROOT.TGraphAsymmErrors()
        on.SetName(("onesigma_%d" % ig))
        on.SetLineWidth(0)
        on.SetFillColor(ROOT.kGreen)
        on.SetFillStyle(1001)
        onesigma.append( on )
        tw = ROOT.TGraphAsymmErrors()
        tw.SetName(("twosigma_%d" % ig))
        tw.SetLineWidth(0)
        tw.SetFillColor(ROOT.kYellow)
        tw.SetFillStyle(1001)
        twosigma.append( tw )


    for ires1,res1 in enumerate(results):
        for ires2,res2 in enumerate(res1):
            mass_name = res2[0]
            mass_results = res2[1]
            imass = float(mass_name.split('_')[-1][1:]) 
            expected[ires1].SetPoint(ires2, imass, mass_results[2])
            onesigma[ires1].SetPoint(ires2, imass, mass_results[2])
            onesigma[ires1].SetPointError(ires2, 0.0, 0.0, mass_results[2]-mass_results[1], mass_results[3]-mass_results[2])
            twosigma[ires1].SetPoint(ires2, imass, mass_results[2])
            twosigma[ires1].SetPointError(ires2, 0.0, 0.0, mass_results[2]-mass_results[0], mass_results[4]-mass_results[2])
        expected[ires1].Print()
        onesigma[ires1].Print()
        twosigma[ires1].Print()
        mg.Add(twosigma[ires1])
        mg.Add(onesigma[ires1])
        mg.Add(expected[ires1])

    leg.AddEntry(expected[0], "Expected", "L")
    leg.AddEntry(onesigma[0], "68%", "F")
    leg.AddEntry(twosigma[0], "95%", "F")
    
    mg.SetMinimum(0.)
    mg.SetMaximum(20.)

    mg.Draw("ALP3")
    mg.SetTitle("CMS Preliminary 2016 #sqrt{s}=13 TeV, L=2.63 fb^{-1}")
    mg.GetXaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetTitleOffset(0.85)
    mg.GetXaxis().SetTitle("Mass (GeV)")
    mg.GetYaxis().SetTitle("#sigma #times BR(X#rightarrow b#bar{b}) (pb) at 95% CL")
    mg.GetXaxis().SetLimits(500, 1250)

    leg.Draw()

    raw_input()

    for ext in ["png", "pdf"]:
        c.SaveAs(save_dir+"/limit_"+out_name+"."+ext)


############################################################################################

def make_limit_plot(out_name="", save_dir=""):

    tests = []
    results = []
    for cat_btag in ['Had_MT']:
        for cat_kin in ['MinPt100_DH1p6']:        
            for pdf_s in ['buk']:
                for pdf_b in ['polydijet']:
                    for mass in ['MassFSR']:
                        for sgn in [
                            'Spin0_M550', 'Spin0_M600', 'Spin0_M650', 'Spin0_M700', 'Spin0_M750', 'Spin0_M800', 'Spin0_M850', 'Spin0_M900', 'Spin0_M1000', 'Spin0_M1100', 'Spin0_M1200',
                            #'Spin2_M550', 'Spin2_M600', 'Spin2_M650', 'Spin2_M700', 'Spin2_M750', 'Spin2_M800', 'Spin2_M850', 'Spin2_M900', 'Spin2_M1000', 'Spin2_M1100', 'Spin2_M1200'
                            ]:
                            for x_range in [
                                #'550to1200'
                                signal_to_range[sgn]
                                ]:
                                tests.append(cat_btag+'_'+cat_kin+'_'+mass+'_'+x_range+'_'+pdf_s+'_'+pdf_b+'_'+sgn)

    print tests
    for itest,test in enumerate(tests):
        res = run_combine("Xbb_workspace_"+test, what='limit')
        if len(res)>0:
            results.append([test.split('_')[-1],res])
            
    make_canvas( results=results, out_name=out_name, save_dir=save_dir )

############################################################################################

def make_limit_plot_split(out_name="", save_dir=""):

    tests = []
    results = []
    for cat_btag in ['Had_MT']:
        for cat_kin in ['MinPt100_DH1p6']:        
            for pdf_s in ['buk']:
                for pdf_b in ['polydijet']:
                    for mass in ['MassFSR']:
                        for sgn in [
                            'Spin0_M550', 'Spin0_M600', 'Spin0_M650', 'Spin0_M700', 'Spin0_M750', 'Spin0_M800', 'Spin0_M850', 'Spin0_M900', 'Spin0_M1000', 'Spin0_M1100', 'Spin0_M1200',
                            #'Spin2_M550', 'Spin2_M600', 'Spin2_M650', 'Spin2_M700', 'Spin2_M750', 'Spin2_M800', 'Spin2_M850', 'Spin2_M900', 'Spin2_M1000', 'Spin2_M1100', 'Spin2_M1200'
                            ]:
                            for x_range in [
                                #'550to1200'
                                signal_to_range[sgn]
                                ]:
                                tests.append(cat_btag+'_'+cat_kin+'_'+mass+'_'+x_range+'_'+pdf_s+'_'+pdf_b+'_'+sgn)

    print tests
    for itest,test in enumerate(tests):
        res = run_combine("Xbb_workspace_"+test, what='limit')
        if len(res)>0:
            results.append([test.split('_')[-1],res])
            
    results_merged = [ [results[0], results[1], results[2]], [results[3], results[4], results[5]], [results[6], results[7]], [results[8], results[9], results[10]] ]
    #results_merged = [ [results[0], results[1], results[2]]  ]

    make_canvas_split( results=results_merged, out_name=out_name, save_dir=save_dir )


############################################################################################

def make_fits():

    tests = []
    results = []
    for cat_btag in ['Had_MT']:
        for cat_kin in ['MinPt100_DH1p6']:        
            for pdf_s in ['buk']:
                for pdf_b in ['polydijet']:
                    for mass in ['MassFSR']:
                        for sgn in ['Spin0_M750', 'Spin0_M850']:
                            for x_range in [
                                signal_to_range[sgn]
                                ]:
                                tests.append(cat_btag+'_'+cat_kin+'_'+mass+'_'+x_range+'_'+pdf_s+'_'+pdf_b+'_'+sgn)

    print tests
    for itest,test in enumerate(tests):
        run_combine("Xbb_workspace_"+test, what='fit', params=signal_to_parameters[test.split('_')[-2]+'_'+test.split('_')[-1]])
            
############################################################################################


#make_fits()
make_limit_plot(out_name="Spin0_polydijet", save_dir="../V6/")
#make_limit_plot_split(out_name="Spin0_split_polydijet", save_dir="../V6/")
