from sys import argv
argv.append( '-b-' )
import ROOT
ROOT.gROOT.SetBatch(True)
argv.remove( '-b-' )
from ROOT import TLorentzVector

import math

f = ROOT.TFile("gen.root", "RECREATE")
h = ROOT.TH1F("mass","Mass after ISR",300,400,1000)
njet = ROOT.TH1F("njet","Numberr of genjets",5,0,5)
hjet = ROOT.TH1F("massJet","Mass with jets",50,0,800)
pt = ROOT.TH1F("pt","Pt after ISR",20,0,400)

ROOT.gSystem.Load("libFWCoreFWLite.so")
ROOT.gSystem.Load("libDataFormatsFWLite.so")
ROOT.FWLiteEnabler.enable()

from DataFormats.FWLite import Handle, Events

for ff in xrange(int(argv[2]), int(argv[3])):

    print argv[1]+("_%d.root" % ff)
    events = Events(argv[1]+("_%d.root" % ff))

    genH, genN = Handle("std::vector<reco::GenParticle>"), "genParticles"
    jetH, jetN = Handle("std::vector<reco::GenJet>"), "ak4GenJets"

    for i,event in enumerate(events):

        if i%10==0:
            print "Event", i, ", file n.", ff
        genbquarksFromH = []

        event.getByLabel(genN,genH)
        event.getByLabel(jetN,jetH)

        nj = sum( abs(j.eta())<2.5 and j.pt()>150 for j in jetH.product() )
        njet.Fill(nj)

        genParticles = list(genH.product())
        for np,p in enumerate(genParticles):
            #print " %5d: pdgId %+5d status %3d  pt %6.1f  " % (i, p.pdgId(),p.status(),p.pt())
            if p.pdgId() in [25, 5100039] and p.numberOfDaughters() > 0 and abs(p.daughter(0).pdgId()) not in  [25,5100039]:
                for d in xrange( p.numberOfDaughters() ):
                    if abs(p.daughter(d).pdgId()) == 5:
                    #print "\tAdd daughter with status " , p.daughter(d).status()
                        b = p.daughter(d)
                        genbquarksFromH.append( b )                                            

        bjets = []
        for nj,j in enumerate(list(jetH.product())):
            if abs(j.eta())<2.5 and j.pt()>150:
                for nb,b in enumerate(genbquarksFromH):
                    if math.sqrt( math.pow(j.eta()-b.eta(),2) + math.pow( math.acos(math.cos(j.phi()-b.phi())) ,2))<0.4:
                        bjets.append(j)

        sorted(bjets, lambda x,y : x.pt()>y.pt())
        if len(bjets)>=2 :        
            #print bjets[0].pt(), bjets[1].pt()
            dau1 = ROOT.TLorentzVector()
            dau1.SetPtEtaPhiM(bjets[0].pt(), bjets[0].eta(), bjets[0].phi(), bjets[0].mass())
            dau2 = ROOT.TLorentzVector()
            dau2.SetPtEtaPhiM(bjets[1].pt(), bjets[1].eta(), bjets[1].phi(), bjets[1].mass())        
            hjet.Fill((dau1+dau2).M())        

        if len(genbquarksFromH)==2:
            dau1 = ROOT.TLorentzVector()
            dau1.SetPtEtaPhiM(genbquarksFromH[0].pt(), genbquarksFromH[0].eta(), genbquarksFromH[0].phi(), genbquarksFromH[0].mass())
            dau2 = ROOT.TLorentzVector()
            dau2.SetPtEtaPhiM(genbquarksFromH[1].pt(), genbquarksFromH[1].eta(), genbquarksFromH[1].phi(), genbquarksFromH[1].mass())
            h.Fill((dau1+dau2).M())
            pt.Fill((dau1+dau2).Pt())


f.cd()
h.Write()
hjet.Write()
njet.Write()
pt.Write()
f.Close()
