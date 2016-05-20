from sys import argv
argv.append( '-b-' )
import ROOT
ROOT.gROOT.SetBatch(True)
argv.remove( '-b-' )

import math
import sys
sys.path.append('./')

def is_blind():
    return False

def k_factor_QCD():
    return 1.45

def get_samples():
    samples = ["Run2015",
               "HT100to200", 
               "HT200to300", 
               "HT300to500", 
               "HT500to700", 
               "HT700to1000", 
               "HT1000to1500", 
               "HT1500to2000", 
               "HT2000toInf",
               "TT_ext3",
               "ST_t_atop",
               "ST_t_top",
               "ST_tW_atop",
               "ST_tW_top", 
               "Spin0_M650",
               "Spin0_M750",
               "Spin0_M850",
               "Spin0_M1000",
               "Spin0_M1200",
               "Spin2_M650",
               "Spin2_M750",
               "Spin2_M850",
               "Spin2_M1000",
               "Spin2_M1200",
               ]
    return samples

def plot( files={}, dir_name = "Had_LT_MinPt150_DH2p0", h_name = "Pt", postfix = "", option_signal = "HIST", option_bkg = "PE", option_data = "PE", option_shape = "", out_name = "plot", version = "V3"):
    
    out = ROOT.TFile.Open("/scratch/bianchi/"+version+"/"+out_name+".root", "UPDATE")
    if out!=None and out.IsZombie():
        print "Remove file because is corrupted" 
        os.system('rm /scratch/bianchi/'+version+'/'+out_name+'.root')
        out = ROOT.TFile.Open("/scratch/bianchi/"+version+"/"+out_name+".root", "RECREATE")

    s = ROOT.THStack("stack_background_"+h_name,"");

    leg = ROOT.TLegend(0.45,0.55,0.80,0.88, "","brNDC");
    leg.SetHeader("#splitline{CMS Preliminary 2015, L=2.63 fb^{-1}}{Selection: "+dir_name+"}");
    leg.SetFillStyle(0);
    leg.SetBorderSize(0);
    leg.SetTextSize(0.03);
    leg.SetFillColor(10);

    hdata = []
    hsignal = []
    hqcd = []
    htop = []
    hbackground = []

    for ns,sample in enumerate( get_samples() ):
        
        f = files[sample]

        count = f.Get("Count").GetBinContent(1)
        h_sample = f.Get(dir_name+"/"+h_name).Clone(h_name+"_clone")
        if h_sample==None:
            continue

        if "Lep" in dir_name and "Mass" in h_name and "toMass" not in h_name:
            h_sample.Rebin(500 if "MassFSR" in h_name else 10)

        if "Run2015" in sample:
            data = h_sample.Clone("data_"+h_name)
            data.SetDirectory(0)
            data.SetMarkerColor(ROOT.kBlack);
            data.SetLineColor(ROOT.kBlack);
            data.SetMarkerSize(1.2);
            data.SetMarkerStyle(ROOT.kFullCircle);
            data.SetFillColor(0);
            hdata.append( data )
            print "Processed sample n.%.0f %s: %.1f" % (ns,sample, h_sample.Integral()) 
            continue

        h_sample.Scale(1./count)
        
        if "Spin" in sample:
            signal = h_sample.Clone("signal_"+h_name+"_"+sample+option_shape)
            signal.SetDirectory(0)
            signal.SetLineColor(ROOT.kRed if "Spin0" in sample else ROOT.kBlue)
            signal.SetLineStyle(ROOT.kDashed)
            signal.SetLineWidth(3)
            hsignal.append( [signal, sample] )
            
        elif "HT" in sample:
            ht = h_sample.Clone("qcd_"+h_name)
            ht.SetDirectory(0)
            ht.Scale( k_factor_QCD() )
            ht.SetFillColor(ns+30)
            ht.SetLineColor(ns+30)
            ht.SetLineWidth(0) 
            ht.SetFillStyle(1001)
            s.Add(ht)
            hqcd.append(ht)
            hbackground.append(ht)

        elif "TT_" in sample or "ST_" in sample:
            top = h_sample.Clone("top_"+h_name)
            top.SetDirectory(0)
            top.SetFillColor(ROOT.kMagenta)
            top.SetLineColor(ROOT.kMagenta)
            top.SetLineWidth(0) 
            top.SetFillStyle(1001)
            s.Add(top)
            htop.append(top)
            hbackground.append(top)
            
        else:
            print "Not a valud process..."
            continue

        print "Processed sample n.%.0f %s: %.1f" % (ns,sample, h_sample.Integral()) 


    qcd = hqcd[0].Clone("qcd_all_"+h_name)
    qcd.SetLineColor(ROOT.kBlack)
    qcd.SetLineWidth(2)
    qcd.SetFillColor(0);
    leg.AddEntry(qcd, "Multi-jet, K-factor=%.1f" % k_factor_QCD(), "L");
    qcd.Reset();
    for h in hqcd:
        qcd.Add(h,1.0)

    top = htop[0].Clone("top_all_"+h_name)
    top.SetLineColor(ROOT.kMagenta)
    top.SetLineWidth(2)
    top.SetFillColor(0);
    leg.AddEntry(top, "Top", "L");
    top.Reset();
    for h in htop:
        top.Add(h,1.0)

    background = hbackground[0].Clone("background_"+h_name)
    background.SetLineColor(ROOT.kGray)
    background.SetLineWidth(2)
    background.SetMarkerStyle(ROOT.kFullCircle)
    background.SetMarkerSize(0.)
    background.SetFillColor(ROOT.kBlue)
    background.SetFillStyle(3004);
    leg.AddEntry(background, "Total background", "F");
    background.Reset();
    for h in hbackground:
        background.Add(h,1.0)

    c = ROOT.TCanvas("c_"+dir_name+"_"+h_name, "canvas", 600, 600) 
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1.0)     
    if option_shape!="Shape":
        pad1.SetLogy(1)
    pad1.SetBottomMargin(0) 
    pad1.SetGridx()  
    pad1.Draw()      
    pad1.cd()    

    s.SetMinimum( hsignal[0][0].GetMinimum()*0.5 + 0.01 )
    s.SetMaximum( max(data.GetMaximum()*1.5, background.GetMaximum()*1.5) )
    s.Draw("HIST")
    if(s.GetHistogram()!=None):
        s.GetHistogram().SetXTitle(h_name.split('_')[-1])
        s.GetHistogram().SetTitle(dir_name)

    for signal in hsignal:
        if "M750" not in signal[1]:
            continue
        if option_shape=="Shape":
            signal[0].Scale(background.Integral()/signal[0].Integral() if signal[0].Integral()>0. else 1.0)
            leg.AddEntry(signal[0], signal[1]+" normalised to Bkg.", "L") 
        else:
            leg.AddEntry(signal[0], signal[1]+" , #sigma=1.0 pb", "L")
        signal[0].Draw(option_signal+"SAME")

    background.Draw(option_bkg+"E2SAME")
    if is_blind():
        data.Reset()
        data.Add(background, 1.0)
        leg.AddEntry(data, "Data = MC (blinded)", "PE")
        data.Draw(option_data+"SAME");  
    else:
        data.Draw(option_data+"SAME")
        leg.AddEntry(data, "Data", "PE"); 

    if s.GetHistogram()!=None :
        s.GetHistogram().GetYaxis().SetTitleSize(20)
        s.GetHistogram().GetYaxis().SetTitleFont(43)
        s.GetHistogram().GetYaxis().SetTitleOffset(1.55)
  
    leg.Draw();

    c.cd() 
    pad2 = ROOT.TPad("pad2", "pad2", 0, 0.05, 1, 0.3)
    pad2.SetTopMargin(0)
    pad2.SetBottomMargin(0.2)
    pad2.SetGridx()   
    pad2.SetGridy() 
    pad2.Draw()
    pad2.cd()       

    hratio = data.Clone("data_clone")
    hratio.SetLineColor(ROOT.kBlack)
    hratio.SetMinimum(0.) 
    hratio.SetMaximum(2) 
    hratio.SetStats(0) 
    hratio.Divide(background)
    hratio.SetMarkerStyle(21)
    hratio.Draw("ep") 
    hratio.SetTitle("") 
    hratio.GetYaxis().SetTitle("data/MC")
    hratio.GetYaxis().SetNdivisions(505)
    hratio.GetYaxis().SetTitleSize(20)
    hratio.GetYaxis().SetTitleFont(43)
    hratio.GetYaxis().SetTitleOffset(1.35)
    hratio.GetYaxis().SetLabelFont(43) 
    hratio.GetYaxis().SetLabelSize(15)
    hratio.GetXaxis().SetTitle(h_name.split('_')[4])
    hratio.GetXaxis().SetTitleSize(20)
    hratio.GetXaxis().SetTitleFont(43)
    hratio.GetXaxis().SetTitleOffset(4.)
    hratio.GetXaxis().SetLabelFont(43) 
    hratio.GetXaxis().SetLabelSize(15)
    hratioErr = background.Clone("hratioErr")
    for b in range(hratioErr.GetNbinsX()+1):
        val = hratioErr.GetBinContent(b+1)
        err = hratioErr.GetBinError(b+1)
        hratioErr.SetBinContent(b+1,1.0)
        hratioErr.SetBinError(b+1, err/val if val>0. else 0.)
    hratioErr.Draw(option_bkg+"E2SAME")

    c.SaveAs("/scratch/bianchi/"+version+"/"+h_name+postfix+".png")  
  
    out.cd()
    # save only once
    if option_shape!="Shape":
        if not out.cd(dir_name):
            out.mkdir(dir_name)
            out.cd(dir_name)
        for h in hsignal:
            h[0].Write("", ROOT.TObject.kOverwrite)
        background.Write("", ROOT.TObject.kOverwrite)
        top.Write("", ROOT.TObject.kOverwrite)
        qcd.Write("", ROOT.TObject.kOverwrite)
        data.Write("", ROOT.TObject.kOverwrite)
        #s.Write("", ROOT.TObject.kOverwrite);

    out.Close()

    ROOT.gDirectory.Remove(c)
    ROOT.gDirectory.Remove(pad1)
    ROOT.gDirectory.Remove(pad2)
    ROOT.gDirectory.Remove(s)
    for h in hsignal:
        ROOT.gDirectory.Remove(h[0])
    for h in hbackground:
        ROOT.gDirectory.Remove(h)
    for h in hdata:
        ROOT.gDirectory.Remove(h)


