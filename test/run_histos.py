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
from parameters_cfi import luminosity


class Xbb_trigger_corrector:

    def __init__(self, fname="../data/X750_trigger_efficiency.root", switch=165.):
        self.file = ROOT.TFile.Open(fname, "READ")
        self.corrs = {}
        for ana in ["err_", ""]:
            for hlt in ["low", "high"]:
                for eta_bin in ["0-0.6", "0.6-1.7", "1.7-2.2"]:
                    self.corrs["Fcorr_"+ana+hlt+"M_"+eta_bin] = self.file.Get("Fcorr_"+ana+hlt+"M_"+eta_bin)
        self.switch = switch
        if self.file!=None:
            print ("[Xbb_trigger_corrector]: Correction file properly loaded. Switch between triggers at %.0f GeV" % self.switch)

    def eval_OR(self, pt1=100, eta1=0.0, pt2=100, eta2=0.0, pass_low=True, pass_high=True, syst=""):

        val = 1.0
        if not (pass_low or pass_high):
            print "None of the triggers fire!"
            return val

        eta_bin1 = ""
        if abs(eta1)<0.6:
            eta_bin1 = "0-0.6"
        elif abs(eta1)<1.7:
            eta_bin1 = "0.6-1.7"
        elif abs(eta1)<2.5:
            eta_bin1 = "1.7-2.2"
        eta_bin2 = ""
        if abs(eta2)<0.6:
            eta_bin2 = "0-0.6"
        elif abs(eta2)<1.7:
            eta_bin2 = "0.6-1.7"
        elif abs(eta2)<2.5:
            eta_bin2 = "1.7-2.2"

        is_shifted = ("Kin" in syst)
        shift_sign = +1 if "Up" in syst else -1
    
        hlt = "low" if pass_low else "high"
        if is_shifted:
            val = self.corrs["Fcorr_"+hlt+"M_"+eta_bin1].Eval(pt1)*self.corrs["Fcorr_"+hlt+"M_"+eta_bin2].Eval(pt2)
        else:
            val = (self.corrs["Fcorr_"+hlt+"M_"+eta_bin1].Eval(pt1) + shift_sign*self.corrs["Fcorr_err_"+hlt+"M_"+eta_bin1].Eval(pt1))*(self.corrs["Fcorr_"+hlt+"M_"+eta_bin2].Eval(pt2) + shift_sign*self.corrs["Fcorr_err_"+hlt+"M_"+eta_bin2].Eval(pt2))            
                
        if abs(1-val)>0.3:
            print ("Large weight: pt=%.0f,%.0f, eta=%.1f,%.1f, hlt=%s, syst=%s ==> %.3f" % (pt1,pt2,eta1,eta2,hlt,syst,val))
        return val

    def get_switch(self):
        return self.switch
 
    def eval(self, pt=100, eta=0.0, hlt="low", syst=""):
        val = 1.0
        eta_bin = ""
        if abs(eta)<0.6:
            eta_bin = "0-0.6"
        elif abs(eta)<1.7:
            eta_bin = "0.6-1.7"
        elif abs(eta)<2.5:
            eta_bin = "1.7-2.2"
        else:
            return val

        if pt<self.switch and hlt=="high":
            return val
        elif pt>self.switch and hlt=="low":
            return val
        elif pt<100 and hlt=="low":
            return val

        ana = "" if "Kin" not in syst else "err_"
        sign = +1 if "Up" in syst else -1

        g = self.corrs["Fcorr_"+ana+hlt+"M_"+eta_bin]
        val = g.Eval(pt)
        if ana!="":
            n = self.corrs["Fcorr_"+hlt+"M_"+eta_bin]
            ROOT.SetOwnership(n, False ) 
            val = n.Eval(pt) + sign*g.Eval(pt)
            if abs(1-val)>0.3:
                print ("Large weight: Pt=%.0f, eta=%.1f, hlt=%s, syst=%s ==> %.3f" % (pt,eta,hlt,syst,val))
        return val

            

def deltaPhi(phi1, phi2):
    result = phi1 - phi2
    while (result > math.pi): result -= 2*math.pi
    while (result <= -math.pi): result += 2*math.pi
    return result


def deltaR2( e1, p1, e2=None, p2=None):
    """Take either 4 arguments (eta,phi, eta,phi) or two objects that have 'eta', 'phi' methods)"""
    if (e2 == None and p2 == None):
        return deltaR2(e1.eta(),e1.phi(), p1.eta(), p1.phi())
    de = e1 - e2
    dp = deltaPhi(p1, p2)
    return de*de + dp*dp

