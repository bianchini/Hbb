from sys import argv
argv.append( '-b-' )

import ROOT
from ROOT import RooFit
ROOT.gROOT.SetBatch(True)
argv.remove( '-b-' )

import numpy as n

import math
import sys
sys.path.append('./')

sqrts = 1.3e+04

PdfsFTest = {
    "pol" : {
        "FirstOrder" : 4,
        "LastOrder" : 9,
        "Match" : -1,
        "MaxOrder" : 6,
        },
    "exp" : {
        "FirstOrder" : 1,
        "LastOrder" : 4,
        "Match" : -1,
        "MaxOrder" : 3,
        },
    "pow" : {
        "FirstOrder" : 1,
        "LastOrder" : 4,
        "Match" : -1,
        "MaxOrder" : 2,
        },
    "polyexp" : {
        "FirstOrder" : 1,
        "LastOrder" : 5,
        "Match" : -1,
        "MaxOrder" : 3,
        },
    "dijet" : {
        "FirstOrder" : 1,
        "LastOrder" : 3,
        "Match" : -1,
        "MaxOrder" : 2,
        },
}

# global variables (for memory issues)
gcs = []

class BiasStudy:

    def __init__(self, fname="", ws_name="Xbb_workspace", version="V4", saveDir="/scratch/bianchi/"):
        self.fname = fname
        self.file = ROOT.TFile.Open(saveDir+"/"+version+"/"+fname+".root", "READ")
        if self.file==None or self.file.IsZombie():
            print "No file with name ", saveDir+"/"+version+"/"+fname+".root", " could be opened!"
            return
        self.ws_name = ws_name
        self.version = version
        self.saveDir = saveDir+'/'+version+'/'
        self.w = self.file.Get(ws_name)
        self.x = self.w.var("x")        

    def generate_pdf(self, pdf_name="pol", n_param=4, n_iter=0):

        pdf = None
        coeff = ROOT.RooArgList()

        if pdf_name=="pol":            
            coeff.removeAll()
            for p in xrange(n_param):
                param = ROOT.RooRealVar( ("a%d_deg%d_%d" % (p,n_param,n_iter)), "", -1.5, 1.5)
                if p==0:
                    param.setVal(1.)
                    param.setConstant(1)
                gcs.append(param)
                coeff.add(param)
            coeff.Print()
            pdf = ROOT.RooBernstein( ("pol_deg%d_%d" % (n_param,n_iter)) , "", self.x, coeff)

        elif pdf_name=="exp":            
            coeff.removeAll()
            formula = "TMath::Exp("
            for p in xrange(n_param):
                p_name = ("a%d_deg%d_%d" % (p,n_param,n_iter))
                formula += p_name
                for exp in xrange(p+1):
                    formula += "*x"
                p_min = -1e-04 if p!=0 else -0.2
                p_max = +1e-04 if p!=0 else -0.
                param = ROOT.RooRealVar( p_name, "", p_min, p_max)
                gcs.append(param)
                coeff.add(param)
                if p<(n_param-1):
                    formula += " + "
            formula += ")"
            print formula
            coeff.add(self.x)
            coeff.Print()
            pdf = ROOT.RooGenericPdf( ("exp_deg%d_%d" % (n_param,n_iter)), "", formula, coeff )

        elif pdf_name=="pow":            
            coeff.removeAll()
            formula = "TMath::Power(x, "
            for p in xrange(n_param):
                p_name = ("a%d_deg%d_%d" % (p,n_param,n_iter))
                formula += p_name
                for exp in xrange(p):
                    formula += "*x"
                p_min = -ROOT.TMath.Power(10,-3*p + 1)
                p_max = +ROOT.TMath.Power(10,-3*p + 1) 
                param = ROOT.RooRealVar( p_name, "", p_min, p_max)
                gcs.append(param)
                if p<(n_param-1):
                    formula += " + "
                coeff.add(param)
            formula += ")"
            print formula
            coeff.add(self.x)
            coeff.Print()
            pdf = ROOT.RooGenericPdf( ("pow_deg%d_%d" % (n_param,n_iter)), "", formula, coeff )

        elif pdf_name=="polyexp":            
            coeff.removeAll()
            formula = "TMath::Max(1e-50,"
            for p in xrange(n_param):
                p_name = ("a%d_deg%d_%d" % (p,n_param,n_iter))
                p_min = -5. if p!=0 else -0.2
                p_max = +5. if p!=0 else -0.
                param = ROOT.RooRealVar( p_name, "", p_min, p_max)
                gcs.append(param)
                coeff.add(param)
                if p==0:
                    formula += "TMath::Exp(x*" + p_name
                elif p==1:
                    formula += ")*(1+"+p_name+"*x"
                else:
                    formula += (" + " + p_name)
                    for exp in xrange(p):
                        formula += "*x"
                    if p<(n_param-1):
                        formula += " + "
            formula += "))"
            print formula
            coeff.add(self.x)
            coeff.Print()
            pdf = ROOT.RooGenericPdf( ("polyexp_deg%d_%d" % (n_param,n_iter)), "", formula, coeff )

        elif pdf_name=="dijet":            
            coeff.removeAll()
            formula = ""
            if n_param==1:
                formula = ("TMath::Max(1e-50,1./TMath::Power(x/%E, @0))" % (sqrts))
            elif n_param==2:
                formula = ("TMath::Max(1e-50,1./TMath::Power(x/%E, @0 + @1*TMath::Log(x/%E)))" % (sqrts, sqrts))
            elif n_param==3:
                formula = ("TMath::Max(1e-50,1./TMath::Power(x/%E, @0 + @1*TMath::Log(x/%E))*TMath::Power(1-x/%E,@2))" % (sqrts, sqrts, sqrts))
            for p in xrange(n_param):
                p_name = ("a%d_deg%d_%d" % (p,n_param,n_iter))
                p_min = -1.
                p_max = +1.
                if p==0:
                    p_min = 0.
                    p_max = 20.
                elif p==1:
                    p_min = -5.
                    p_max = +5.
                elif p==2:
                    p_min = 0.
                    p_max = 10.
                param = ROOT.RooRealVar( p_name, "", p_min, p_max)
                gcs.append(param)
                coeff.add(param)

            print formula
            coeff.add(self.x)
            coeff.Print()
            pdf = ROOT.RooGenericPdf( ("dijet_deg%d_%d" % (n_param,n_iter)), "", formula, coeff )

        pdf.Print()
        return pdf

    def get_save_name(self):
        return "ftest_"+self.fname

    def plot(self, data=None, pdfs=[], probs=[], npars=[], legs=[], title=""):

        c1 = ROOT.TCanvas("c1_"+self.get_save_name()+"_"+title,"c1",600,600)

        leg = ROOT.TLegend(0.15,0.65,0.45,0.88, "","brNDC")
        leg.SetHeader("F-test: "+title)  
        leg.SetFillStyle(0)
        leg.SetBorderSize(0)
        leg.SetTextSize(0.04)
        leg.SetFillColor(10)    

        frame = self.x.frame()
        frame.SetName("frame")
        frame.SetTitle("")
        frame.GetYaxis().SetTitleSize(20)
        frame.GetYaxis().SetTitleFont(43)
        frame.GetYaxis().SetTitleOffset(1.35)
        frame.GetYaxis().SetLabelFont(43) 
        frame.GetYaxis().SetLabelSize(15)

        data.plotOn(frame, RooFit.Name("data"))
        for p,pdf in enumerate(pdfs):
            opt_color = RooFit.LineColor(1+p) 
            pdf.plotOn(frame, RooFit.LineColor(1+p), RooFit.LineStyle(ROOT.kSolid), RooFit.Name(pdf.GetName()))

        frame.Draw()
        for p,pdf in enumerate(pdfs):
            chi2 = frame.chiSquare(pdf.GetName(), "data", npars[p] )
            leg.AddEntry(frame.getCurve(pdf.GetName()), legs[p]+(", #chi^{2}=%.2f, p=%.3f" % (chi2,probs[p])), "L")
        leg.Draw()

        c1.SaveAs(self.saveDir+self.get_save_name()+"_"+title+".png")
        return


    def doFTest(self, data_name="data_bkg", test_pdfs=[]):

        self.data = self.w.data(data_name)
        self.data.Print()

        for pdf_name in test_pdfs:
            pdfs = []
            npars = []
            legs = []
            probs = []
            firstOrder = PdfsFTest[pdf_name]["FirstOrder"]
            lastOrder = PdfsFTest[pdf_name]["LastOrder"]
            prevNll = 0.
            match = False
            for p in range(firstOrder, lastOrder+1):
                pdf = self.generate_pdf(pdf_name=pdf_name, n_param=p, n_iter=0)
                if pdf==None:
                    print "No pdf"
                    return
                res = pdf.fitTo(self.data, RooFit.Strategy(1), RooFit.Minimizer("Minuit2"), RooFit.Minos(1), RooFit.Save(1))
                pdfs.append(pdf)
                npars.append(p)
                legs.append("ndof: %d" % p)
                thisNll = res.minNll()
                if p==firstOrder:
                    prevNll = thisNll
                    probs.append(0.)
                    continue
                chi2 = 2*(prevNll-thisNll)
                prob = ROOT.TMath.Prob(abs(chi2), 1)
                print "Param: ", p
                print "\t", prevNll
                print "\t", thisNll
                print "\t", chi2 
                print "\t", prob 
                probs.append(prob)
                if thisNll<prevNll:
                    prevNll = thisNll
                if prob>0.05 and not match:
                    PdfsFTest[pdf_name]["Match"] = p-1
                    match = True
            self.plot(data=self.data, pdfs=pdfs, probs=probs, npars=npars, legs=legs, title=pdf_name)

        print PdfsFTest
        return

    def doBiasStudy(self, pdf_alt_name="dijet", pdf_fit_name="dijet", data_name="data_bkg", n_bins=-1, pdf_sgn_name="buk", sgn_name="Spin0_M750", sgn_xsec=0., ntoys=10):

        self.out = ROOT.TFile.Open(self.saveDir+"/"+self.get_save_name()+"_bias.root", "RECREATE") 
        tree = ROOT.TTree("toys","")
        # sgn/bkg normalisation from toy fit
        ns_fit = n.zeros(1, dtype=float) 
        nb_fit = n.zeros(1, dtype=float)
        # sgn/bkg normalisation error from toy fit
        ns_err = n.zeros(1, dtype=float)
        nb_err = n.zeros(1, dtype=float)
        # number of sgn/bkg events generated in toy
        ns_gen = n.zeros(1, dtype=float)
        nb_gen = n.zeros(1, dtype=float)
        # central value of sgn/bkg normalisation used for toy generation 
        ns_asy = n.zeros(1, dtype=float)
        nb_asy = n.zeros(1, dtype=float)
        # expected signal yield from workspace
        ns_exp = n.zeros(1, dtype=float)

        tree.Branch('ns_fit', ns_fit, 'ns_fit/D')
        tree.Branch('ns_gen', ns_gen, 'ns_gen/D')
        tree.Branch('ns_err', ns_err, 'ns_err/D')
        tree.Branch('ns_asy', ns_asy, 'ns_asy/D')
        tree.Branch('ns_exp', ns_exp, 'ns_asy/D')
        tree.Branch('nb_fit', nb_fit, 'nb_fit/D')
        tree.Branch('nb_gen', nb_gen, 'nb_gen/D')
        tree.Branch('nb_err', nb_err, 'nb_err/D')
        tree.Branch('nb_asy', nb_asy, 'nb_asy/D')

        # make sure we use random numbers
        ROOT.RooRandom.randomGenerator().SetSeed(0)

        # data set for initial fit
        self.data = self.w.data(data_name)
        self.data.Print()      
        self.x.setBins(self.data.numEntries() if n_bins<0 else n_bins)
        print "Total number of bins: ", self.x.getBins()

        # sgn pdf
        pdf_sgn = self.w.pdf(pdf_sgn_name+"_pdf_sgn_"+sgn_name)
        self.w.var("mean_sgn_"+sgn_name).setConstant(1)
        self.w.var("sigma_sgn_"+sgn_name).setConstant(1)
        sgn_norm = self.w.var(pdf_sgn_name+"_pdf_sgn_"+sgn_name+"_norm")
        sgn_norm_val = sgn_norm.getVal()
        sgn_norm.setVal(sgn_norm_val*sgn_xsec if sgn_xsec>0. else sgn_norm_val)
        pdf_sgn_ext = ROOT.RooExtendPdf("pdf_sgn_ext","", pdf_sgn, sgn_norm)

        # fit the alternative pdf to data (use it for toy generation)
        pdf_bkg_alt = self.generate_pdf(pdf_name=pdf_alt_name, n_param=PdfsFTest[pdf_alt_name]['MaxOrder'], n_iter=0)
        res_bkg_alt = pdf_bkg_alt.fitTo(self.data, RooFit.Strategy(1), RooFit.Minimizer("Minuit2"), RooFit.Minos(1), RooFit.Save(1))        
        # normalise the background to data_obs
        bkg_norm = ROOT.RooRealVar("bkg_norm", "", self.w.data("data_obs").sumEntries())
        pdf_bkg_alt_ext = ROOT.RooExtendPdf("pdf_bkg_alt_ext","", pdf_bkg_alt, bkg_norm)

        n_s = ROOT.RooRealVar("n_s","", -5000., +5000.)
        n_b = ROOT.RooRealVar("n_b","", bkg_norm.getVal()-10*math.sqrt(bkg_norm.getVal()), bkg_norm.getVal()+10*math.sqrt(bkg_norm.getVal()))
        pdf_bkg_fit = self.generate_pdf(pdf_name=pdf_fit_name, n_param=PdfsFTest[pdf_alt_name]['MaxOrder'], n_iter=1)
        pdf_fit_ext = ROOT.RooAddPdf("pdf_fit_ext","", ROOT.RooArgList(pdf_sgn,pdf_bkg_fit),  ROOT.RooArgList(n_s,n_b))

        ntoy = 0
        while ntoy<ntoys:
            data_toy = pdf_bkg_alt_ext.generateBinned(ROOT.RooArgSet(self.x), RooFit.Extended())
            data_toy_sgn = None
            if sgn_xsec>0.:
                data_toy_sgn = pdf_sgn_ext.generateBinned(ROOT.RooArgSet(self.x), RooFit.Extended())
                data_toy.add(data_toy_sgn)

            nb_toy = data_toy.sumEntries() - (data_toy_sgn.sumEntries() if data_toy_sgn!=None else 0.)
            ns_toy = data_toy_sgn.sumEntries() if data_toy_sgn!=None else 0.
            n_toy = data_toy.sumEntries()

            res_fit = pdf_fit_ext.fitTo(data_toy, RooFit.Strategy(1), RooFit.Minimizer("Minuit2"), RooFit.Minos(1), RooFit.Save(1))
            if res_fit==None or res_fit.status()!=0:
                continue                
            print "Nb=%.0f -- Ns=%.0f ==> tot:  %.0f" % (nb_toy, ns_toy, n_toy)
            print ">>>>>>>>>>", n_s.getVal()/n_s.getError()
            ns_fit[0] = n_s.getVal()
            ns_err[0] = n_s.getError()
            ns_gen[0] = ns_toy
            ns_asy[0] = sgn_norm.getVal()
            ns_exp[0] = sgn_norm_val
            nb_fit[0] = n_b.getVal()
            nb_err[0] = n_b.getError()
            nb_gen[0] = nb_toy
            nb_asy[0] = bkg_norm.getVal()
            tree.Fill()
            ntoy += 1

        self.out.cd()
        tree.Write("", ROOT.TObject.kOverwrite)
        self.out.Close()

########################

test_pdfs= [
    #"pol", 
    #"exp", 
    #"pow", 
    #"polyexp", 
    "dijet"
    ]

bs = BiasStudy(fname="Xbb_workspace_Had_MT_MinPt150_DH1p6_MassFSR_550to1200", 
               ws_name="Xbb_workspace", version="V4", saveDir="/scratch/bianchi/")

bs.doFTest(data_name="data_obs", test_pdfs=test_pdfs )
#bs.doBiasStudy(pdf_alt_name="dijet", pdf_fit_name="dijet", data_name="data_bkg", n_bins=100, pdf_sgn_name="buk", sgn_name="Spin0_M750", sgn_xsec=0., ntoys=1)

for gc in gcs:
    gc.Print()
