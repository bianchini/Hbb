from sys import argv
argv.append( '-b-' )
import ROOT
ROOT.gROOT.SetBatch(True)
argv.remove( '-b-' )
from ROOT import TLorentzVector
import math
import sys
sys.path.append('./')
sys.path.append('../python/')
from samples import *

def weight(ev, lumi):
  if lumi<0:
    return 1.0
  return ev.puWeight*abs(ev.genWeight)/ev.genWeight*lumi

def weight_bTag_SF(ev, wp1, wp2, ana):
  sf = 1.0
  if ana=="nominal":
    sf = getattr(ev, "Jet_btagCSV"+wp1+"SF")[ev.hJCidx[0]]*getattr(ev, "Jet_btagCSV"+wp2+"SF")[ev.hJCidx[1]]
  else:
    sf = getattr(ev, "Jet_btagCSV"+wp1+"SF_"+ana)[ev.hJCidx[0]]*getattr(ev, "Jet_btagCSV"+wp2+"SF_"+ana)[ev.hJCidx[1]]
  #print "SF ", wp1, wp2, ana, ": " , sf
  return sf

def weight_bTag(ev, cut):
  ana = "nominal"
  if "CSVSFUp" in cut:
    ana = "Up"
  elif "CSVSFDown" in cut:
     ana = "Down"
  if "_LT_" in cut or "_nMT_" in cut:
    return weight_bTag_SF(ev, "T", "L", ana)
  elif "_MT_" in cut:
    return weight_bTag_SF(ev, "T", "M", ana)
  elif "_TT_" in cut:
    return weight_bTag_SF(ev, "T", "T", ana)
  else:
    return 1.0 

def preselection(ev):
  if hasattr(ev, "json_silver"):
    return getattr(ev, "json_silver")
  return True

def ak08_mass(ev):
  fatmass = 0.
  if getattr(ev, "nFatjetAK08ungroomed", 0) < 2 :
    return fatmass
  fatjets = []
  block_idx = -1
  for ij8 in xrange(ev.nFatjetAK08ungroomed):
    j08 = ROOT.TLorentzVector()
    #corr_factor = ev.FatjetAK08ungroomed_mprunedcorr[ij8]/ev.FatjetAK08ungroomed_mass[ij8] if hasattr(ev, "FatjetAK08ungroomed_mprunedcorr") and ev.FatjetAK08ungroomed_mass[ij8]>0 else 1.0
    corr_factor = 1.0
    j08.SetPtEtaPhiM( ev.FatjetAK08ungroomed_pt[ij8]*corr_factor, ev.FatjetAK08ungroomed_eta[ij8], ev.FatjetAK08ungroomed_phi[ij8], ev.FatjetAK08ungroomed_mass[ij8]*corr_factor)
    for ij4 in [ev.hJCidx[0], ev.hJCidx[1]]:
      j04 = ROOT.TLorentzVector()
      j04.SetPtEtaPhiM( ev.Jet_pt[ij4],  ev.Jet_eta[ij4],  ev.Jet_phi[ij4],  ev.Jet_mass[ij4])
      if j08.DeltaR(j04)<0.8 and ij4!=block_idx:
        fatjets.append(j08)
        block_idx = ij4
      if len(fatjets)==2:
        break  
  fatmass = (fatjets[0]+fatjets[1]).M() if len(fatjets)==2 else 0.
  return fatmass

# specify here which samples
samples = samples_pruned

sample_to_process = samples[argv[1]]
print "\nProcessing sample", argv[1]

is_empty = True
processed = 0
chain = ROOT.TChain("tree")

if int(argv[2])<0:
  fname = sample_to_process[0]+"tree.root"
  fi = ROOT.TFile.Open(fname)
  if not (fi==None or fi.IsZombie()):
    is_empty = False
    chain.AddFile(fname)  
    processed += fi.Get("CountWeighted").GetBinContent(1)
    fi.Close()
    print "Adding file tree.root: total processed events:", processed
else:
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

if int(argv[2])<0:
  f = ROOT.TFile("/scratch/bianchi/"+argv[1]+".root", "RECREATE")
else:
  f = ROOT.TFile("/scratch/bianchi/"+argv[1]+"_"+argv[2]+"_"+argv[3]+".root", "RECREATE")

luminosity = 2630.
lumi_factor = sample_to_process[1]*luminosity/processed if processed>0 else -1
print "Luminosity: %.0f pb-1 --- xsection: %.0f pb --- Processed: %.0f ==> Lumi factor: %.2f" % (luminosity, sample_to_process[1], processed, lumi_factor)

