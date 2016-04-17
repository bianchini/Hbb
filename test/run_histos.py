from sys import argv
argv.append( '-b-' )
import ROOT
ROOT.gROOT.SetBatch(True)
argv.remove( '-b-' )
from ROOT import TLorentzVector
import math

def weight(ev, lumi):
  if lumi<0:
    return 1.0
  return ev.puWeight*abs(ev.genWeight)/ev.genWeight*lumi


samples = {
  "Run2015D" : ["root://stormgf1.pi.infn.it:1094//store/user/arizzi/VHBBHeppyV21//BTagCSV//VHBB_HEPPY_V21_BTagCSV__Run2015D-16Dec2015-v1/160317_132347/0000/", -1],
  "HT100to200" : ["root://stormgf1.pi.infn.it:1094//store/user/arizzi/VHBBHeppyV21/QCD_HT100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/VHBB_HEPPY_V21_QCD_HT100to200_TuneCUETP8M1_13TeV-madgraphMLM-Py8__fall15MAv2-pu25ns15v1_76r2as_v12-v1/160316_144616/0000/", 27990000],
  "HT200to300" : ["root://stormgf1.pi.infn.it:1094//store/user/arizzi/VHBBHeppyV21//QCD_HT200to300_TuneCUETP8M1_13TeV-madgraphMLM-pythia8//VHBB_HEPPY_V21_QCD_HT200to300_TuneCUETP8M1_13TeV-madgraphMLM-Py8__fall15MAv2-pu25ns15v1_76r2as_v12-v1/160316_151338/0000/", 1712000.],
  "HT300to500" :   ["root://stormgf1.pi.infn.it:1094//store/user/arizzi/VHBBHeppyV21/QCD_HT300to500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/VHBB_HEPPY_V21_QCD_HT300to500_TuneCUETP8M1_13TeV-madgraphMLM-Py8__fall15MAv2-pu25ns15v1_76r2as_v12-v1/160321_090315/0000/",347700.],
  "HT500to700" :   ["root://stormgf1.pi.infn.it:1094//store/user/arizzi/VHBBHeppyV21/QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/VHBB_HEPPY_V21_QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-Py8__fall15MAv2-pu25ns15v1_76r2as_v12-v1/160316_144548/0000/", 32100.],
  "HT700to1000" :  ["root://stormgf1.pi.infn.it:1094//store/user/arizzi/VHBBHeppyV21/QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8//VHBB_HEPPY_V21_QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-Py8__fall15MAv2-pu25ns15v1_76r2as_v12-v1//160321_090740/0000/", 6831.],
  "HT1000to1500" : ["root://stormgf1.pi.infn.it:1094//store/user/arizzi/VHBBHeppyV21/QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/VHBB_HEPPY_V21_QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-Py8__fall15MAv2-pu25ns15v1_76r2as_v12-v1//160316_151306/0000/", 1207.],
  "HT1500to2000" : ["root://stormgf1.pi.infn.it:1094//store/user/arizzi/VHBBHeppyV21/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/VHBB_HEPPY_V21_QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-Py8__fall15MAv2-pu25ns15v1_76r2as_v12-v1//160316_144454//0000/",119.9],
  "HT2000toInf" :  ["root://stormgf1.pi.infn.it:1094//store/user/arizzi/VHBBHeppyV21/QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8//VHBB_HEPPY_V21_QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-Py8__fall15MAv2-pu25ns15v1_76r2as_v12-v1//160316_144521/0000/", 25.24], 
  "M750" : ["root://eoscms.cern.ch//eos/cms/store/group/cmst3/user/degrutto/VHBBHeppyV21_add/RSGravitonTobb_kMpl001_M_750_Tune4C_13TeV_pythia8/VHBB_HEPPY_F21_add_RSGravitonTobb_kMpl001_M_750_Tune4C_13TeV_Py8__khurana-MINIAODSIM-17d438ff51ec6b3cada9e499a5a978e0/160405_155957/0000/", 1.0],
  "HT1500to2000_pruned" : ["/scratch/bianchi/HT1500to2000/", 119.9]
}


sample_to_process = samples[argv[1]]
print "\nProcessing sample", argv[1]

