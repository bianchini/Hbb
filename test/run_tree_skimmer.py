from sys import argv
argv.append( '-b-' )
import ROOT
ROOT.gROOT.SetBatch(True)
argv.remove( '-b-' )
from ROOT import TLorentzVector
import math
import os

import sys
sys.path.append('./')
sys.path.append('../python/')
from samples import *

samples = samples_V21

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
chain.SetBranchStatus("json*", True)
chain.SetBranchStatus("hJCidx", True)
chain.SetBranchStatus("nJet", True)
chain.SetBranchStatus("Jet_pt", True)
chain.SetBranchStatus("Jet_corr*", True)
chain.SetBranchStatus("Jet_eta", True)
chain.SetBranchStatus("Jet_phi", True)
chain.SetBranchStatus("Jet_mass", True)
chain.SetBranchStatus("Jet_btagCSV", True)
chain.SetBranchStatus("Jet_btagCSV*SF*", True)
chain.SetBranchStatus("Jet_hadronFlavour", True)
chain.SetBranchStatus("Jet_lepton*", True)
chain.SetBranchStatus("Jet_puId", True)
chain.SetBranchStatus("Jet_id", True)
chain.SetBranchStatus("met_pt", True)
chain.SetBranchStatus("met_phi", True)
chain.SetBranchStatus("HCSV_pt", True)
chain.SetBranchStatus("HCSV_mass", True)
chain.SetBranchStatus("HCSV_eta", True)
chain.SetBranchStatus("HCSV_phi", True)
chain.SetBranchStatus("Vtype", True)
chain.SetBranchStatus("lheHT", True)
chain.SetBranchStatus("HaddJetsdR08_*", True)
chain.SetBranchStatus("FatjetAK08ungroomed_mprunedcorr", True)
chain.SetBranchStatus("FatjetAK08ungroomed_mass", True)
chain.SetBranchStatus("FatjetAK08ungroomed_pt", True)
chain.SetBranchStatus("FatjetAK08ungroomed_eta", True)
chain.SetBranchStatus("FatjetAK08ungroomed_phi", True)
chain.SetBranchStatus("nFatjetAK08ungroomed", True)
chain.SetBranchStatus("puWeight", True)
chain.SetBranchStatus("genWeight", True)

#cut_string = "(HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p85_DoublePFJetsC160_v | HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p9_DoublePFJetsC100MaxDeta1p6_v) & (TMath::Abs(Jet_eta[hJCidx[0]]-Jet_eta[hJCidx[1]])<1.6 & Jet_pt[hJCidx[0]]>200 & Jet_pt[hJCidx[1]]>200 & TMath::Abs(Jet_eta[hJCidx[0]])<2.4 & TMath::Abs(Jet_eta[hJCidx[1]])<2.4)"
cut_string = "(HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p85_DoublePFJetsC160_v | HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p9_DoublePFJetsC100MaxDeta1p6_v) & (TMath::Abs(Jet_eta[hJCidx[0]]-Jet_eta[hJCidx[1]])<2.0 & Jet_pt[hJCidx[0]]>150 & Jet_pt[hJCidx[1]]>150 & TMath::Abs(Jet_eta[hJCidx[0]])<2.4 & TMath::Abs(Jet_eta[hJCidx[1]])<2.4)"

print "Cut string: ", cut_string
print "Copying tree with ", chain.GetEntries(), " entries..."
tree = chain.CopyTree(cut_string, "")
print "Copied ", tree.GetEntries(), " entries satisfying the cut condition"

print "Writing to file..."
f.cd()
tree.Write("", ROOT.TObject.kOverwrite)
h_count.Write("", ROOT.TObject.kOverwrite)
f.Close()
print "Done!"