########################################################

def plot_all( version = "V5" ):

    files = {}
    for ns,sample in enumerate( get_samples() ):    
        f = ROOT.TFile.Open("./plots/"+version+"/"+sample+".root", "READ"); 
        if f==None or f.IsZombie():
            print "No file"
            continue
        files[sample] = f

    for cat_btag in [#"Had_LT", 
                     "Had_MT", 
                     #"Had_TT",
                     #"Lep_LT"
                     ]:
        for cat_kin in [
            #"MinPt150_DH2p0", 
            "MinPt150_DH1p6", "MinPt100_DH1p6", "MinMaxPt100150_DH1p6"
            #"MinPt150_DH1p1",
            #"MinPt175_DH2p0", "MinPt175_DH1p6", "MinPt175_DH1p1",
            #"MinPt200_DH2p0", "MinPt200_DH1p6", "MinPt200_DH1p1",
            ]:            
            for syst in ["", 
                         "_CSVSFUp", "_CSVSFDown"
                         ]:
                if cat_btag=="Lep_LT" and syst!="":
                    continue
                for hist in [    
                    "MassFSR",
                    "MassFSR_JECUp",
                    "MassFSR_JECDown",
                    "MassFSR_JERUp",
                    "MassFSR_JERDown",
                    #"MinJetPt",
                    #"MaxJetPt",
                    #"Mass",
                    #"MassAK08",
                    #"Pt",
                    #"Eta",
                    #"DeltaEta",
                    #"DeltaPhi",
                    #"MaxJetCSV",
                    #"MinJetCSV",
                    #"Vtype",
                    #"njet30",
                    #"njet50",
                    #"njet70",
                    #"njet100",
                    #"MET",
                    #"PtBalance",
                    #"MaxJetPtoMass",
                    #"MinJetPtoMass",
                    #"MaxEta",
                    ]:
                    cat = cat_btag+syst+"_"+cat_kin
                    plot(files=files, dir_name=cat, h_name=cat+"_"+hist, postfix="",       option_signal="HIST", option_bkg="PE", option_data="PE", option_shape="",      out_name="plot", version=version)
                    plot(files=files, dir_name=cat, h_name=cat+"_"+hist, postfix="_shape", option_signal="HIST", option_bkg="PE", option_data="PE", option_shape="Shape", out_name="plot", version=version)
                    #exit(1)

    for f in files.keys():
        files[f].Close()

#############################

plot_all()