# True if one cut implies all those before

cuts_Vtype = {  
  "Had" : lambda ev : ev.Vtype in [-1,4],
  "Lep" : lambda ev : ev.Vtype in [0,1,2,3],
}

cuts_BTag = {
  #"All" :  lambda ev : True,
  "LT" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.460) if len(ev.hJCidx)==2 else False,
  "LT_CSVSFUp" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.460) if len(ev.hJCidx)==2 else False,
  "LT_CSVSFDown" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.460) if len(ev.hJCidx)==2 else False,
  #"nMT" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]<0.800 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.460) if len(ev.hJCidx)==2 else False,
  "MT" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.800) if len(ev.hJCidx)==2 else False,
  "MT_CSVSFUp" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.800) if len(ev.hJCidx)==2 else False,
  "MT_CSVSFDown" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.800) if len(ev.hJCidx)==2 else False,
  "TT" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.935) if len(ev.hJCidx)==2 else False,
  "TT_CSVSFUp" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.935) if len(ev.hJCidx)==2 else False,
  "TT_CSVSFDown" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.935) if len(ev.hJCidx)==2 else False,
}

cuts_MinPt = {
  #"All" :  lambda ev : True,
  "MinPt200" : lambda ev :  min(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]])>200. if len(ev.hJCidx)==2 else False,
  "MinPt175" : lambda ev :  min(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]])>175. if len(ev.hJCidx)==2 else False,
  "MinPt150" : lambda ev :  min(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]])>150. if len(ev.hJCidx)==2 else False,
}

cuts_DH = {
  #"All" :  lambda ev : True,
  "DH2p0" :  lambda ev : abs(ev.Jet_eta[ev.hJCidx[0]]-ev.Jet_eta[ev.hJCidx[1]])<2.0  if len(ev.hJCidx)==2 else False,
  "DH1p6" :  lambda ev : abs(ev.Jet_eta[ev.hJCidx[0]]-ev.Jet_eta[ev.hJCidx[1]])<1.6  if len(ev.hJCidx)==2 else False,
  "DH1p1" :  lambda ev : abs(ev.Jet_eta[ev.hJCidx[0]]-ev.Jet_eta[ev.hJCidx[1]])<1.1  if len(ev.hJCidx)==2 else False,
}

cuts_in_chain = False
cuts_map = [ ["All", lambda ev : True] ]
##cuts_map.append( ["Vtype" ,lambda ev : ev.Vtype==-1 or ev.Vtype==4])
##cuts_map.append( ["HLT" ,lambda ev : (ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p9_DoublePFJetsC100MaxDeta1p6_v or ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p85_DoublePFJetsC160_v)])
##cuts_map.append( ["HLT_Offline_OR", lambda ev : ((ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p9_DoublePFJetsC100MaxDeta1p6_v and abs(ev.Jet_eta[ev.hJCidx[0]])<2.4 and abs(ev.Jet_eta[ev.hJCidx[1]])<2.4 and abs(ev.Jet_eta[ev.hJCidx[0]] - ev.Jet_eta[ev.hJCidx[1]])<1.6 and ev.Jet_pt[ev.hJCidx[0]]>150 and ev.Jet_pt[ev.hJCidx[1]]>150) or (ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p85_DoublePFJetsC160_v and ev.Jet_pt[ev.hJCidx[0]]>200 and ev.Jet_pt[ev.hJCidx[1]]>200 and abs(ev.Jet_eta[ev.hJCidx[0]])<2.4 and abs(ev.Jet_eta[ev.hJCidx[1]])<2.4 )) if len(ev.hJCidx)==2 else False])
##cuts_map.append( ["HLT_Offline_AND", lambda ev : (abs(ev.Jet_eta[ev.hJCidx[0]] - ev.Jet_eta[ev.hJCidx[1]])<1.6 and ev.Jet_pt[ev.hJCidx[0]]>200 and ev.Jet_pt[ev.hJCidx[1]]>200 and abs(ev.Jet_eta[ev.hJCidx[0]])<2.4 and abs(ev.Jet_eta[ev.hJCidx[1]])<2.4 ) if len(ev.hJCidx)==2 else False] )
#cuts_map.append( ["BTag_LT_lept", lambda ev : ( ev.Vtype in [0,1,2,3] and ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.460) if len(ev.hJCidx)==2 else False])
#cuts_map.append( ["BTag_LT", lambda ev : (ev.Vtype in [-1,4] and ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.460) if len(ev.hJCidx)==2 else False])
#cuts_map.append( ["BTag_nMT", lambda ev : (ev.Vtype in [-1,4] and ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]<0.800 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.460) if len(ev.hJCidx)==2 else False])
#cuts_map.append( ["BTag_MT", lambda ev : (ev.Vtype in [-1,4] and ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.800) if len(ev.hJCidx)==2 else False])
#cuts_map.append( ["BTag_TT", lambda ev : (ev.Vtype in [-1,4] and ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.935) if len(ev.hJCidx)==2 else False])
##cuts_map.append( ["Mass", lambda ev : ev.HaddJetsdR08_mass>600 and ev.HaddJetsdR08_mass<800] )

