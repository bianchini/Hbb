from sys import argv
argv.append( '-b-' )
import ROOT
ROOT.gROOT.SetBatch(True)
argv.remove( '-b-' )

import math
import sys
sys.path.append('./')
sys.path.append('../python/')

from parameters_cfi import luminosity

def is_blind():
    return False

def k_factor_QCD():
    return 1.53
    #return 1.

def get_extra_SF():
    # this is to match new lumi 2.69/2.63
    return 1.0228
    #return 1.

def get_samples():
    samples = ["Run2015",
               "TT_ext3",
               "ST_t_atop",
               "ST_t_top",
               "ST_tW_atop",
               "ST_tW_top", 
               "HT100to200", 
               "HT200to300", 
               "HT300to500", 
               "HT500to700", 
               "HT700to1000", 
               "HT1000to1500", 
               "HT1500to2000", 
               "HT2000toInf",
               "Spin0_M550",
               "Spin0_M600",
               "Spin0_M650",
               "Spin0_M700",
               "Spin0_M750",
               "Spin0_M800",
               "Spin0_M850",
               "Spin0_M900",
               "Spin0_M1000",
               "Spin0_M1100",
               "Spin0_M1200",
               "Spin2_M550",
               "Spin2_M600",
               "Spin2_M650",
               "Spin2_M700",
               "Spin2_M750",
               "Spin2_M800",
               "Spin2_M850",
               "Spin2_M900",
               "Spin2_M1000",
               "Spin2_M1100",
               "Spin2_M1200",
               ]
    return samples