def deltaR( *args ):
    return math.sqrt( deltaR2(*args) )



def projectionMETOntoJet(met, metphi, jet, jetphi, onlyPositive=True, threshold = math.pi/4.0):
  deltaphi = deltaPhi(metphi, jetphi)
  projection = met * math.cos(deltaphi)  
  if onlyPositive and abs(deltaphi) >= threshold:
      return 0.0
  else:
      return projection

def projMetOntoH(ev, tryAlsoWNoLept, recoverAlsoFSR):
  if len(ev.hJCidx)<2:
    return ev.HCSV_mass
  lep0pt = ev.Jet_leptonPt[ev.hJCidx[0]]
  lep1pt = ev.Jet_leptonPt[ev.hJCidx[1]]

  nu = ROOT.TLorentzVector()
  j0 = ROOT.TLorentzVector()
  j1 = ROOT.TLorentzVector()
  j0.SetPtEtaPhiM( ev.Jet_pt[ev.hJCidx[0]],  ev.Jet_eta[ev.hJCidx[0]],  ev.Jet_phi[ev.hJCidx[0]],  ev.Jet_mass[ev.hJCidx[0]])
  j1.SetPtEtaPhiM( ev.Jet_pt[ev.hJCidx[1]],  ev.Jet_eta[ev.hJCidx[1]],  ev.Jet_phi[ev.hJCidx[1]],  ev.Jet_mass[ev.hJCidx[1]])

  proj0 = projectionMETOntoJet(ev.met_pt, ev.met_phi, j0.Pt() , j0.Phi(), False, 999)
  dPhi0= deltaPhi(ev.met_phi,  j0.Phi())    
  proj1 = projectionMETOntoJet(ev.met_pt, ev.met_phi, j1.Pt() ,j1.Phi(), False, 999)
  dPhi1= deltaPhi(ev.met_phi,  j1.Phi())    

  if recoverAlsoFSR:
      FSRjet = ROOT.TLorentzVector()
      idxtoAdd = []
      idxtoAdd =  [x for x in range(ev.nJet)  if ( x not in ev.hJCidx and ev.Jet_pt[x]>15. and abs(ev.Jet_eta[x])<3.0 and  ev.Jet_id[x]>=3 and ev.Jet_puId[x]>=4 and  min( deltaR(ev.Jet_eta[x],ev.Jet_phi[x], j0.Eta(), j0.Phi()), deltaR(ev.Jet_eta[x],ev.Jet_phi[x], j1.Eta(), j1.Phi() ) ) <0.8 )  ] 
      for ad in idxtoAdd:        
            FSRjet.SetPtEtaPhiM( ev.Jet_pt[ad],  ev.Jet_eta[ad],  ev.Jet_phi[ad],  ev.Jet_mass[ad])
            dR0 = deltaR(ev.Jet_eta[ad],ev.Jet_phi[ad], j0.Eta(), j0.Phi() )
            dR1 = deltaR(ev.Jet_eta[ad],ev.Jet_phi[ad], j1.Eta(), j1.Phi() )
            if dR0<dR1:
                   j0 +=FSRjet
            else:
                   j1 +=FSRjet


  if not tryAlsoWNoLept:
      if (lep0pt>0 or lep1pt>0):  
              if ( (abs(dPhi0)<abs(dPhi1)) and lep0pt>0) :
                  nu.SetPtEtaPhiM( proj0,  j0.Eta(),  j0.Phi(), 0)
                  j0+=nu
              elif ( (abs(dPhi0)>abs(dPhi1))  and lep1pt>0 ):
                  nu.SetPtEtaPhiM( proj1,  j1.Eta(),  j1.Phi(), 0)
                  j1+=nu

      return (j0+j1).M()
 
  else : 
          if (abs(dPhi0)<abs(dPhi1)) :
                 nu.SetPtEtaPhiM( proj0,  j0.Eta(),  j0.Phi(), 0)
                 j0+=nu
          else:
                 nu.SetPtEtaPhiM( proj1,  j1.Eta(),  j1.Phi(), 0)
                 j1+=nu
  
  return (j0+j1).M()



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

def weight_bTag_online():
    return 0.89

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


# utilities
corrector = Xbb_trigger_corrector(fname="../data/X750_trigger_efficiency.root", switch=165.)

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
    #f = ROOT.TFile("/afs/cern.ch/work/d/degrutto/private/Xbbanalysis/CMSSW_7_6_3_patch2/src/Hbb/files/"+argv[1]+".root", "RECREATE")
    f = ROOT.TFile("/scratch/bianchi/"+argv[1]+".root", "RECREATE")