for cut_Vtype in cuts_Vtype.keys():
  for cut_BTag in cuts_BTag.keys():
    for cut_MinPt in cuts_MinPt.keys():
      for cut_DH in cuts_DH.keys():
        cut_name = cut_Vtype+"_"+cut_BTag+"_"+cut_MinPt+"_"+cut_DH
        cut = lambda ev,cuts_Vtype=cuts_Vtype,cuts_BTag=cuts_BTag,cuts_MinPt=cuts_MinPt,cuts_DH=cuts_DH,cut_Vtype=cut_Vtype, cut_BTag=cut_BTag, cut_MinPt=cut_MinPt,cut_DH=cut_DH : (cuts_Vtype[cut_Vtype](ev) and cuts_BTag[cut_BTag](ev) and cuts_MinPt[cut_MinPt](ev) and cuts_DH[cut_DH](ev))
        cuts_map.append( [cut_name,cut] )

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

  #if "CSVSF" in cut[0]:
  #  histo_map[cut[0]] = {}
  #  continue

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
    "MaxJetPtoMass" : ROOT.TH1F(cut[0]+"_MaxJetPtoMass", argv[1]+": "+cut[0]+"_MaxJetPtoMass", 20, 0., 1),
    "MinJetPtoMass" : ROOT.TH1F(cut[0]+"_MinJetPtoMass", argv[1]+": "+cut[0]+"_MinJetPtoMass", 20, 0., 1),
    "Mass" : ROOT.TH1F(cut[0]+"_Mass", argv[1]+": "+cut[0]+"_Mass", 180, 400, 4000),
    "Mass_JECUp" : ROOT.TH1F(cut[0]+"_Mass_JECUp", argv[1]+": "+cut[0]+"_Mass_JECUp", 180, 400, 4000),
    "Mass_JECDown" : ROOT.TH1F(cut[0]+"_Mass_JECDown", argv[1]+": "+cut[0]+"_Mass_JECDown", 180, 400, 4000),
    "Mass_JERUp" : ROOT.TH1F(cut[0]+"_Mass_JERUp", argv[1]+": "+cut[0]+"_Mass_JERUp", 180, 400, 4000),
    "Mass_JERDown" : ROOT.TH1F(cut[0]+"_Mass_JERDown", argv[1]+": "+cut[0]+"_Mass_JERDown", 180, 400, 4000),
    "MassFSR" : ROOT.TH1F(cut[0]+"_MassFSR", argv[1]+": "+cut[0]+"_MassFSR", 36000, 400, 4000),
    "MassFSR_JECUp" : ROOT.TH1F(cut[0]+"_MassFSR_JECUp", argv[1]+": "+cut[0]+"_MassFSR_JECUp", 36000, 400, 4000),
    "MassFSR_JECDown" : ROOT.TH1F(cut[0]+"_MassFSR_JECDown", argv[1]+": "+cut[0]+"_MassFSR_JECDown", 36000, 400, 4000),
    "MassFSR_JERUp" : ROOT.TH1F(cut[0]+"_MassFSR_JERUp", argv[1]+": "+cut[0]+"_MassFSR_JERUp", 36000, 400, 4000),
    "MassFSR_JERDown" : ROOT.TH1F(cut[0]+"_MassFSR_JERDown", argv[1]+": "+cut[0]+"_MassFSR_JERDown", 36000, 400, 4000),
    "MassAK08" : ROOT.TH1F(cut[0]+"_MassAK08", argv[1]+": "+cut[0]+"_MassAK08", 180, 400, 4000),
    "njetAK08" : ROOT.TH1F(cut[0]+"_njetAK08", argv[1]+": "+cut[0]+"_njetAK08", 10, 0, 10),
    "Pt" : ROOT.TH1F(cut[0]+"_Pt", argv[1]+": "+cut[0]+"_Pt", 20, 0, 500),
    "Eta" : ROOT.TH1F(cut[0]+"_Eta", argv[1]+": "+cut[0]+"_Eta", 20, -6, +6),
    "MaxEta" : ROOT.TH1F(cut[0]+"_MaxEta", argv[1]+": "+cut[0]+"_MaxEta", 20, 0., 2.4),
    "DeltaEta" : ROOT.TH1F(cut[0]+"_DeltaEta", argv[1]+": "+cut[0]+"_DeltaEta", 20, 0, 3),
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
chain.SetBranchStatus("json*", True)
chain.SetBranchStatus("FatjetAK08ungroomed_*", True)
chain.SetBranchStatus("nFatjetAK08ungroomed", True)