is_empty = True
processed = 0
chain = ROOT.TChain("tree")
for ff in xrange(int(argv[2]),int(argv[3])+1):
  fname = sample_to_process[0]+"tree_"+str(ff)+".root"
  fi = ROOT.TFile.Open(fname)
  if fi==None or fi.IsZombie():
    continue
  is_empty = False
  chain.AddFile(fname)  
  processed += fi.Get("CountWeighted").GetBinContent(1)
  fi.Close()
  print "Adding file n.", ff, ": total processed events:", processed

if is_empty:
  print "Return because no files could be opened"
  exit(1)

f = ROOT.TFile("/scratch/bianchi/"+argv[1]+"_"+argv[2]+"_"+argv[3]+".root", "RECREATE")

luminosity = 2500.
lumi_factor = sample_to_process[1]*luminosity/processed if processed>0 else -1
print "Luminosity: %.0f pb-1 --- xsection: %.0f pb --- Processed: %.0f ==> Lumi factor: %.2f" % (luminosity, sample_to_process[1], processed, lumi_factor)

cuts_map = [ ["All", lambda ev : True] ]
cuts_map.append( ["Vtype" ,lambda ev : ev.Vtype==-1 or ev.Vtype==4])
cuts_map.append( ["HLT" ,lambda ev : (ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p9_DoublePFJetsC100MaxDeta1p6_v or ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p85_DoublePFJetsC160_v)])
cuts_map.append( ["HLT_Offline_OR", lambda ev : ((ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p9_DoublePFJetsC100MaxDeta1p6_v and abs(ev.Jet_eta[ev.hJCidx[0]])<2.4 and abs(ev.Jet_eta[ev.hJCidx[1]])<2.4 and abs(ev.Jet_eta[ev.hJCidx[0]] - ev.Jet_eta[ev.hJCidx[1]])<1.6 and ev.Jet_pt[ev.hJCidx[0]]>150 and ev.Jet_pt[ev.hJCidx[1]]>150) or (ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p85_DoublePFJetsC160_v and ev.Jet_pt[ev.hJCidx[0]]>200 and ev.Jet_pt[ev.hJCidx[1]]>200 and abs(ev.Jet_eta[ev.hJCidx[0]])<2.4 and abs(ev.Jet_eta[ev.hJCidx[1]])<2.4 )) if len(ev.hJCidx)==2 else False])
cuts_map.append( ["HLT_Offline_AND", lambda ev : (abs(ev.Jet_eta[ev.hJCidx[0]] - ev.Jet_eta[ev.hJCidx[1]])<1.6 and ev.Jet_pt[ev.hJCidx[0]]>200 and ev.Jet_pt[ev.hJCidx[1]]>200 and abs(ev.Jet_eta[ev.hJCidx[0]])<2.4 and abs(ev.Jet_eta[ev.hJCidx[1]])<2.4 ) if len(ev.hJCidx)==2 else False] )
cuts_map.append( ["BTag_MT", lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.800) if len(ev.hJCidx)==2 else False])
cuts_map.append( ["BTag_TT", lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.935) if len(ev.hJCidx)==2 else False])
cuts_map.append( ["Mass", lambda ev : ev.HaddJetsdR08_mass>600 and ev.HaddJetsdR08_mass<800] )

f.cd()
eff_map = {}
histo_map = {}
h_count = ROOT.TH1F("Count", argv[1]+": count runs", 1, 0, 2)
h_count.Fill(1.0)
h_eff = ROOT.TH1F("CutFlow", argv[1]+": cutflow", len(cuts_map), 0, len(cuts_map))
h_eff.Sumw2() 
h_eff.SetLineWidth(2)
h_eff.SetLineColor(ROOT.kBlue)