def plot( files={}, dir_name = "Had_LT_MinPt150_DH2p0", h_name = "Pt", var_name="p_{T}^{X}", postfix = "", option_signal = "HIST", option_bkg = "PE", option_data = "PE", option_shape = "", out_name = "plot", version = "V3"):
    
    out = ROOT.TFile.Open("/scratch/bianchi/"+version+"/"+out_name+".root", "UPDATE")
    if out!=None and out.IsZombie():
        print "Remove file because is corrupted" 
        os.system('rm /scratch/bianchi/'+version+'/'+out_name+'.root')
        out = ROOT.TFile.Open("/scratch/bianchi/"+version+"/"+out_name+".root", "RECREATE")

    table = None
    if option_shape!="Shape":
        table = open( "/scratch/bianchi/"+version+"/yield_"+dir_name+".txt", 'w')

    s = ROOT.THStack("stack_background_"+h_name,"")
    s.SetTitle("")

    leg = ROOT.TLegend(0.46,0.44,0.85,0.88, "","brNDC");
    leg.SetFillStyle(0);
    leg.SetBorderSize(0);
    leg.SetTextSize(0.05);
    leg.SetFillColor(10);
    region = ""
    if "Had_LT" in dir_name:
        region = "X #rightarrow b#bar{b}, preselection"
    elif "Had_MT" in dir_name:
        region = "X #rightarrow b#bar{b}, signal region"
    elif "Lep_LT" in dir_name:
        region = "X #rightarrow b#bar{b}, top-quark sideband"    
    leg.SetHeader(region)

    hdata = []
    hsignal = []
    hqcd = []
    htop = []
    hbackground = []

    do_rebin = False
    new_ranges = [0,1]
    new_bin_width = 1
    if "Lep" in dir_name and "Mass" in h_name and ("toMass" not in h_name and "vsMass" not in h_name):
        do_rebin = True
        new_ranges = [374,2002]
        new_bin_width = 37
    if "Had_LT" in dir_name and "Mass" in h_name and ("toMass" not in h_name and "vsMass" not in h_name):
        do_rebin = True
        new_ranges = [374,4000]
        new_bin_width = 37*2
    if "Had_MT" in dir_name and "Mass" in h_name and ("toMass" not in h_name and "vsMass" not in h_name) and is_blind():
        do_rebin = True
        new_ranges = [374,4000]
        new_bin_width = 37
    if "vsMass" in h_name:
        do_rebin = True
        new_ranges = [0,2000]
        new_bin_width = 40 #80

    for ns,sample in enumerate( get_samples() ):
        
        f = files[sample]

        count = f.Get("Count").GetBinContent(1)
        h_sample = f.Get(dir_name+"/"+h_name).Clone(h_name+"_clone")
        if h_sample==None:
            continue

        if do_rebin:
            orig_bin_width = h_sample.GetBinWidth(1)
            h_sample.Rebin(int(new_bin_width/orig_bin_width))    

        need_to_blind = False
        if "Had" in dir_name and "Mass" in h_name and "toMass" not in h_name and is_blind():
            need_to_blind = True

        if "Run2015" in sample:
            data = h_sample.Clone("data_"+h_name)
            data.SetDirectory(0)
            data.SetMarkerColor(ROOT.kBlack);
            data.SetLineColor(ROOT.kBlack);
            data.SetMarkerSize(1.0);
            data.SetMarkerStyle(ROOT.kFullCircle);
            data.SetFillColor(0);
            hdata.append( data )
            print "Processed sample n.%.0f %s: %.1f" % (ns,sample, h_sample.Integral()) 
            continue

        # needed because of automatic nornalisation
        h_sample.Scale(1./count)
        
        # any extra scale factors that applies to all simulations
        h_sample.Scale(get_extra_SF())
        
        if "Spin" in sample:
            signal = h_sample.Clone("signal_"+h_name+"_"+sample+option_shape)
            signal.SetDirectory(0)
            signal.SetLineColor(ROOT.kRed if "Spin0" in sample else ROOT.kBlue)
            signal.SetLineStyle(ROOT.kSolid if "Spin0" in sample else ROOT.kDashed)
            signal.SetLineWidth(3)
            hsignal.append( [signal, sample] )
            
        elif "HT" in sample:
            ht = h_sample.Clone("qcd_"+h_name)
            ht.SetDirectory(0)
            ht.Scale( k_factor_QCD() )
            ht.SetFillColor(33)
            ht.SetLineColor(33)
            ht.SetLineWidth(0) 
            ht.SetFillStyle(1001)
            s.Add(ht)
            hqcd.append(ht)
            hbackground.append(ht)

        elif "TT_" in sample or "ST_" in sample:
            top = h_sample.Clone("top_"+h_name)
            top.SetDirectory(0)
            #top.SetFillColor(ROOT.kBlue-7)
            #top.SetLineColor(ROOT.kBlue-7)
            top.SetFillColor(38)
            top.SetLineColor(38)
            top.SetLineWidth(0) 
            top.SetFillStyle(1001)
            s.Add(top)
            htop.append(top)
            hbackground.append(top)
            
        else:
            print "Not a valud process..."
            continue

        print "Processed sample n.%.0f %s: %.1f" % (ns,sample, h_sample.Integral()) 

    if need_to_blind:
        leg.AddEntry(data, "Data = Bkg. (blinded)", "PE")
    else:
        leg.AddEntry(data, "Data", "PE")

    qcd = hqcd[0].Clone("qcd_all_"+h_name)
    qcd.SetLineColor(33)
    qcd.SetLineWidth(1)
    qcd.SetFillColor(33);
    qcd.SetFillStyle(1001);
    leg.AddEntry(qcd, "Multijet bkg. (#times%.2f)" % k_factor_QCD(), "F");
    qcd.Reset();
    for h in hqcd:
        qcd.Add(h,1.0)

    top = htop[0].Clone("top_all_"+h_name)
    #top.SetLineColor(ROOT.kBlue-7)
    top.SetLineColor(38)
    top.SetLineWidth(2)
    #top.SetFillColor(0);
    leg.AddEntry(top, "Top bkg.", "F");
    top.Reset();
    for h in htop:
        top.Add(h,1.0)

    background = hbackground[0].Clone("background_"+h_name)
    background.SetLineColor(ROOT.kWhite)
    background.SetLineWidth(0)
    background.SetMarkerStyle(ROOT.kFullCircle)
    background.SetMarkerSize(0.)
    background.SetFillColor(ROOT.kBlue)
    background.SetFillStyle(3004);
    leg.AddEntry(background, "Bkg. stat. unc.", "F");
    background.Reset();
    for h in hbackground:
        background.Add(h,1.0)

    c = ROOT.TCanvas("c_"+dir_name+"_"+h_name, "canvas", 600, 600) 

    pad1 = ROOT.TPad("pad1", "pad1", 0.02, 0.30, 1, 1.0)    
    pad1.SetLeftMargin(0.13)
    #pad1.SetBottomMargin(0.03)
    pad1.Draw()
    pad1.cd()    

    s.SetMinimum( hsignal[0][0].GetMinimum()*0.5 + 0.01 )
    s.SetMaximum( max(data.GetMaximum(), background.GetMaximum())*(2.0 if option_shape=="Shape" else math.exp(2*math.log(max(data.GetMaximum(), background.GetMaximum())) ) ) )
    s.Draw("HIST")
    if(s.GetHistogram()!=None):
        s.GetHistogram().SetXTitle(h_name.split('_')[-1])
        s.GetHistogram().SetYTitle("Events/Bin")
        s.GetHistogram().SetTitle(dir_name)
        if do_rebin:
            s.GetHistogram().GetXaxis().SetLimits(new_ranges[0],new_ranges[1])
        s.GetHistogram().GetYaxis().SetTitleSize(24)
        s.GetHistogram().GetYaxis().SetTitleFont(43)
        s.GetHistogram().GetYaxis().SetTitleOffset(1.32)
        s.GetHistogram().GetYaxis().SetLabelFont(43)
        s.GetHistogram().GetYaxis().SetLabelSize(20)
        s.GetHistogram().GetXaxis().SetLabelSize(0)

    for signal in hsignal:
        mass = float(signal[1][7:])
        spin = float(signal[1][4])
        if "M750" not in signal[1]:
            continue
        #if "Lep" in dir_name and option_shape=="Shape":
        if "Lep" in dir_name:
            signal[0].SetLineColor(ROOT.kWhite)
            leg.AddEntry(signal[0], " ", "L")
            continue
        if option_shape=="Shape":
            signal[0].Scale(background.Integral()/signal[0].Integral() if signal[0].Integral()>0. else 1.0)
            #leg.AddEntry(signal[0], ('Spin-%.0f, m_{X}=%.0f GeV' % (spin,mass))+" norm. to bkg.", "L") 
            leg.AddEntry(signal[0], ('Spin-%.0f, m_{X}=%.0f GeV' % (spin,mass)), "L") 
        else:
            #leg_entry = leg.AddEntry(signal[0], ('Spin-%.0f, m_{X}=%.0f GeV' % (spin,mass))+", #sigma=1pb", "L")
            leg_entry = leg.AddEntry(signal[0], ('Spin-%.0f, m_{X}=%.0f GeV' % (spin,mass)), "L")
        signal[0].Draw(option_signal+"SAME")

    background.Draw(option_bkg+"E2SAME")
    if need_to_blind:
        data.Reset()
        data.Add(background, 1.0)
    data.Draw(option_data+"SAME")

    #if s.GetHistogram()!=None :
    #    s.GetHistogram().GetYaxis().SetTitleSize(20)
    #    s.GetHistogram().GetYaxis().SetTitleFont(43)
    #    s.GetHistogram().GetYaxis().SetTitleOffset(1.35)
    pave_cms = ROOT.TPaveText(0.16,0.82,0.42,0.89, "NDC")
    pave_cms.SetFillStyle(0);
    pave_cms.SetBorderSize(0);
    pave_cms.SetTextAlign(12)
    pave_cms.SetTextSize(0.06)
    #pave_cms.SetTextFont(61)
    pave_cms.AddText("CMS")
    pave_prel = ROOT.TPaveText(0.16,0.75,0.42,0.82, "NDC")
    pave_prel.SetFillStyle(0);
    pave_prel.SetBorderSize(0);
    pave_prel.SetTextAlign(12)
    pave_prel.SetTextSize(0.045)
    pave_prel.SetTextFont(52)
    pave_prel.AddText("Preliminary")
    pave_lumi = ROOT.TPaveText(0.484,0.90,0.92,0.96, "NDC")
    pave_lumi.SetFillStyle(0);
    pave_lumi.SetBorderSize(0);
    pave_lumi.SetTextAlign(32)
    pave_lumi.SetTextSize(0.05)
    pave_lumi.SetTextFont(42)
    pave_lumi.AddText(("%.2f fb^{-1} (2015)" % luminosity))

    if option_shape!="Shape":
        pad1.SetLogy(1)
    pad1.SetBottomMargin(0.01) 

    pad1.Draw()      
    pave_cms.Draw("same")
    pave_prel.Draw("same")
    pave_lumi.Draw("same")
    leg.Draw();
    c.Modified()

    c.cd() 
    pad2 = ROOT.TPad("pad2", "pad2", 0.02, 0.02, 1, 0.28)
    pad2.SetTopMargin(0.05)
    pad2.SetBottomMargin(0.37)
    pad2.SetLeftMargin(0.13)
    #pad2.SetGridy() 
    pad2.Draw()
    pad2.cd()       

    hratio = data.Clone("data_clone")
    hratio.SetLineColor(ROOT.kBlack)
    hratio.SetMinimum(0.) 
    hratio.SetMaximum(2) 
    hratio.SetStats(0) 
    hratio.Divide(background)
    hratio.SetMarkerStyle(ROOT.kFullCircle)
    if do_rebin:
        hratio.GetXaxis().SetRangeUser(new_ranges[0],new_ranges[1])
    hratio.Draw("ep") 
    hratio.SetTitle("") 
    hratio.GetYaxis().CenterTitle()
    hratio.GetYaxis().SetTitle("Data/Bkg.")
    hratio.GetYaxis().SetNdivisions(505)
    hratio.GetYaxis().SetTitleSize(25)
    hratio.GetYaxis().SetTitleFont(43)
    hratio.GetYaxis().SetTitleOffset(1.18)
    hratio.GetYaxis().SetLabelFont(43) 
    hratio.GetYaxis().SetLabelSize(20)
    hratio.GetXaxis().SetTitle(var_name)
    hratio.GetXaxis().SetTitleSize(25)
    hratio.GetXaxis().SetTitleFont(43)
    hratio.GetXaxis().SetTitleOffset(3.5)
    hratio.GetXaxis().SetLabelFont(43) 
    hratio.GetXaxis().SetLabelSize(20)

    hratioErr = background.Clone("hratioErr")
    for b in range(hratioErr.GetNbinsX()+1):
        val = hratioErr.GetBinContent(b+1)
        err = hratioErr.GetBinError(b+1)
        hratioErr.SetBinContent(b+1,1.0)
        hratioErr.SetBinError(b+1, err/val if val>0. else 0.)
    if do_rebin:
        hratioErr.GetXaxis().SetRangeUser(new_ranges[0],new_ranges[1])
    hratioErr.Draw(option_bkg+"E2SAME")

    line = ROOT.TF1("line", "1.0", hratio.GetXaxis().GetXmin(), hratio.GetXaxis().GetXmax())
    line.SetLineWidth(2)
    line.SetLineStyle(ROOT.kDashed)
    line.SetLineColor(ROOT.kBlack)
    line.Draw("same")

    #raw_input()

    for ext in ["png", "pdf"]:
        c.SaveAs("/scratch/bianchi/"+version+"/"+h_name+postfix+"."+ext)  
  
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

    # save yields in latex table
    if table!=None:
        table.write('\\begin{table}[htbH]\n')
        table.write('\\begin{center}\n')
        table.write('\caption{Expected and observed event yields after preselection.}\n')
        table.write('\\begin{tabular}{| c | c |}\n')
        table.write('\hline\n')
        qcd_yield = qcd.Integral()/k_factor_QCD()
        qcd_yield_err = ROOT.Double()
        qcd.IntegralAndError(0, qcd.GetNbinsX()+1, qcd_yield_err)
        top_yield = top.Integral()
        top_yield_err = ROOT.Double()
        top.IntegralAndError(0, top.GetNbinsX()+1, top_yield_err) 
        table.write(('Multi-jet & $%.2E \\pm %.0E$ \\\\\n' % (qcd_yield, qcd_yield_err)))
        table.write(('Top & $%.0f \\pm %.0f$ \\\\\n' % (top_yield,top_yield_err)))
        table.write('\hline\n')
        table.write(('Data & %.0f \\\\\n' % data.Integral()))
        table.write('\hline\n')
        table.write('\hline\n')
        table.write('Signal process & $\epsilon\\times\mathcal{A}$ \\\\\n')
        table.write('\hline\n')
        for nh,h in enumerate(hsignal):
            name = h[1]
            mass = float(name[7:])
            spin = float(name[4])
            sgn_yield = h[0].Integral()
            sgn_yield_err = ROOT.Double()
            h[0].IntegralAndError(0, h[0].GetNbinsX()+1, sgn_yield_err) 
            table.write(('$m_{X}(J=%.0f)=%.0f$ GeV & $%.3f \\pm %.3f$ \\\\\n' % (spin, mass, sgn_yield/2630., sgn_yield_err/2630.)))
            table.write('\hline\n') 
        table.write('\end{tabular}\n')
        table.write('\end{center}\n')
        table.write('\end{table}\n')
        table.close()

    # close the file
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