print eff_map

print "Total events in the vhbb trees:", chain.GetEntries()
for iev in range( min(int(1e+9), chain.GetEntries()) ):

    chain.GetEntry(iev)
    ev = chain
    if iev%100 == 0:
        print "Processing event ", iev

    if not preselection(ev):
      continue

    variables = {}
    variables["lheHT"] = ev.lheHT if hasattr(ev,"lheHT") else 0.
    variables["MET"] = ev.met_pt
    for ptcut in [30,50,70,100]:
      variables["njet"+str(ptcut)] = sum( ev.Jet_pt[j]>ptcut and abs(ev.Jet_eta[j])<2.4 for j in range(ev.nJet) )
    variables["MinJetPt"] = min(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]] ) if len(ev.hJCidx)==2 else 0.
    variables["MaxJetPt"] = max(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]] ) if len(ev.hJCidx)==2 else 0. 
    variables["MinJetPtoMass"] = min(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]] )/ev.HCSV_mass if len(ev.hJCidx)==2 else 0. 
    variables["MaxJetPtoMass"] = max(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]] )/ev.HCSV_mass if len(ev.hJCidx)==2 else 0. 
    variables["PtBalance"] = abs(ev.Jet_pt[ev.hJCidx[0]]-ev.Jet_pt[ev.hJCidx[1]])/(ev.Jet_pt[ev.hJCidx[0]]+ev.Jet_pt[ev.hJCidx[1]]) if len(ev.hJCidx)==2 else 99. 
    variables["MaxJetCSV"] = ev.Jet_btagCSV[ev.hJCidx[0]] if len(ev.hJCidx)==2 else 0.
    variables["MinJetCSV"] = ev.Jet_btagCSV[ev.hJCidx[1]] if len(ev.hJCidx)==2 else 0. 
    variables["Mass"] = ev.HCSV_mass 
    variables["Mass_JECUp"] = ev.HCSV_mass * math.sqrt( ev.Jet_corr_JECUp[ev.hJCidx[0]]*ev.Jet_corr_JECUp[ev.hJCidx[1]]/ev.Jet_corr[ev.hJCidx[0]]/ev.Jet_corr[ev.hJCidx[1]]) if len(ev.hJCidx)==2 and ev.Jet_corr_JECUp[ev.hJCidx[0]]>0. and ev.Jet_corr_JECUp[ev.hJCidx[1]]>0. and lumi_factor>0  else ev.HCSV_mass
    variables["Mass_JECDown"] = ev.HCSV_mass * math.sqrt( ev.Jet_corr_JECDown[ev.hJCidx[0]]*ev.Jet_corr_JECDown[ev.hJCidx[1]]/ev.Jet_corr[ev.hJCidx[0]]/ev.Jet_corr[ev.hJCidx[1]]) if len(ev.hJCidx)==2  and lumi_factor>0 and ev.Jet_corr_JECDown[ev.hJCidx[0]]>0. and ev.Jet_corr_JECDown[ev.hJCidx[1]]>0. else ev.HCSV_mass
    variables["Mass_JERUp"] = ev.HCSV_mass * math.sqrt( ev.Jet_corr_JERUp[ev.hJCidx[0]]*ev.Jet_corr_JERUp[ev.hJCidx[1]]/ev.Jet_corr_JER[ev.hJCidx[0]]/ev.Jet_corr_JER[ev.hJCidx[1]]) if len(ev.hJCidx)==2  and lumi_factor>0 and ev.Jet_corr_JER[ev.hJCidx[0]]>0. and ev.Jet_corr_JER[ev.hJCidx[1]]>0. else ev.HCSV_mass
    variables["Mass_JERDown"] = ev.HCSV_mass * math.sqrt( ev.Jet_corr_JERDown[ev.hJCidx[0]]*ev.Jet_corr_JERDown[ev.hJCidx[1]]/ev.Jet_corr_JER[ev.hJCidx[0]]/ev.Jet_corr_JER[ev.hJCidx[1]]) if len(ev.hJCidx)==2  and lumi_factor>0 and ev.Jet_corr_JER[ev.hJCidx[0]]>0. and ev.Jet_corr_JER[ev.hJCidx[1]]>0. else ev.HCSV_mass
    variables["MassFSR"] = ev.HaddJetsdR08_mass 
    variables["MassFSR_JECUp"] = ev.HaddJetsdR08_mass * math.sqrt( ev.Jet_corr_JECUp[ev.hJCidx[0]]*ev.Jet_corr_JECUp[ev.hJCidx[1]]/ev.Jet_corr[ev.hJCidx[0]]/ev.Jet_corr[ev.hJCidx[1]]) if len(ev.hJCidx)==2  and lumi_factor>0 and ev.Jet_corr_JECUp[ev.hJCidx[0]]>0. and ev.Jet_corr_JECUp[ev.hJCidx[1]]>0. else ev.HaddJetsdR08_mass
    variables["MassFSR_JECDown"] = ev.HaddJetsdR08_mass * math.sqrt( ev.Jet_corr_JECDown[ev.hJCidx[0]]*ev.Jet_corr_JECDown[ev.hJCidx[1]]/ev.Jet_corr[ev.hJCidx[0]]/ev.Jet_corr[ev.hJCidx[1]]) if len(ev.hJCidx)==2  and lumi_factor>0 and ev.Jet_corr_JECDown[ev.hJCidx[0]]>0. and ev.Jet_corr_JECDown[ev.hJCidx[1]]>0. else ev.HaddJetsdR08_mass
    variables["MassFSR_JERUp"] = ev.HaddJetsdR08_mass * math.sqrt( ev.Jet_corr_JERUp[ev.hJCidx[0]]*ev.Jet_corr_JERUp[ev.hJCidx[1]]/ev.Jet_corr_JER[ev.hJCidx[0]]/ev.Jet_corr_JER[ev.hJCidx[1]]) if len(ev.hJCidx)==2  and lumi_factor>0 and ev.Jet_corr_JER[ev.hJCidx[0]]>0. and ev.Jet_corr_JER[ev.hJCidx[1]]>0. else ev.HaddJetsdR08_mass
    variables["MassFSR_JERDown"] = ev.HaddJetsdR08_mass * math.sqrt( ev.Jet_corr_JERDown[ev.hJCidx[0]]*ev.Jet_corr_JERDown[ev.hJCidx[1]]/ev.Jet_corr_JER[ev.hJCidx[0]]/ev.Jet_corr_JER[ev.hJCidx[1]]) if len(ev.hJCidx)==2  and lumi_factor>0 and ev.Jet_corr_JER[ev.hJCidx[0]]>0. and ev.Jet_corr_JER[ev.hJCidx[1]]>0. else ev.HaddJetsdR08_mass
    variables["MassAK08"] = ak08_mass(ev) 
    variables["njetAK08"] = getattr(ev, "nFatjetAK08ungroomed", 2)
    variables["Pt"] = ev.HCSV_pt 
    variables["Eta"] = ev.HCSV_eta 
    variables["MaxEta"] = max(abs(ev.Jet_eta[ev.hJCidx[0]]),abs(ev.Jet_eta[ev.hJCidx[1]])) if len(ev.hJCidx)==2 else 99 
    variables["Vtype"] = ev.Vtype 
    variables["DeltaEta"] = abs(ev.Jet_eta[ev.hJCidx[0]] - ev.Jet_eta[ev.hJCidx[1]])  if len(ev.hJCidx)==2 else 99 
    variables["DeltaPhi"] = math.acos(math.cos(ev.Jet_phi[ev.hJCidx[0]] - ev.Jet_phi[ev.hJCidx[1]]))  if len(ev.hJCidx)==2 else 99 

    passall = True
    for cut in cuts_map:
        if cut[1](ev) and passall:
          #print cut[0], ": pass" 
          weight_btag = weight_bTag(ev, cut[0]) if lumi_factor>0 else 1.0
          if cut[0]!="All" :
            eff_map[cut[0]] += weight(ev, lumi_factor)*weight_btag
          for var in histo_map[cut[0]].keys():
            histo_map[cut[0]][var].Fill(variables[var], weight(ev,lumi_factor)*weight_btag)
        else:
          #print cut[0], ": fail" 
          passall = (False or not cuts_in_chain)

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
        histo.SetBinContent( histo.GetNbinsX(), histo.GetBinContent(histo.GetNbinsX()) +  histo.GetBinContent(histo.GetNbinsX()+1) )
        histo.Write("", ROOT.TObject.kOverwrite)
f.Close()

