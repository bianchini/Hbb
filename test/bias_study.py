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
sys.path.append('../python/')

from utilities import *

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
                #pdf = self.generate_pdf(pdf_name=pdf_name, n_param=p, n_iter=0)[0]
                pdf = generate_pdf(self.x, pdf_name=pdf_name, n_param=p, n_iter=0, gcs=gcs)[0]
                if pdf==None:
                    print "No pdf"
                    continue
                res = pdf.fitTo(self.data, RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Minos(1), RooFit.Save(1))
                pdfs.append(pdf)

                par_fixed=0
                if pdf_name=="pol":
                    par_fixed += 1
                elif pdf_name=="dijet" and p==5:
                    par_fixed += 1

                npars.append(p-par_fixed)

                legs.append("ndof: %d" % (p-par_fixed))
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

            h_rebinned = self.data.createHistogram("h_"+data_name+"_rebinned", self.x, RooFit.Binning( int((self.x.getMax()-self.x.getMin())/5.0) , self.x.getMin(), self.x.getMax()) )
            data_rebinned = ROOT.RooDataHist(data_name+"_rebinned","", ROOT.RooArgList(self.x), h_rebinned, 1.0)
            self.plot(data=data_rebinned, pdfs=pdfs, probs=probs, npars=npars, legs=legs, title=pdf_name)

        print PdfsFTest
        return

    def doBiasStudy(self, pdf_alt_name="dijet", pdf_fit_name="dijet", data_name="data_bkg", n_bins=-1, pdf_sgn_name="buk", sgn_name="Spin0_M750", sgn_xsec=0., ntoys=10, nproc=0):

        self.out = ROOT.TFile.Open(self.saveDir+"/"+self.get_save_name()+"_bias_"+pdf_alt_name+"_"+pdf_fit_name+"_"+data_name+"_"+pdf_sgn_name+"_"+sgn_name+"_"+("xsec%.0f" % sgn_xsec)+"_"+str(nproc)+".root", "RECREATE") 
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
        alt = n.zeros(1, dtype=int)
        fit = n.zeros(1, dtype=int)
        alt[0] = PdfsFTest.keys().index(pdf_alt_name)
        fit[0] = PdfsFTest.keys().index(pdf_fit_name)

        tree.Branch('ns_fit', ns_fit, 'ns_fit/D')
        tree.Branch('ns_gen', ns_gen, 'ns_gen/D')
        tree.Branch('ns_err', ns_err, 'ns_err/D')
        tree.Branch('ns_asy', ns_asy, 'ns_asy/D')
        tree.Branch('ns_exp', ns_exp, 'ns_asy/D')
        tree.Branch('nb_fit', nb_fit, 'nb_fit/D')
        tree.Branch('nb_gen', nb_gen, 'nb_gen/D')
        tree.Branch('nb_err', nb_err, 'nb_err/D')
        tree.Branch('nb_asy', nb_asy, 'nb_asy/D')
        tree.Branch('alt', alt, 'alt/I')
        tree.Branch('fit', fit, 'fit/I')

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
        pdf_bkg_alt = generate_pdf(x=self.x, pdf_name=pdf_alt_name, n_param=PdfsFTest[pdf_alt_name]['MaxOrder'], n_iter=0)[0]
        res_bkg_alt = pdf_bkg_alt.fitTo(self.data, RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Minos(1), RooFit.Save(1), RooFit.PrintLevel(-1), RooFit.PrintEvalErrors(0), RooFit.Warnings(ROOT.kFALSE))        
        res_bkg_alt.Print()

        # normalise the background to data_obs
        bkg_norm = ROOT.RooRealVar("bkg_norm", "", self.w.data("data_obs").sumEntries())
        pdf_bkg_alt_ext = ROOT.RooExtendPdf("pdf_bkg_alt_ext","", pdf_bkg_alt, bkg_norm)

        # fit the nominal pdf to data 
        pdf_bkg_nom = generate_pdf(x=self.x, pdf_name=pdf_fit_name, n_param=PdfsFTest[pdf_alt_name]['MaxOrder'], n_iter=1)[0]
        res_bkg_nom = pdf_bkg_nom.fitTo(self.data, RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Minos(1), RooFit.Save(1), RooFit.PrintLevel(-1), RooFit.PrintEvalErrors(0), RooFit.Warnings(ROOT.kFALSE))
        res_bkg_nom.Print()

        # save a snapshot of the initial fits
        h_rebinned = self.data.createHistogram("h_"+data_name+"_rebinned", self.x, RooFit.Binning( int((self.x.getMax()-self.x.getMin())/5.0) , self.x.getMin(), self.x.getMax()) )
        data_rebinned = ROOT.RooDataHist(data_name+"_rebinned","", ROOT.RooArgList(self.x), h_rebinned, 1.0)
        self.plot(data=data_rebinned, pdfs=[pdf_bkg_nom,pdf_bkg_alt], probs=[0.,0.], npars=[PdfsFTest[pdf_fit_name]['MaxOrder'],PdfsFTest[pdf_alt_name]['MaxOrder']], legs=["Nominal: "+pdf_fit_name,"Alternative: "+pdf_alt_name], title="bias_"+pdf_fit_name+"_"+pdf_alt_name)

        n_s = ROOT.RooRealVar("n_s","", 0., -1000., +1000.)
        n_b = ROOT.RooRealVar("n_b","", bkg_norm.getVal(), bkg_norm.getVal()-10*math.sqrt(bkg_norm.getVal()), bkg_norm.getVal()+10*math.sqrt(bkg_norm.getVal()))

        pdfs_bkg_fit = generate_pdf(x=self.x, pdf_name=pdf_fit_name, n_param=PdfsFTest[pdf_alt_name]['MaxOrder'], n_iter=2)
        pdf_bkg_fit = pdfs_bkg_fit[0]
        coeff_bkg_fit = pdfs_bkg_fit[1]
        coeff_bkg_fit_reset = []
        for p in xrange(coeff_bkg_fit.getSize()):
            coeff_bkg_fit_reset[p] = coeff_bkg_fit[p].getVal()

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

            # reset all fit parameters
            n_s.setVal(0.)
            n_b.setVal(bkg_norm.getVal())
            for p in xrange(coeff_bkg_fit.getSize()):
                coeff_bkg_fit[p].setVal(coeff_bkg_fit_reset[p])

            res_fit = pdf_fit_ext.fitTo(data_toy, RooFit.Strategy(1), RooFit.Minimizer("Minuit2", "migrad"), RooFit.Minos(1), RooFit.Save(1), RooFit.PrintLevel(-1), RooFit.PrintEvalErrors(0), RooFit.Warnings(ROOT.kFALSE), RooFit.Extended(ROOT.kTRUE))
            if res_fit==None or res_fit.status()!=0:
                continue                

            res_fit.Print()
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
    "pow", 
    #"polyexp", 
    #"dijet"
    #"polydijet"
    ]