def plot_all( version = "V7" ):

    files = {}
    for ns,sample in enumerate( get_samples() ):    
        f = ROOT.TFile.Open("./plots/"+version+"/"+sample+".root", "READ"); 
        if f==None or f.IsZombie():
            print "No file"
            continue
        files[sample] = f

    for cat_btag in ["Had_LT", 
                     "Had_MT", 
                     #"Had_TT",
                     "Lep_LT",
                     #"All"
                     ]:
        for cat_kin in [
            #"MinPt150_DH2p0", 
            #"MinPt150_DH1p6", 
            "MinPt100_DH2p0", 
            "MinPt100_DH1p6", 
            #"MinPt100_HLTKinUp_DH1p6", 
            #"MinPt100_HLTKinDown_DH1p6", 
            #"MinMaxPt100150_DH1p6"
            #"MinPt150_DH1p1",
            #"MinPt175_DH2p0", "MinPt175_DH1p6", "MinPt175_DH1p1",
            #"MinPt200_DH2p0", "MinPt200_DH1p6", "MinPt200_DH1p1",
            ""
            ]:            
            for syst in ["", 
                         "_CSVSFUp", "_CSVSFDown"
                         ]:

                if cat_btag != "All" and (cat_kin==""):
                    continue
                if cat_btag == "All" and (cat_kin!="" or syst!=""):
                    continue

                if "Kin" in cat_kin and not (cat_btag=="Had_MT"):
                    continue

                if cat_btag=="Lep_LT" and (syst!="" or cat_kin!="MinPt100_DH2p0"):
                    continue
                if cat_btag=="Had_LT" and (syst!="" or cat_kin!="MinPt100_DH2p0"):
                    continue
                if cat_btag=="Had_MT" and cat_kin not in ["MinPt100_HLTKinUp_DH1p6","MinPt100_HLTKinDown_DH1p6","MinPt100_DH1p6"]:
                    continue

                for hist in [    
                    ["Eff_HLTHigh_vsMassFSR", "m_{b#bar{b}} (HLT-high & !HLT-low) (GeV)"],
                    ["MassFSR", "m_{b#bar{b}} (GeV)"],
                    ["MassFSR_JECUp", "m_{b#bar{b}} JEC up (GeV)"],
                    ["MassFSR_JECDown","m_{b#bar{b}} JEC down (GeV)"],
                    ["MassFSR_JERUp","m_{b#bar{b}} JER up GeV)"],
                    ["MassFSR_JERDown","m_{b#bar{b}} JER down (GeV)"],
                    ["MassFSRProjMET", "m_{b#bar{b}} (FSR + MET) (GeV)"],
                    ["MinJetPt", "Min(p_{T}^{b1}, p_{T}^{b2}) (GeV)"],
                    ["MaxJetPt", "Max(p_{T}^{b1}, p_{T}^{b2}) (GeV)"],
                    ["Mass", "m_{b#bar{b}} (R=0.4) (GeV)"],
                    ["MassAK08", "m_{b#bar{b}} (R=0.8) (GeV)"],
                    ["Pt", "p_{T}^{X} (GeV)"],
                    ["Eta","#eta^{X}"],
                    ["DeltaPhi","#Delta#phi_{b#bar{b}}"],
                    ["MaxJetCSV","max(CSV_{b1},CSV_{b2})"],
                    ["MinJetCSV","min(CSV_{b1},CSV_{b2})"],
                    ["Vtype","event type"],
                    ["njet30","Multiplicity of jets with p_{T}>30 GeV"],
                    ["njet50","Multiplicity of jets with p_{T}>50 GeV"],
                    ["njet70","Multiplicity of jets with p_{T}>70 GeV"],
                    ["njet100","Multiplicity of jets with p_{T}>100 GeV"],
                    ["MET","E_{T}^{miss} (GeV)"],
                    ["PtBalance","|p_{T}^{b1}-p_{T}^{b2}|/(p_{T}^{b1}+p_{T}^{b2})"],
                    ["MaxJetPtoMass", "Max(p_{T}^{b1}, p_{T}^{b2})/m_{b#bar{b}}"],
                    ["MinJetPtoMass","Min(p_{T}^{b1}, p_{T}^{b2})/m_{b#bar{b}}"],
                    ["MaxEta","Max(#eta^{b1}, #eta^{b2})"],
                    ["DeltaEta","|#Delta#eta_{b#bar{b}}|"],
                    ]:

                    if (("_JEC" in hist[0]) or ("_JER" in hist[0])) and (syst!="" or cat_btag!="Had_MT" or cat_kin!="MinPt100_DH1p6"):
                        continue
                    if ("Mass" not in hist[0]) and (syst!=""):
                        continue

                    cat = cat_btag+syst+"_"+cat_kin if cat_btag!="All" else cat_btag
                    print cat
                    plot(files=files, dir_name=cat, h_name=cat+"_"+hist[0], var_name=hist[1], postfix="",       option_signal="HIST", option_bkg="PE", option_data="PE", option_shape="",      out_name="plot", version=version)
                    #exit(1)
                    plot(files=files, dir_name=cat, h_name=cat+"_"+hist[0], var_name=hist[1], postfix="_shape", option_signal="HIST", option_bkg="PE", option_data="PE", option_shape="Shape", out_name="plot", version=version)


    for f in files.keys():
        files[f].Close()

#############################

plot_all( version = "PostPreApproval/" )
