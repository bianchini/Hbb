from sys import argv
argv.append( '-b-' )

import ROOT
from ROOT import RooFit
ROOT.gROOT.SetBatch(True)
argv.remove( '-b-' )

import numpy as n
import json
import math
import sys
sys.path.append('./')
sys.path.append('../python/')

from utilities import *

# global variables (for memory issues)
gcs = []

class BiasStudy:

    def __init__(self, fname="", ws_name="Xbb_workspace", read_dir="/scratch/bianchi/", save_dir="/scratch/bianchi/", save_ext=['png'], blind_plot=False):
        self.fname = fname
        self.file = ROOT.TFile.Open(read_dir+"/"+fname+".root", "READ")
        if self.file==None or self.file.IsZombie():
            print "No file with name ", save_dir+"/"+fname+".root", " could be opened!"
            return
        self.ws_name = ws_name
        self.save_dir = save_dir+'/'
        self.save_ext = save_ext
        self.w = self.file.Get(ws_name)
        self.x = self.w.var("x")        
        self.plot_blind = blind_plot

    def get_save_name(self):
        return "ftest_"+self.fname

    def plot(self, data=None, hdata=None, pdfs=[], params=[], res=[], probs=[], npars=[], legs=[], add_ratio=False, title="", header=""):

        c1 = ROOT.TCanvas("c1_"+self.get_save_name()+"_"+title,"c1",600,600)
        c1.cd()
        if add_ratio:
            pad1 = ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
            pad1.SetBottomMargin(0) 
            #pad1.SetGridx()  
            pad1.Draw()      
            pad1.cd()    

        leg = ROOT.TLegend(0.15,0.60,0.45,0.88, "","brNDC")
        leg.SetHeader(header)  
        leg.SetFillStyle(0)
        leg.SetBorderSize(0)
        leg.SetTextSize(0.06 if add_ratio else 0.04 )
        leg.SetFillColor(10)    

        frame = self.x.frame()
        frame.SetName("frame")
        frame.SetTitle("CMS Preliminary 2016 #sqrt{s}=13 TeV")
        frame.GetYaxis().SetTitle("Events / "+str(frame.GetXaxis().GetBinWidth(1))+" GeV")
        if not add_ratio:            
            frame.GetXaxis().SetTitle("mass (GeV)")

        frame.GetYaxis().SetTitleSize(20)
        frame.GetYaxis().SetTitleFont(43)
        frame.GetYaxis().SetTitleOffset(1.35)
        frame.GetYaxis().SetLabelFont(43) 
        frame.GetYaxis().SetLabelSize(15)
        frame.GetXaxis().SetTitleSize(20)
        frame.GetXaxis().SetTitleFont(43)
        frame.GetXaxis().SetLabelFont(43)
        frame.GetXaxis().SetLabelSize(15)

        data.plotOn(frame, RooFit.Name("data"))
        for p,pdf in enumerate(pdfs):
            opt_color = RooFit.LineColor(1+p) 
            pdf.plotOn(frame, RooFit.LineWidth(2), RooFit.LineColor(1+p), RooFit.LineStyle(ROOT.kSolid), RooFit.Name(pdf.GetName()))

        if add_ratio:
            pad1.cd()

        for p,pdf in enumerate(pdfs):
            chi2 = frame.chiSquare(pdf.GetName(), "data", npars[p] )
            label =  legs[p]+(", #chi^{2}=%.2f" % chi2)
            if "F-test" in header:
                label += (", P(-2#Deltalog(L))=%.2f" % probs[p])
            leg.AddEntry(frame.getCurve(pdf.GetName()), label, "L")

        if self.plot_blind:
            frame.remove("data", ROOT.kFALSE)
        frame.Draw()
        leg.Draw()

        frame2 = None
        if add_ratio:
            c1.cd()
            pad2 = ROOT.TPad("pad2", "pad2", 0, 0.05, 1, 0.3)
            pad2.SetTopMargin(0)
            pad2.SetBottomMargin(0.2)
            pad2.SetGridx()   
            pad2.SetGridy() 
            pad2.Draw()
            pad2.cd()       
            frame2 = self.x.frame(RooFit.Name("frame2"))
            frame2.SetTitle(self.get_save_name()+"_"+title)        
            hresids = []
            integrals = []

            hsyst = ROOT.TH1F("hsyst", "",  int((self.x.getMax()-self.x.getMin())/5.0), self.x.getMin(), self.x.getMax())
            hsyst.SetFillColor(ROOT.kBlack)
            hsyst.SetFillStyle(3004)
            leg.AddEntry(hsyst, "#sqrt{B_{i}/B}", "F")

            for p,pdf in enumerate(pdfs):
                integrals.append( pdf.createIntegral(ROOT.RooArgSet(self.x), "MassFSR").getVal() )
                param = params[p] 
                if p<1:
                    continue

                hresid = hdata.Clone(data.GetName()+"_ratio_"+pdf.GetName())
                hresid.SetLineColor(frame.getCurve(pdf.GetName()).GetLineColor())
                hresid.SetLineWidth(frame.getCurve(pdf.GetName()).GetLineWidth())
                hresid.SetLineStyle(ROOT.kSolid)                
                for bin in xrange(hresid.GetNbinsX()):
                    self.x.setVal( hresid.GetBinCenter(bin+1) )
                    bkg = hresid.GetBinContent(bin+1)
                    val = pdfs[p].getVal()/integrals[p] 
                    diff = (pdfs[p].getVal()/integrals[p]-pdfs[p-1].getVal()/integrals[p-1])/(pdfs[p-1].getVal()/integrals[p-1]) if pdfs[p-1].getVal()>0. else 0.
                    hresid.SetBinContent(bin+1, diff*math.sqrt(bkg))                        
                    hresid.SetBinError(bin+1, 0.)
                    hsyst.SetBinContent(bin+1, 0.)
                    hsyst.SetBinError(bin+1, math.sqrt(bkg/data.sumEntries()) )
                    print "At x=%.1f: ALT: %E (%E) --- FIT: %E (%E) ==> Bkg: %.0f : Delta: %.4f" % (self.x.getVal(), pdfs[p].getVal()/integrals[p], integrals[p], pdfs[p-1].getVal()/integrals[p-1] , integrals[p-1], bkg,  diff )

                hresid.SetMinimum( -1 )
                hresid.SetMaximum( +1. )
                frame2.addTH1(hresid, "L")
                frame2.addTH1(hsyst, "F")
                hresids.append(hresid)
                hresids.append(hsyst)

            frame2.SetTitle("") 
            frame2.GetYaxis().SetTitle("(Alt.-Nom.)/#sqrt{B_{i}}")
            frame2.GetYaxis().SetNdivisions(505)
            frame2.GetYaxis().SetTitleSize(20)
            frame2.GetYaxis().SetTitleFont(43)
            frame2.GetYaxis().SetTitleOffset(1.35)
            frame2.GetYaxis().SetLabelFont(43) 
            frame2.GetYaxis().SetLabelSize(15)
            frame2.GetXaxis().SetTitle("mass (GeV)")
            frame2.GetXaxis().SetTitleSize(20)
            frame2.GetXaxis().SetTitleFont(43)
            frame2.GetXaxis().SetTitleOffset(4.)
            frame2.GetXaxis().SetLabelFont(43) 
            frame2.GetXaxis().SetLabelSize(15)            
            frame2.Draw()    

        for ext in self.save_ext:
            c1.SaveAs(self.save_dir+self.get_save_name()+"_"+title+"."+ext)

        # for memory issues
        if hasattr(self, "out"):
            self.out.Remove(frame)
            if frame2!=None:
                self.out.Remove(frame2)

        return


    def doFTest(self, data_name="data_bkg", test_pdfs=[], parameter_set="default"):

        self.data = self.w.data(data_name)
        self.data.Print()

        is_data = (data_name=="data_obs") 

        mass_range = self.fname.split("_")[-1]        

        FTestCfg = {}
        if is_data:
            FTestCfg = FTestCfg_data
        else:
            FTestCfg = FTestCfg_mc  
            self.plot_blind = False  

        for pdf_name in test_pdfs:
            pdfs = []
            npars = []
            legs = []
            probs = []
            firstOrder = FTestCfg[pdf_name]["FirstOrder"]
            lastOrder = FTestCfg[pdf_name]["LastOrder"]
            prevNll = 0.
            match = False
            for p in range(firstOrder, lastOrder+1):
                [pdf,coeff] = generate_pdf(self.x, pdf_name=pdf_name, n_param=p, n_iter=0, gcs=gcs, 
                                           mass_range=mass_range, 
                                           parameter_set=parameter_set,
                                           is_data=is_data)
                if pdf==None:
                    print "No pdf"
                    continue
                res = pdf.fitTo(self.data, 
                                RooFit.Strategy(1), 
                                RooFit.Minimizer("Minuit2", "migrad"), 
                                RooFit.Minos(1), 
                                RooFit.Save(1), 
                                RooFit.PrintLevel(-1), 
                                RooFit.PrintEvalErrors(0),
                                RooFit.Warnings(ROOT.kFALSE))

                res.Print()
                res.correlationMatrix().Print()
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
                    FTestCfg[pdf_name]["Match"] = p-1
                    match = True

            h_rebinned = self.data.createHistogram("h_"+data_name+"_rebinned", self.x, RooFit.Binning( int((self.x.getMax()-self.x.getMin())/5.0) , self.x.getMin(), self.x.getMax()) )
            data_rebinned = ROOT.RooDataHist(data_name+"_rebinned","", ROOT.RooArgList(self.x), h_rebinned, 1.0)
            self.plot(data=data_rebinned, pdfs=pdfs, probs=probs, npars=npars, legs=legs, title=pdf_name+"_"+data_name, header="F-test: "+pdf_name)

        print FTestCfg
        return

    def doBiasStudy(self, pdf_alt_name="dijet", pdf_fit_name="dijet", data_name="data_bkg", n_bins=-1, pdf_sgn_name="buk", sgn_name="Spin0_M750", sgn_xsec=0., ntoys=10, nproc=0, randomize_params=False, parameter_set="default"):

        is_data = (data_name=="data_obs") 

        mass_range = self.fname.split("_")[-1]

        FTestCfg = {}
        if is_data:
            FTestCfg = FTestCfg_data
        else:
            FTestCfg = FTestCfg_mc    
            self.plot_blind = False

        self.out = ROOT.TFile.Open(self.save_dir+"/"+self.get_save_name()+"_bias_"+pdf_alt_name+"_"+pdf_fit_name+"_deg"+str(FTestCfg[pdf_fit_name]['ndof'][mass_range])+"_"+data_name+"_"+pdf_sgn_name+"_"+sgn_name+"_"+("xsec%.0f" % sgn_xsec)+"_"+str(nproc)+".root", "RECREATE") 
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

        # parameters
        nparams = n.zeros(1, dtype=int)
        params = n.zeros(8, dtype=float)

        # edm, minll
        edm = n.zeros(1, dtype=float)
        minll = n.zeros(1, dtype=float)

        # pdf index
        alt = n.zeros(1, dtype=int)
        fit = n.zeros(1, dtype=int)
        alt[0] = FTestCfg.keys().index(pdf_alt_name)
        fit[0] = FTestCfg.keys().index(pdf_fit_name)

        tree.Branch('ns_fit', ns_fit, 'ns_fit/D')
        tree.Branch('ns_gen', ns_gen, 'ns_gen/D')
        tree.Branch('ns_err', ns_err, 'ns_err/D')
        tree.Branch('ns_asy', ns_asy, 'ns_asy/D')
        tree.Branch('ns_exp', ns_exp, 'ns_asy/D')
        tree.Branch('nb_fit', nb_fit, 'nb_fit/D')
        tree.Branch('nb_gen', nb_gen, 'nb_gen/D')
        tree.Branch('nb_err', nb_err, 'nb_err/D')
        tree.Branch('nb_asy', nb_asy, 'nb_asy/D')
        tree.Branch('nparams', nparams, 'nparams/I')
        tree.Branch('params', params, 'params[nparams]/D')
        tree.Branch('edm', edm, 'edm/D')
        tree.Branch('minll', minll, 'minll/D')
        tree.Branch('alt', alt, 'alt/I')
        tree.Branch('fit', fit, 'fit/I')

        # make sure we use random numbers
        ROOT.RooRandom.randomGenerator().SetSeed(0)

        # data set for initial fit
        self.data = self.w.data(data_name)
        self.data.Print()      
        self.x.setBins(self.data.numEntries() if n_bins<0 else n_bins)
        print "Total number of bins: ", self.x.getBins()

        # for debugging...
        #mean = ROOT.RooRealVar("mean", "", 750)
        #sigma = ROOT.RooRealVar("sigma", "", 5)
        #pdf_sgn = ROOT.RooGaussian(pdf_sgn_name+"_pdf_sgn_"+sgn_name, "", self.x, mean, sigma)

        # sgn pdf
        #pdf_sgn = ROOT.RooBukinPdf(pdf_sgn_name+"_pdf_sgn_"+sgn_name, "", self.x, mean, sigma, xi, rho1, rho2)
        pdf_sgn = self.w.pdf(pdf_sgn_name+"_pdf_sgn_"+sgn_name)
        self.w.var("mean_sgn_"+sgn_name).setConstant(1)
        self.w.var("sigma_sgn_"+sgn_name).setConstant(1)
        sgn_norm = self.w.var(pdf_sgn_name+"_pdf_sgn_"+sgn_name+"_norm")
        sgn_norm_val = sgn_norm.getVal()
        sgn_norm.setVal(sgn_norm_val*sgn_xsec if sgn_xsec>0. else sgn_norm_val)
        pdf_sgn_ext = ROOT.RooExtendPdf("pdf_sgn_ext","", pdf_sgn, sgn_norm)

        # fit the alternative pdf to data (use it for toy generation)
        [pdf_bkg_alt, coeff_bkg_alt] = generate_pdf(x=self.x, pdf_name=pdf_alt_name, n_param=FTestCfg[pdf_alt_name]['MaxOrder'][mass_range], n_iter=0, mass_range=mass_range, parameter_set=parameter_set, is_data=is_data)
        res_bkg_alt = pdf_bkg_alt.fitTo(self.data, 
                                        RooFit.Strategy(1), 
                                        RooFit.Minimizer("Minuit2"), 
                                        RooFit.Minos(1), RooFit.Save(1), 
                                        RooFit.PrintLevel(-1), 
                                        RooFit.PrintEvalErrors(0), 
                                        RooFit.Warnings(ROOT.kFALSE))
        res_bkg_alt.Print()
        res_bkg_alt.correlationMatrix().Print()
        
        # normalise the background to data_obs
        bkg_norm = ROOT.RooRealVar("bkg_norm", "", self.w.data("data_obs").sumEntries())
        pdf_bkg_alt_ext = ROOT.RooExtendPdf("pdf_bkg_alt_ext","", pdf_bkg_alt, bkg_norm)

        # fit the nominal pdf to data 
        [pdf_bkg_nom, coeff_bkg_nom] = generate_pdf(x=self.x, pdf_name=pdf_fit_name, n_param=FTestCfg[pdf_fit_name]['MaxOrder'][mass_range], n_iter=1, mass_range=mass_range, parameter_set=parameter_set, is_data=is_data)
        res_bkg_nom = pdf_bkg_nom.fitTo(self.data, 
                                        RooFit.Strategy(1), 
                                        RooFit.Minimizer("Minuit2"), 
                                        RooFit.Minos(1), 
                                        RooFit.Save(1), 
                                        RooFit.PrintLevel(-1), 
                                        RooFit.PrintEvalErrors(0), 
                                        RooFit.Warnings(ROOT.kFALSE))
        res_bkg_nom.Print()
        res_bkg_nom.correlationMatrix().Print()

        # save a snapshot of the initial fits
        h_rebinned = self.data.createHistogram("h_"+data_name+"_rebinned", self.x, RooFit.Binning( int((self.x.getMax()-self.x.getMin())/5.0) , self.x.getMin(), self.x.getMax()) )
        data_rebinned = ROOT.RooDataHist(data_name+"_rebinned","", ROOT.RooArgList(self.x), h_rebinned, 1.0)
        self.plot(data=data_rebinned, hdata=h_rebinned, pdfs=[pdf_bkg_nom,pdf_bkg_alt], params=[coeff_bkg_nom,coeff_bkg_alt], res=[res_bkg_nom,res_bkg_alt], probs=[0.,0.], npars=[FTestCfg[pdf_fit_name]['MaxOrder'][mass_range],FTestCfg[pdf_alt_name]['MaxOrder'][mass_range]], legs=["Nominal: "+pdf_fit_name,"Alternative: "+pdf_alt_name], add_ratio=True, title="bias_"+pdf_fit_name+"_"+pdf_alt_name+"_"+data_name, header="Data fit (B-only)")

        # Ns and Nb (fit)
        n_s = ROOT.RooRealVar("n_s","", 0.)
        n_s.setConstant(0)
        n_b = ROOT.RooRealVar("n_b","", bkg_norm.getVal()) 
        n_b.setConstant(0)

        [pdf_bkg_fit, coeff_bkg_fit] = generate_pdf(x=self.x, pdf_name=pdf_fit_name, n_param=FTestCfg[pdf_fit_name]['MaxOrder'][mass_range], n_iter=2, mass_range=mass_range, parameter_set=parameter_set, is_data=is_data)
        coeff_bkg_fit_reset = []

        nparams[0] = FTestCfg[pdf_fit_name]['ndof'][mass_range]
        for p in xrange(FTestCfg[pdf_fit_name]['ndof'][mass_range]):
            coeff_bkg_fit_reset.append(coeff_bkg_fit[p].getVal())

        pdf_fit_ext = ROOT.RooAddPdf("pdf_fit_ext","", ROOT.RooArgList(pdf_sgn,pdf_bkg_fit),  ROOT.RooArgList(n_s,n_b))
        
        ntoy = 0

        # run on self.data for ntoys=-1
        run_ntoys = ntoys if ntoys>=0 else 1

        while ntoy<run_ntoys:

            # randomize parameters using covariance matrix
            if randomize_params:
                coeff_bkg_alt = res_bkg_alt.randomizePars()
                for p in xrange(FTestCfg[pdf_alt_name]['ndof'][mass_range]):                
                    print "\tRandomize alternative parameter ", p, " at value ", coeff_bkg_alt[p].getVal()
            
            # generate the toy data set (binned by default)
            data_toy = pdf_bkg_alt_ext.generateBinned(ROOT.RooArgSet(self.x), RooFit.Extended()) if ntoys>0 else self.data
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
            for p in xrange(FTestCfg[pdf_fit_name]['ndof'][mass_range]):                
                coeff_bkg_fit[p].setVal(coeff_bkg_fit_reset[p])
                print "\tReset parameter ", p, " at value ", coeff_bkg_fit[p].getVal()

            res_fit = pdf_fit_ext.fitTo(data_toy, 
                                        RooFit.Strategy(1), 
                                        RooFit.Minimizer("Minuit2", "migrad"), 
                                        RooFit.Minos(1), 
                                        RooFit.Save(1), 
                                        RooFit.PrintLevel(-1), 
                                        RooFit.PrintEvalErrors(0), 
                                        RooFit.Warnings(ROOT.kFALSE), 
                                        RooFit.Extended(ROOT.kTRUE))
            if res_fit==None or res_fit.status()>0:
                continue                

            res_fit.Print()
            print "Nb=%.0f -- Ns=%.0f ==> tot:  %.0f" % (nb_toy, ns_toy, n_toy)
            print "Toy ", ntoy, ">>>>>>>>>>", n_s.getVal()/n_s.getError()
            ns_fit[0] = n_s.getVal()
            ns_err[0] = n_s.getError()
            ns_gen[0] = ns_toy
            ns_asy[0] = sgn_norm.getVal()
            ns_exp[0] = sgn_norm_val
            nb_fit[0] = n_b.getVal()
            nb_err[0] = n_b.getError()
            nb_gen[0] = nb_toy
            nb_asy[0] = bkg_norm.getVal()
            edm[0] = res_fit.edm() 
            minll[0] = res_fit.minNll()
            for p in xrange(FTestCfg[pdf_fit_name]['ndof'][mass_range]):                
                params[p] = coeff_bkg_fit[p].getVal()
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
    #"dijet",
    "polydijet",
    #"expdijet"
    ]

