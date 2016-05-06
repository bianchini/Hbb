from sys import argv
argv.append( '-b-' )

import ROOT
from ROOT import RooFit
ROOT.gROOT.SetBatch(True)
argv.remove( '-b-' )

import math
import sys
sys.path.append('./')


FitParam = {
    "dijet" : {
        'p0' : [0.,10.],
        'p1' : [0., 50.],
        'p2' : [-5., 5.],
        'fit_range' : [550., 1200.],
        },
    "Spin0_M650" : {
        'mean' : [550.,650.],
        'sigma' : [30., 100.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [500., 800.],
        },
    "Spin0_M750" : {
        'mean' : [650.,750.],
        'sigma' : [20., 100.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [500., 900.],
        },
    "Spin0_M850" : {
        'mean' : [750.,900.],
        'sigma' : [20., 200.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [550., 1100.],
        },
    "Spin0_M1000" : {
        'mean' : [800.,1100.],
        'sigma' : [50., 400.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [600., 1200.],
        },
    "Spin0_M1200" : {
        'mean' : [900.,1300.],
        'sigma' : [50., 400.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [700., 1400.],
        }
}



class XbbFactory:

    def __init__(self, fname="plot.root", ws_name="Xbb_workspace", version="V3", saveDir="/scratch/bianchi/"):
        self.file = ROOT.TFile.Open("plots/"+version+"/"+fname, "READ")
        if self.file==None or self.file.IsZombie():
            return
        self.ws_name = ws_name
        self.version = version
        self.saveDir = saveDir
        self.w = ROOT.RooWorkspace( ws_name, "workspace") ; 
        self.bin_size = 1.

    # import into workspace
    def imp(self, obj):
        getattr(self.w,"import")(obj, ROOT.RooCmdArg())

    # define the category 
    def add_category(self, cat_btag="Had_MT", cat_kin="MinPt150_DH1p6"):
        self.cat_btag = cat_btag
        self.cat_kin = cat_kin

    # create and import the fitting variable
    def create_mass(self, name="MassFSR", xmin=550., xmax=1200.):        
        self.x = ROOT.RooRealVar("x", "", 400., 2000.)
        self.x_name = name
        self.x.setRange(name, xmin, xmax)
        for k in FitParam.keys():
            self.x.setRange(k, FitParam[k]['fit_range'][0], FitParam[k]['fit_range'][1])
        self.imp(self.x)
    
    # save plots to png
    def plot(self, data=None, pdfs=[], res=None, add_pulls=False, legs=[], ran="", n_par=1, title=""):

        #return
        c1 = ROOT.TCanvas("c1_"+title,"c1",600,600)
        if add_pulls:
            c1.Divide(2)

        leg = ROOT.TLegend(0.40,0.65,0.70,0.88, "","brNDC")
        leg.SetHeader( "[%.0f,%.0f]" % (self.x.getMin(), self.x.getMax()) )  
        leg.SetFillStyle(0)
        leg.SetBorderSize(0)
        leg.SetTextSize(0.03)
        leg.SetFillColor(10)    

        self.x.setRange( FitParam[ran]['fit_range'][0], FitParam[ran]['fit_range'][1] )
        frame = self.x.frame(RooFit.Range(ran))
        frame.SetName("frame")
        frame.SetTitle(title)
        data.plotOn(frame, RooFit.Name("data"))
        for p,pdf in enumerate(pdfs):
            opt_color = RooFit.LineColor(ROOT.kRed) if len(pdfs)==1 else RooFit.LineColor(1+p) 
            if res!=None:
                pdf.plotOn(frame, RooFit.VisualizeError(res, 1, ROOT.kFALSE), opt_color, RooFit.LineStyle(ROOT.kSolid if p%2 or len(pdfs)==1 else ROOT.kDashed), RooFit.Name(pdf.GetName()))
                data.plotOn(frame, RooFit.Name("data"))
            else:
                pdf.plotOn(frame, opt_color, RooFit.LineStyle(ROOT.kSolid if p%2 or len(pdfs)==1 else ROOT.kDashed), RooFit.Name(pdf.GetName()))

        c1.cd(1)  
        frame.Draw()
        for p,pdf in enumerate(pdfs):
            chi2 = frame.chiSquare(pdf.GetName(), "data", n_par )
            leg.AddEntry(frame.getCurve(pdf.GetName()), legs[p]+", #chi^{2}=%.2f" % chi2, "L")
        leg.Draw()

        if add_pulls:
            c1.cd(2)
            frame2 = self.x.frame(RooFit.Range(ran))
            frame2.SetName("frame2")
            frame2.SetTitle(title)        
            hresid = frame.residHist()
            frame2.addPlotable(hresid,"P")
            frame2.Draw()

        c1.SaveAs(self.saveDir+"/"+title+".png")
        return

    # add a signal sample to the ws
    def add_sgn_to_ws(self, sgn_name="Spin0_M750", rebin_factor=1.0, set_param_const=True):

        hname = "signal_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+sgn_name
        print hname
        h = self.file.Get(hname)
        if rebin_factor>1. :
            h.Rebin(rebin_factor)

        self.x.setRange( FitParam[sgn_name]['fit_range'][0], FitParam[sgn_name]['fit_range'][1] )
        data_sgn = ROOT.RooDataHist("data_sgn_"+sgn_name, "", ROOT.RooArgList(self.x), h, 1.0)
        self.imp(data_sgn)

        norm = data_sgn.sumEntries()

        hist_pdf_sgn = ROOT.RooHistPdf("hist_pdf_sgn_"+sgn_name,"", ROOT.RooArgSet(self.x), data_sgn, 0)        
        hist_pdf_sgn_norm = ROOT.RooRealVar("hist_pdf_sgn_"+sgn_name+"_norm", "signal normalisation", norm )
        self.imp(hist_pdf_sgn)
        self.imp(hist_pdf_sgn_norm)

        mean = ROOT.RooRealVar("mean_sgn_"+sgn_name, "", FitParam[sgn_name]['mean'][0], FitParam[sgn_name]['mean'][1])
        sigma = ROOT.RooRealVar("sigma_sgn_"+sgn_name, "", FitParam[sgn_name]['sigma'][0], FitParam[sgn_name]['sigma'][1])
        xi = ROOT.RooRealVar("xi_sgn_"+sgn_name, "", FitParam[sgn_name]['xi'][0], FitParam[sgn_name]['xi'][1])
        rho1 = ROOT.RooRealVar("rho1_sgn_"+sgn_name, "", FitParam[sgn_name]['rho1'][0], FitParam[sgn_name]['rho1'][1])
        rho2 = ROOT.RooRealVar("rho2_sgn_"+sgn_name, "", FitParam[sgn_name]['rho2'][0], FitParam[sgn_name]['rho2'][1])
    
        buk_pdf_sgn = ROOT.RooBukinPdf("buk_pdf_sgn_"+sgn_name,"", self.x, mean, sigma, xi, rho1, rho2)
        buk_pdf_sgn_norm = ROOT.RooRealVar("buk_pdf_sgn_"+sgn_name+"_norm","", norm)

        res = buk_pdf_sgn.fitTo(data_sgn, RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Minos(1), RooFit.Range(sgn_name), RooFit.SumCoefRange(sgn_name), RooFit.Save(1))

        self.plot( data_sgn, [buk_pdf_sgn], res, False, ["Bukin"], sgn_name, 5, self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+sgn_name)

        if set_param_const:
            mean.setConstant()
            sigma.setConstant()
            xi.setConstant()
            rho1.setConstant()
            rho2.setConstant()

        self.imp(buk_pdf_sgn)
        self.imp(buk_pdf_sgn_norm)

    # add signal systematics to ws
    def add_syst_to_ws(self, sgn_name="Spin0_M750", rebin_factor=1.0):

        shifts = {}
        for syst in ["JECUp", "JECDown", "JERUp", "JERDown"]:
            hname = "signal_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+syst+"_"+sgn_name
            h = self.file.Get(hname)
            if rebin_factor>1. :
                h.Rebin(rebin_factor)

            self.x.setRange( FitParam[sgn_name]['fit_range'][0], FitParam[sgn_name]['fit_range'][1] )
            data_sgn = ROOT.RooDataHist("data_sgn_"+syst+"_"+sgn_name, "", ROOT.RooArgList(self.x), h, 1.0)
            norm = data_sgn.sumEntries()

            hist_pdf_sgn = ROOT.RooHistPdf("hist_pdf_sgn_"+syst+"_"+sgn_name,"", ROOT.RooArgSet(self.x), data_sgn, 0)        
            mean = ROOT.RooRealVar("mean_sgn_"+syst+"_"+sgn_name, "", FitParam[sgn_name]['mean'][0], FitParam[sgn_name]['mean'][1])
            sigma = ROOT.RooRealVar("sigma_sgn_"+syst+"_"+sgn_name, "", FitParam[sgn_name]['sigma'][0], FitParam[sgn_name]['sigma'][1])
            mean.setVal( self.w.var("mean_sgn_"+sgn_name).getVal() )
            sigma.setVal( self.w.var("sigma_sgn_"+sgn_name).getVal() )
            xi = ROOT.RooRealVar("xi_sgn_"+syst+"_"+sgn_name, "", self.w.var("xi_sgn_"+sgn_name).getVal())
            rho1 = ROOT.RooRealVar("rho1_sgn_"+syst+"_"+sgn_name, "", self.w.var("rho1_sgn_"+sgn_name).getVal())
            rho2 = ROOT.RooRealVar("rho2_sgn_"+syst+"_"+sgn_name, "", self.w.var("rho2_sgn_"+sgn_name).getVal())
            if "JEC" in syst:
                mean.setConstant(0)
                sigma.setConstant(1)
            if "JER" in syst:
                mean.setConstant(1)
                sigma.setConstant(0)
            xi.setConstant()
            rho1.setConstant()
            rho2.setConstant()

            buk_pdf_sgn = ROOT.RooBukinPdf("buk_pdf_sgn_"+syst+"_"+sgn_name,"", self.x, mean, sigma, xi, rho1, rho2)
            buk_pdf_sgn.fitTo(data_sgn, RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Minos(1), RooFit.Range(sgn_name), RooFit.SumCoefRange(sgn_name))
            shifts[syst] = [mean.getVal(), sigma.getVal(), norm]
            self.imp( buk_pdf_sgn )

        for syst in ["CSVSFUp", "CSVSFDown"]:
            hname = "signal_"+self.cat_btag+"_"+syst+"_"+self.cat_kin+"_"+self.x_name+"_"+sgn_name
            h = self.file.Get(hname)
            norm = self.w.var("buk_pdf_sgn_"+sgn_name+"_norm").getVal()
            if h!=None:
                norm = h.Integral()
            shifts[syst] = [norm]

        csv = max( abs(shifts["CSVSFUp"][0]-self.w.var("buk_pdf_sgn_"+sgn_name+"_norm").getVal()), 
                   abs(shifts["CSVSFDown"][0]-self.w.var("buk_pdf_sgn_"+sgn_name+"_norm").getVal()))
        jec = max( abs(shifts["JECUp"][0]-self.w.var("mean_sgn_"+sgn_name).getVal()), 
                   abs(shifts["JECDown"][0]-self.w.var("mean_sgn_"+sgn_name).getVal()))
        jer = max( abs(shifts["JERUp"][1]-self.w.var("sigma_sgn_"+sgn_name).getVal()), 
                   abs(shifts["JERDown"][1]-self.w.var("sigma_sgn_"+sgn_name).getVal()) ) 
        csv_shift = ROOT.RooRealVar("CSV_shift_"+sgn_name, "", csv )
        mean_shift = ROOT.RooRealVar("mean_shift_"+sgn_name, "", jec )
        sigma_shift = ROOT.RooRealVar("sigma_shift_"+sgn_name, "", jer )
        self.imp(csv_shift)
        self.imp(mean_shift)
        self.imp(sigma_shift)

        self.w.var("mean_sgn_"+sgn_name).setConstant(0)
        self.w.var("sigma_sgn_"+sgn_name).setConstant(0)

        pdfs = [ self.w.pdf("buk_pdf_sgn"+syst+"_"+sgn_name) for syst in ["","_JECUp", "_JECDown", "_JERUp", "_JERDown"]]
        legs = ["Nominal", "JEC up", "JEC down", "JER up", "JER down"]

        self.plot( self.w.data("data_sgn_"+sgn_name), pdfs, None, False, legs, sgn_name, 5, self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+sgn_name+"_JEC-JER")

    # add background pdf to ws
    def add_bkg_to_ws(self, pdf_name="dijet", rebin_factor=1.0, set_param_const=False):

        hname = "data_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name
        print hname
        h = self.file.Get(hname)
        if rebin_factor>1. :
            h.Rebin(rebin_factor)

        self.x.setRange( FitParam[pdf_name]['fit_range'][0], FitParam[pdf_name]['fit_range'][1] )
        data_bkg = ROOT.RooDataHist("data_bkg", "", ROOT.RooArgList(self.x), h, 1.0)
        self.imp(data_bkg)

        norm = data_bkg.sumEntries()

        hist_pdf_bkg = ROOT.RooHistPdf("hist_pdf_bkg","", ROOT.RooArgSet(self.x), data_bkg, 0)        
        hist_pdf_bkg_norm = ROOT.RooRealVar("hist_pdf_bkg_norm", "", norm )
        self.imp(hist_pdf_bkg)
        self.imp(hist_pdf_bkg_norm)

        sqrts = 1.3e+04
        formula = ("TMath::Max(1e-50,TMath::Power(1-@0/%E,@1)/(TMath::Power(@0/%E,@2+@3*TMath::Log(@0/%E))))" % (sqrts,sqrts,sqrts))
        
        p0 = ROOT.RooRealVar("p0_bkg_"+pdf_name, "", FitParam[pdf_name]['p0'][0], FitParam[pdf_name]['p0'][1])
        p0.setVal(0.)
        p0.setConstant()
        p1 = ROOT.RooRealVar("p1_bkg_"+pdf_name, "", FitParam[pdf_name]['p1'][0], FitParam[pdf_name]['p1'][1])
        p2 = ROOT.RooRealVar("p2_bkg_"+pdf_name, "", FitParam[pdf_name]['p2'][0], FitParam[pdf_name]['p2'][1])
    
        pdf_bkg = ROOT.RooGenericPdf(pdf_name+"_pdf_bkg", formula, ROOT.RooArgList(self.x,p0,p1,p2))
        pdf_bkg_norm = ROOT.RooRealVar(pdf_name+"_pdf_bkg_norm","", norm)

        res = pdf_bkg.fitTo(data_bkg, RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Minos(1), RooFit.Range(pdf_name), RooFit.SumCoefRange(pdf_name), RooFit.Save(1))

        self.plot( data_bkg, [pdf_bkg], None, False, [pdf_name], pdf_name, 2, self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_background")

        if set_param_const:
            p0.setConstant()
            p1.setConstant()
            p2.setConstant()

        self.imp(pdf_bkg)
        self.imp(pdf_bkg_norm)

    # add data_obs to ws
    def add_data_to_ws(self, rebin_factor=1.0):

        hname = "data_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name
        print hname
        h = self.file.Get(hname)
        if rebin_factor>1. :
            h.Rebin(rebin_factor)            

        # set default range to Range(self.x_name)
        self.w.var("x").setRange(self.x.getMin(self.x_name), self.x.getMax(self.x_name))

        self.x.setRange(self.x.getMin(self.x_name), self.x.getMax(self.x_name))
        data_obs = ROOT.RooDataHist("data_obs", "", ROOT.RooArgList(self.x), h, 1.0)
        self.imp(data_obs)
        self.bin_size = data_obs.binVolume(ROOT.RooArgSet(self.x))

    def get_save_name(self):        
        return  self.saveDir+self.ws_name+"_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+("%.0f" % (self.x.getMin(self.x_name)-self.bin_size*0.5))+"to"+("%.0f" % (self.x.getMax(self.x_name)+self.bin_size*0.5))

    # create the ws
    def create_workspace(self, signals=[]):                            

        for sgn in signals:
            self.add_sgn_to_ws(sgn_name=sgn, rebin_factor=400, set_param_const=True)
            self.add_syst_to_ws(sgn_name=sgn, rebin_factor=400)
        
        self.add_bkg_to_ws(pdf_name="dijet", rebin_factor=500, set_param_const=False)
        self.add_data_to_ws(rebin_factor=-1)

        self.w.Print()
        self.w.writeToFile(self.get_save_name()+".root")

        self.file.Close()

###########################

xbbfact = XbbFactory(fname="plot.root", ws_name="Xbb_workspace", version="V3", saveDir="/scratch/bianchi/")
xbbfact.add_category(cat_btag="Had_LT", cat_kin="MinPt150_DH1p6")
xbbfact.create_mass(name="MassFSR", xmin=550., xmax=1200.)
#xbbfact.create_workspace( ["Spin0_M650", "Spin0_M750", "Spin0_M850","Spin0_M1000","Spin0_M1200" ] )
xbbfact.create_workspace( ["Spin0_M650"] )