cfg_fname = argv[1] if len(argv)>=2 else "Xbb_workspace_Had_MT_MinPt100_DH1p6_MassFSR_400to1200"
cfg_pdf_alt_name = argv[2] if len(argv)>=3 else "polydijet"
cfg_pdf_fit_name = argv[3] if len(argv)>=4 else "polydijet"
cfg_n_bins = int(argv[4]) if len(argv)>=5 else -1
cfg_pdf_sgn_name = argv[5] if len(argv)>=6 else "buk"
cfg_sgn_name = argv[6] if len(argv)>=7 else "Spin0_M750"
cfg_sgn_xsec = float(argv[7]) if len(argv)>=8 else 0.
cfg_ntoys = int(argv[8]) if len(argv)>=9 else 100
cfg_nproc = int(argv[9]) if len(argv)>=10 else -1

bs = BiasStudy(fname=cfg_fname, 
               ws_name="Xbb_workspace", version="V5", saveDir="./plots/")

#bs.doFTest(data_name="data_obs", test_pdfs=test_pdfs )
bs.doBiasStudy(pdf_alt_name=cfg_pdf_alt_name, pdf_fit_name=cfg_pdf_fit_name, data_name="data_obs", n_bins=cfg_n_bins, pdf_sgn_name=cfg_pdf_sgn_name, sgn_name=cfg_sgn_name, sgn_xsec=cfg_sgn_xsec, ntoys=cfg_ntoys, nproc=cfg_nproc)

for gc in gcs:
    gc.Print()
