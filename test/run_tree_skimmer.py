from sys import argv
argv.append( '-b-' )
import ROOT
ROOT.gROOT.SetBatch(True)
argv.remove( '-b-' )
from ROOT import TLorentzVector
import math
import os

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

h_count = ROOT.TH1F("CountWeighted", "CountWeighted", 1, 0, 2)
h_count.Fill(1, processed)

os.system('mkdir /scratch/bianchi/'+argv[1])
f = ROOT.TFile("/scratch/bianchi/"+argv[1]+"/tree_"+argv[4]+".root", "RECREATE")

chain.SetBranchStatus("*", False)
chain.SetBranchStatus("HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p85_DoublePFJetsC160_v", True)
chain.SetBranchStatus("HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p9_DoublePFJetsC100MaxDeta1p6_v", True)
chain.SetBranchStatus("hJCidx", True)
chain.SetBranchStatus("Jet_pt", True)
chain.SetBranchStatus("Jet_corr*", True)
chain.SetBranchStatus("Jet_eta", True)
chain.SetBranchStatus("Jet_phi", True)
chain.SetBranchStatus("Jet_mass", True)
chain.SetBranchStatus("Jet_btagCSV", True)
chain.SetBranchStatus("Jet_btagCSV*SF*", True)
chain.SetBranchStatus("met_pt", True)
chain.SetBranchStatus("met_phi", True)
chain.SetBranchStatus("nJet", True)
chain.SetBranchStatus("HCSV_*", True)
chain.SetBranchStatus("Vtype", True)
chain.SetBranchStatus("lheHT", True)
chain.SetBranchStatus("HaddJetsdR08_*", True)
chain.SetBranchStatus("puWeight", True)
chain.SetBranchStatus("genWeight", True)

print "Copying tree with ", chain.GetEntries(), " entries..."

cut_string = "(HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p85_DoublePFJetsC160_v | HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p9_DoublePFJetsC100MaxDeta1p6_v) & (TMath::Abs(Jet_eta[hJCidx[0]]-Jet_eta[hJCidx[1]])<1.6 & Jet_pt[hJCidx[0]]>200 & Jet_pt[hJCidx[1]]>200 & TMath::Abs(Jet_eta[hJCidx[0]])<2.4 & TMath::Abs(Jet_eta[hJCidx[1]])<2.4)"

tree = chain.CopyTree(cut_string, "")

f.cd()
tree.Write("", ROOT.TObject.kOverwrite)
h_count.Write("", ROOT.TObject.kOverwrite)
f.Close()
