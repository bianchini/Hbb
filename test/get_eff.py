from sys import argv
argv.append( '-b-' )
import ROOT
ROOT.gROOT.SetBatch(True)
argv.remove( '-b-' )

import math

window = [400,1300]

qcd_num = 0.0
qcd_den = 0.0
qcd_num_err = 0.0
qcd_den_err = 0.0

data_num = 0.0
data_den = 0.0

for sample in ["HT100to200",
               "HT200to300",
               "HT300to500",
               "HT500to700",
               "HT700to1000",
               "HT1000to1500",
               "HT1500to2000",
               "HT2000toInf"]:

    print sample
    qcd_yield_err = ROOT.Double()

    f = ROOT.TFile.Open("plots/JetHT/"+sample+".root")
    h_den = f.Get("Had_MT_MinPt100_DH1p6/Had_MT_MinPt100_DH1p6_MassFSR")
    [bin_l,bin_h] = [h_den.FindBin( window[0] ), h_den.FindBin( window[1] )]
    den = h_den.IntegralAndError(bin_l,bin_h, qcd_yield_err)
    print ("\tDen: %.0f +/- %.0f" % (den,qcd_yield_err))
    qcd_den_err += qcd_yield_err*qcd_yield_err
    qcd_den += den
    h_num = f.Get("Had_MT_MinPt100_HLT_DH1p6/Had_MT_MinPt100_HLT_DH1p6_MassFSR")
    [bin_l,bin_h] = [h_num.FindBin( window[0] ), h_num.FindBin( window[1] )]
    num = h_num.IntegralAndError(bin_l,bin_h, qcd_yield_err)
    print ("\tNum: %.0f +/- %.0f" % (num,qcd_yield_err))
    qcd_num_err += qcd_yield_err*qcd_yield_err
    qcd_num += num
    f.Close()

for sample in ["Run2015D_JetHT"]:
    print sample
    f = ROOT.TFile.Open("plots/JetHT/"+sample+".root")
    h_den = f.Get("Had_MT_MinPt100_DH1p6/Had_MT_MinPt100_DH1p6_MassFSR")
    [bin_l,bin_h] = [h_den.FindBin( window[0] ), h_den.FindBin( window[1] )]
    den = h_den.Integral(bin_l,bin_h)
    data_den += den
    h_num = f.Get("Had_MT_MinPt100_HLT_DH1p6/Had_MT_MinPt100_HLT_DH1p6_MassFSR")
    [bin_l,bin_h] = [h_num.FindBin( window[0] ), h_num.FindBin( window[1] )]
    num = h_num.Integral(bin_l,bin_h)
    data_num += num
    f.Close()

print ("QCD: %.1f/%.1f = %.3f +/- %.3f --- DATA: %.1f/%.1f = %.3f +/- %.3f ==> data/mc = %.2f +/- %.2f%%" % (qcd_num, qcd_den, qcd_num/qcd_den, 
                                                                                                           (math.sqrt((qcd_num/qcd_den)*(1-qcd_num/qcd_den)/qcd_den)/(qcd_num/qcd_den) + math.sqrt(qcd_den_err)/qcd_den + math.sqrt(qcd_num_err)/qcd_num)*(qcd_num/qcd_den),
                                                                                                           data_num, data_den, data_num/data_den, math.sqrt(data_num/data_den*(1-data_num/data_den)/data_den),
                                                                                                           (data_num/data_den)/(qcd_num/qcd_den), 
                                                                                                           math.sqrt(data_num/data_den*(1-data_num/data_den)/data_den)/(data_num/data_den))
       )
    