for n_cut,cut in enumerate(cuts_map):
  h_eff.GetXaxis().SetBinLabel(n_cut+1, cut[0])
  if cut[0]!="All":
    eff_map[cut[0]] = 0.
  else:
    eff_map[cut[0]] = sample_to_process[1]*luminosity
  histo_map[cut[0]] = {
    "njet30" : ROOT.TH1F(cut[0]+"_njet30", argv[1]+": "+cut[0]+"_njet30", 10, 0, 10),
    "njet50" : ROOT.TH1F(cut[0]+"_njet50", argv[1]+": "+cut[0]+"_njet50", 10, 0, 10),
    "njet70" : ROOT.TH1F(cut[0]+"_njet70", argv[1]+": "+cut[0]+"_njet70", 10, 0, 10),
    "njet100" : ROOT.TH1F(cut[0]+"_njet100", argv[1]+": "+cut[0]+"_njet100", 10, 0, 10),
    "MET" : ROOT.TH1F(cut[0]+"_MET", argv[1]+": "+cut[0]+"_MET", 15, 0, 300),
    "lheHT" : ROOT.TH1F(cut[0]+"_lheHT", argv[1]+": "+cut[0]+"_lheHT", 30, 0, 3000),
    "PtBalance" : ROOT.TH1F(cut[0]+"_PtBalance", argv[1]+": "+cut[0]+"_PtBalance", 20, 0, 1),
    "MinJetPt" : ROOT.TH1F(cut[0]+"_MinJetPt", argv[1]+": "+cut[0]+"_MinJetPt", 40, 100, 1000),
    "MaxJetPt" : ROOT.TH1F(cut[0]+"_MaxJetPt", argv[1]+": "+cut[0]+"_MaxJetPt", 40, 100, 1000),
    "MaxJetPtoMass" : ROOT.TH1F(cut[0]+"_MaxJetPtoMass", argv[1]+": "+cut[0]+"_MaxJetPtoMass", 10, 0., 1),
    "MinJetPtoMass" : ROOT.TH1F(cut[0]+"_MinJetPtoMass", argv[1]+": "+cut[0]+"_MinJetPtoMass", 10, 0., 1),
    "Mass" : ROOT.TH1F(cut[0]+"_Mass", argv[1]+": "+cut[0]+"_Mass", 50, 100, 2000),
    "MassFSR" : ROOT.TH1F(cut[0]+"_MassFSR", argv[1]+": "+cut[0]+"_MassFSR", 50, 100, 2000),
    "Pt" : ROOT.TH1F(cut[0]+"_Pt", argv[1]+": "+cut[0]+"_Pt", 20, 0, 500),
    "Eta" : ROOT.TH1F(cut[0]+"_Eta", argv[1]+": "+cut[0]+"_Eta", 20, -6, +6),
    "MaxEta" : ROOT.TH1F(cut[0]+"_MaxEta", argv[1]+": "+cut[0]+"_MaxEta", 20, 0., 2.4),
    "DeltaEta" : ROOT.TH1F(cut[0]+"_DeltaEta", argv[1]+": "+cut[0]+"_DeltaEta", 20, 0, 5),
    "DeltaPhi" : ROOT.TH1F(cut[0]+"_DeltaPhi", argv[1]+": "+cut[0]+"_DeltaPhi", 20, 0, 3.2),
    "MaxJetCSV" : ROOT.TH1F(cut[0]+"_MaxJetCSV", argv[1]+": "+cut[0]+"_MaxJetCSV", 40, 0, 1.),
    "MinJetCSV" : ROOT.TH1F(cut[0]+"_MinJetCSV", argv[1]+": "+cut[0]+"_MinJetCSV", 20, 0, 1.),
    "Vtype" : ROOT.TH1F(cut[0]+"_Vtype", argv[1]+": "+cut[0]+"_Vtype", 7, -1, 6),
    }
for h in histo_map.keys():
  for hh in histo_map[h].keys():
    histo_map[h][hh].Sumw2()
    histo_map[h][hh].SetLineWidth(2)
    histo_map[h][hh].SetLineColor(ROOT.kBlue)

chain.SetBranchStatus("*", False)
chain.SetBranchStatus("nJet", True)
chain.SetBranchStatus("Jet_*", True)
chain.SetBranchStatus("*Weight*", True)
chain.SetBranchStatus("hJCidx", True)
chain.SetBranchStatus("*HLT*", True)
chain.SetBranchStatus("met_pt", True)
chain.SetBranchStatus("*HCSV*", True)
chain.SetBranchStatus("lheHT", True)
chain.SetBranchStatus("Vtype", True)
chain.SetBranchStatus("*HaddJetsdR08*", True)

print eff_map