else:
    #f = ROOT.TFile("/afs/cern.ch/work/d/degrutto/private/Xbbanalysis/CMSSW_7_6_3_patch2/src/Hbb/files/"+argv[1]+"_"+argv[2]+"_"+argv[3]+".root", "RECREATE")
    f = ROOT.TFile("/scratch/bianchi/"+argv[1]+"_"+argv[2]+"_"+argv[3]+".root", "RECREATE")

lumi_factor = sample_to_process[1]*luminosity/processed if processed>0 else -1
print "Luminosity: %.0f pb-1 --- xsection: %.0f pb --- Processed: %.0f ==> Lumi factor: %.2f" % (luminosity, sample_to_process[1], processed, lumi_factor)

# True if one cut implies all those before

cuts_Vtype = {  
    "Had" : lambda ev : ev.Vtype in [-1,4],
    "Lep" : lambda ev : ev.Vtype in [0,1,2,3],
}

cuts_BTag = {
    ##"All" :  lambda ev : True,
    "LT" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.460) if len(ev.hJCidx)==2 else False,
    ##"LT_CSVSFUp" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.460) if len(ev.hJCidx)==2 else False,
    ##"LT_CSVSFDown" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.460) if len(ev.hJCidx)==2 else False,
    ##"nMT" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]<0.800 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.460) if len(ev.hJCidx)==2 else False,
    #"MT" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.800) if len(ev.hJCidx)==2 else False,
    #"MT_CSVSFUp" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.800) if len(ev.hJCidx)==2 else False,
    #"MT_CSVSFDown" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.800) if len(ev.hJCidx)==2 else False,
    ##"TT" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.935) if len(ev.hJCidx)==2 else False,
    ##"TT_CSVSFUp" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.935) if len(ev.hJCidx)==2 else False,
    ##"TT_CSVSFDown" : lambda ev : (ev.Jet_btagCSV[ev.hJCidx[0]]>0.935 and ev.Jet_btagCSV[ev.hJCidx[1]]>0.935) if len(ev.hJCidx)==2 else False,
}

cuts_MinPt = {
    ##"All" :  lambda ev : True,
    ##"MinPt200" : lambda ev :  min(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]])>200. if len(ev.hJCidx)==2 else False,
    ##"MinPt175" : lambda ev :  min(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]])>175. if len(ev.hJCidx)==2 else False,
    ##"MinPt150" : lambda ev :  min(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]])>150. if len(ev.hJCidx)==2 else False,
    "MinPt100" : lambda ev :  min(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]])>100. if len(ev.hJCidx)==2 else False,
    #"MinPt100_HLT" : lambda ev :  (min(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]])>100. if len(ev.hJCidx)==2 else False) and (ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p85_DoublePFJetsC160_v | ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p9_DoublePFJetsC100MaxDeta1p6_v),
    #"MinPt100_HLTKinUp" : lambda ev :  min(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]])>100. if len(ev.hJCidx)==2 else False,
    #"MinPt100_HLTKinDown" : lambda ev :  min(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]])>100. if len(ev.hJCidx)==2 else False,
    ##"MinMaxPt100150" : lambda ev :  min(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]])>100. and  max(ev.Jet_pt[ev.hJCidx[0]], ev.Jet_pt[ev.hJCidx[1]])>150. if len(ev.hJCidx)==2 else False,
}