cfg_fname = argv[1] if len(argv)>=2 else "Xbb_workspace_Had_MT_MinPt100_DH1p6_MassFSR_430to800"
cfg_pdf_alt_name = argv[2] if len(argv)>=3 else "polydijet"
cfg_pdf_fit_name = argv[3] if len(argv)>=4 else "polydijet"
cfg_n_bins = int(argv[4]) if len(argv)>=5 else 200
cfg_pdf_sgn_name = argv[5] if len(argv)>=6 else "buk"
cfg_sgn_name = argv[6] if len(argv)>=7 else "Spin0_M750"
cfg_sgn_xsec = float(argv[7]) if len(argv)>=8 else 0.
cfg_ntoys = int(argv[8]) if len(argv)>=9 else 0
cfg_nproc = int(argv[9]) if len(argv)>=10 else -1

bs = BiasStudy(fname=cfg_fname, 
               ws_name="Xbb_workspace", 
               read_dir="./plots/V7/", 
               save_dir="./plots/V7/", 
               save_ext=['png', 'pdf'], 
               blind_plot=True
               )

bs.doFTest(data_name="data_obs", test_pdfs=test_pdfs, parameter_set="default" )
#bs.doBiasStudy(pdf_alt_name=cfg_pdf_alt_name, pdf_fit_name=cfg_pdf_fit_name, data_name="data_obs", n_bins=cfg_n_bins, pdf_sgn_name=cfg_pdf_sgn_name, sgn_name=cfg_sgn_name, sgn_xsec=cfg_sgn_xsec, ntoys=cfg_ntoys, nproc=cfg_nproc, parameter_set="default")

print FTestCfg_data
#print(json.dumps(FTestCfg, indent = 4))

for gc in gcs:
    gc.Print()