print "Total events in the vhbb trees:", chain.GetEntries()
for iev in range( min(int(1e+6), chain.GetEntries()) ):

    chain.GetEntry(iev)
    ev = chain
    if iev%1000 == 0:
        print "Processing event ", iev

    passall = True
    for cut in cuts_map:
        if cut[1](ev) and passall:
          if cut[0]!="All" :
            eff_map[cut[0]] += weight(ev, lumi_factor) 
          histo_map[cut[0]]["lheHT"].Fill(ev.lheHT if hasattr(ev,"lheHT") else 0., weight(ev,lumi_factor))    
          histo_map[cut[0]]["MET"].Fill(ev.met_pt, weight(ev,lumi_factor))    
          for ptcut in [30,50,70,100]:
            histo_map[cut[0]]["njet"+str(ptcut)].Fill( sum( ev.Jet_pt[j]>ptcut and abs(ev.Jet_eta[j])<2.4 for j in range(ev.nJet) ), weight(ev,lumi_factor))
          histo_map[cut[0]]["MinJetPt"].Fill(min(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]] ) if len(ev.hJCidx)==2 else 0., weight(ev,lumi_factor))
          histo_map[cut[0]]["MaxJetPt"].Fill(max(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]] ) if len(ev.hJCidx)==2 else 0., weight(ev,lumi_factor))
          histo_map[cut[0]]["MaxJetPtoMass"].Fill(max(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]] )/ev.HCSV_mass if len(ev.hJCidx)==2 else 0., weight(ev,lumi_factor))
          histo_map[cut[0]]["MinJetPtoMass"].Fill(min(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]] )/ev.HCSV_mass if len(ev.hJCidx)==2 else 0., weight(ev,lumi_factor))
          histo_map[cut[0]]["PtBalance"].Fill( abs(ev.Jet_pt[ev.hJCidx[0]]-ev.Jet_pt[ev.hJCidx[1]])/(ev.Jet_pt[ev.hJCidx[0]]+ev.Jet_pt[ev.hJCidx[1]]) if len(ev.hJCidx)==2 else 99., weight(ev,lumi_factor))
          histo_map[cut[0]]["MaxJetCSV"].Fill( ev.Jet_btagCSV[ev.hJCidx[0]] if len(ev.hJCidx)==2 else 0., weight(ev,lumi_factor))
          histo_map[cut[0]]["MinJetCSV"].Fill( ev.Jet_btagCSV[ev.hJCidx[1]] if len(ev.hJCidx)==2 else 0., weight(ev,lumi_factor))
          histo_map[cut[0]]["Mass"].Fill(ev.HCSV_mass, weight(ev,lumi_factor))
          histo_map[cut[0]]["MassFSR"].Fill(ev.HaddJetsdR08_mass, weight(ev,lumi_factor))
          histo_map[cut[0]]["Pt"].Fill(ev.HCSV_pt, weight(ev,lumi_factor))
          histo_map[cut[0]]["Eta"].Fill(ev.HCSV_eta, weight(ev,lumi_factor))
          histo_map[cut[0]]["MaxEta"].Fill(max(abs(ev.Jet_eta[ev.hJCidx[0]]),abs(ev.Jet_eta[ev.hJCidx[1]])) if len(ev.hJCidx)==2 else 99, weight(ev,lumi_factor))
          histo_map[cut[0]]["Vtype"].Fill(ev.Vtype, weight(ev,lumi_factor))
          histo_map[cut[0]]["DeltaEta"].Fill(abs(ev.Jet_eta[ev.hJCidx[0]] - ev.Jet_eta[ev.hJCidx[1]])  if len(ev.hJCidx)==2 else 99, weight(ev,lumi_factor))
          histo_map[cut[0]]["DeltaPhi"].Fill(math.acos(math.cos(ev.Jet_phi[ev.hJCidx[0]] - ev.Jet_phi[ev.hJCidx[1]]))  if len(ev.hJCidx)==2 else 99, weight(ev,lumi_factor))
        else:
          passall = False

print eff_map

f.cd()                 
for n_cut,cut in enumerate(cuts_map):
    print "%.1f (%.2f%%)" % (eff_map[cut[0]], eff_map[cut[0]]/eff_map["All"]*100. if eff_map["All"]>0. else 100.), cut[0]
    h_eff.SetBinContent(n_cut+1,eff_map[cut[0]])

h_eff.Write("", ROOT.TObject.kOverwrite)
h_count.Write("", ROOT.TObject.kOverwrite)

for h in histo_map.keys():
    f.mkdir(h)
    f.cd(h)
    for hh in histo_map[h].keys():
        histo = histo_map[h][hh]
        histo.Write("", ROOT.TObject.kOverwrite)
f.Close()