cuts_DH = {
    ##"All" :  lambda ev : True,
    "DH2p0" :  lambda ev : abs(ev.Jet_eta[ev.hJCidx[0]]-ev.Jet_eta[ev.hJCidx[1]])<2.0  if len(ev.hJCidx)==2 else False,
    #"DH1p6" :  lambda ev : abs(ev.Jet_eta[ev.hJCidx[0]]-ev.Jet_eta[ev.hJCidx[1]])<1.6  if len(ev.hJCidx)==2 else False,
    #"DH1p1" :  lambda ev : abs(ev.Jet_eta[ev.hJCidx[0]]-ev.Jet_eta[ev.hJCidx[1]])<1.1  if len(ev.hJCidx)==2 else False,
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
                # do not run all combinations...
                if "Lep" in cut_Vtype:
                    if ("LT" not in cut_BTag) or cut_DH!="DH2p0":
                        print "Reject", cut_name
                        continue
                    if "HLTKin" in cut_MinPt:
                        print "Reject", cut_name
                        continue
                elif "Had" in cut_Vtype:
                    if "HLTKin" in cut_MinPt and (cut_DH!="DH1p6" or cut_BTag!="MT" or "CSV" in cut_BTag):
                        print "Reject", cut_name
                        continue
                    if "CSV" in cut_BTag and cut_DH=="DH2p0":
                        print "Reject", cut_name
                        continue
                    if "MT" in cut_BTag and cut_DH=="DH2p0":
                        print "Reject", cut_name
                        continue                    
                    if "LT" in cut_BTag and cut_DH=="DH1p6":
                        print "Reject", cut_name
                        continue                    
                print "Add", cut_name

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
    #"Mass_JECUp" : ROOT.TH1F(cut[0]+"_Mass_JECUp", argv[1]+": "+cut[0]+"_Mass_JECUp", 180, 400, 4000),
    #"Mass_JECDown" : ROOT.TH1F(cut[0]+"_Mass_JECDown", argv[1]+": "+cut[0]+"_Mass_JECDown", 180, 400, 4000),
    #"Mass_JERUp" : ROOT.TH1F(cut[0]+"_Mass_JERUp", argv[1]+": "+cut[0]+"_Mass_JERUp", 180, 400, 4000),
    #"Mass_JERDown" : ROOT.TH1F(cut[0]+"_Mass_JERDown", argv[1]+": "+cut[0]+"_Mass_JERDown", 180, 400, 4000),
    "MassFSR" : ROOT.TH1F(cut[0]+"_MassFSR", argv[1]+": "+cut[0]+"_MassFSR", 37000, 300, 4000), #37000 bins
    "MassFSR_JECUp" : ROOT.TH1F(cut[0]+"_MassFSR_JECUp", argv[1]+": "+cut[0]+"_MassFSR_JECUp", 3700, 300, 4000),
    "MassFSR_JECDown" : ROOT.TH1F(cut[0]+"_MassFSR_JECDown", argv[1]+": "+cut[0]+"_MassFSR_JECDown", 3700, 300, 4000),
    "MassFSR_JERUp" : ROOT.TH1F(cut[0]+"_MassFSR_JERUp", argv[1]+": "+cut[0]+"_MassFSR_JERUp", 3700, 300, 4000),
    "MassFSR_JERDown" : ROOT.TH1F(cut[0]+"_MassFSR_JERDown", argv[1]+": "+cut[0]+"_MassFSR_JERDown", 3700, 300, 4000),
    "MassFSRProjMET" : ROOT.TH1F(cut[0]+"_MassFSRProjMET", argv[1]+": "+cut[0]+"_MassFSRProjMET", 180, 300, 4000),
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
    "Eff_HLTLow_vsMassFSR" : ROOT.TH1F(cut[0]+"_Eff_HLTLow_vsMassFSR", argv[1]+": "+cut[0]+"_Eff_HLTLow_vsMassFSR",  100, 0, 2000),
    "Eff_HLTHigh_vsMassFSR" : ROOT.TH1F(cut[0]+"_Eff_HLTHigh_vsMassFSR", argv[1]+": "+cut[0]+"_Eff_HLTHigh_vsMassFSR",  100, 0, 2000),
    "Eff_HLTLow_vsMaxJetPt" : ROOT.TH1F(cut[0]+"_Eff_HLTLow_vsMaxJetPt", argv[1]+": "+cut[0]+"_Eff_HLTLow_vsMaxJetPt",  70, 90, 790),
    "Eff_HLTLow_vsMinJetPt" : ROOT.TH1F(cut[0]+"_Eff_HLTLow_vsMinJetPt", argv[1]+": "+cut[0]+"_Eff_HLTLow_vsMinJetPt",  70, 90, 790),
    "Eff_HLTHigh_vsMaxJetPt" : ROOT.TH1F(cut[0]+"_Eff_HLTHigh_vsMaxJetPt", argv[1]+": "+cut[0]+"_Eff_HLTHigh_vsMaxJetPt",  70, 90, 790),
    "Eff_HLTHigh_vsMinJetPt" : ROOT.TH1F(cut[0]+"_Eff_HLTHigh_vsMinJetPt", argv[1]+": "+cut[0]+"_Eff_HLTHigh_vsMinJetPt",  70, 90, 790),
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
chain.SetBranchStatus("HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p85_DoublePFJetsC160_v", True)
chain.SetBranchStatus("HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p9_DoublePFJetsC100MaxDeta1p6_v", True)

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
    variables["MassFSRProjMET"] =  projMetOntoH(ev, True, True) 

    variables["MassAK08"] = ak08_mass(ev) 
    variables["njetAK08"] = getattr(ev, "nFatjetAK08ungroomed", 2)
    variables["Pt"] = ev.HCSV_pt 
    variables["Eta"] = ev.HCSV_eta 
    variables["MaxEta"] = max(abs(ev.Jet_eta[ev.hJCidx[0]]),abs(ev.Jet_eta[ev.hJCidx[1]])) if len(ev.hJCidx)==2 else 99 
    variables["Vtype"] = ev.Vtype 
    variables["Eff_HLTLow_vsMassFSR"] = variables["MassFSR"] if (ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p9_DoublePFJetsC100MaxDeta1p6_v and not ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p85_DoublePFJetsC160_v ) else 0.0
    variables["Eff_HLTHigh_vsMassFSR"] = variables["MassFSR"] if (ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p85_DoublePFJetsC160_v and not ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p9_DoublePFJetsC100MaxDeta1p6_v ) else 0.0

    variables["Eff_HLTLow_vsMaxJetPt"] = variables["MaxJetPt"] if (ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p9_DoublePFJetsC100MaxDeta1p6_v and not ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p85_DoublePFJetsC160_v ) else 90
    variables["Eff_HLTHigh_vsMaxJetPt"] = variables["MaxJetPt"] if (ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p85_DoublePFJetsC160_v and not ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p9_DoublePFJetsC100MaxDeta1p6_v ) else 90
    variables["Eff_HLTLow_vsMinJetPt"] = variables["MinJetPt"] if (ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p9_DoublePFJetsC100MaxDeta1p6_v and not ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p85_DoublePFJetsC160_v ) else 90
    variables["Eff_HLTHigh_vsMinJetPt"] = variables["MinJetPt"] if (ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p85_DoublePFJetsC160_v and not ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p9_DoublePFJetsC100MaxDeta1p6_v ) else 90

    variables["DeltaEta"] = abs(ev.Jet_eta[ev.hJCidx[0]] - ev.Jet_eta[ev.hJCidx[1]])  if len(ev.hJCidx)==2 else 99 
    variables["DeltaPhi"] = math.acos(math.cos(ev.Jet_phi[ev.hJCidx[0]] - ev.Jet_phi[ev.hJCidx[1]]))  if len(ev.hJCidx)==2 else 99 

    passall = True
    for cut in cuts_map:
        if cut[1](ev) and passall:
          #print cut[0], ": pass" 
          weight_btag = weight_bTag(ev, cut[0]) if lumi_factor>0 else 1.0

          weight_kin = 1.0
          if lumi_factor>0:
              #hlt = "high" if (ev.Jet_pt[ev.hJCidx[0]]>corrector.get_switch() and ev.Jet_pt[ev.hJCidx[0]]>corrector.get_switch() ) else "low"
              #for ind in [0,1]:
              #    weight_kin *= corrector.eval( ev.Jet_pt[ev.hJCidx[ind]], ev.Jet_eta[ev.hJCidx[ind]], hlt, cut[0] )          

              lead = 0.
              trail= 0.
              ilead = 0
              itrail = 1
              for ipt,pt in enumerate(ev.Jet_pt):
                  if abs(ev.Jet_eta[ipt])<2.5:                      
                      if pt>lead:
                          lead = pt
                          ilead = ipt
              for ipt,pt in enumerate(ev.Jet_pt):
                  if ipt==ilead:
                      continue
                  if abs(ev.Jet_eta[ipt])<2.5:                      
                      if pt>trail:
                          trail = pt
                          itrail = ipt

              weight_kin *= corrector.eval_OR( pt1=ev.Jet_pt[ilead], eta1=ev.Jet_eta[ilead], pt2=ev.Jet_pt[itrail], eta2=ev.Jet_eta[itrail],
                                               pass_low=ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p9_DoublePFJetsC100MaxDeta1p6_v,
                                               pass_high=ev.HLT_BIT_HLT_DoubleJetsC100_DoubleBTagCSV0p85_DoublePFJetsC160_v,
                                               syst=cut[0] )

          weight_btag_online = weight_bTag_online() if lumi_factor>0 else 1.0

          if cut[0]!="All" :
            eff_map[cut[0]] += weight(ev, lumi_factor)*weight_btag*weight_kin*weight_btag_online
          for var in histo_map[cut[0]].keys():
            histo_map[cut[0]][var].Fill(variables[var], weight(ev,lumi_factor)*weight_btag*weight_kin*weight_btag_online)
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

