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
        'range' : [550., 1200.],
        },
    "Spin0_M650" : {
        'mean' : [550.,650.],
        'sigma' : [30., 100.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'range' : [550., 800.],
        },
    "Spin0_M750" : {
        'mean' : [650.,750.],
        'sigma' : [20., 100.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'range' : [550., 900.],
        },
    "Spin0_M850" : {
        'mean' : [750.,900.],
        'sigma' : [20., 200.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'range' : [550., 1100.],
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

    def imp(self, obj):
        getattr(self.w,"import")(obj, ROOT.RooCmdArg())

    def save(self, data=None, pdfs=[], legs=[], ran=ROOT.RooCmdArg(), n_par=1, title=""):

        c1 = ROOT.TCanvas("c1_"+title,"c1",600,600)

        leg = ROOT.TLegend(0.40,0.65,0.80,0.88, "","brNDC")
        leg.SetHeader( "Range: [%.0f,%.0f]" % (self.x.getMin(), self.x.getMax()) )  
        leg.SetFillStyle(0)
        leg.SetBorderSize(0)
        leg.SetTextSize(0.03)
        leg.SetFillColor(10)
        
        frame = self.x.frame(ran)
        frame.SetName("frame")
        frame.SetTitle(title)
        data.plotOn(frame, RooFit.Name("data"))
        offset = 2 if len(pdfs)==1 else 0
        for p,pdf in enumerate(pdfs):
            pdf.plotOn(frame, RooFit.LineColor(offset+p), RooFit.LineStyle(ROOT.kSolid if p%2 else ROOT.kDashed), RooFit.Name(pdf.GetName()))

        c1.cd()  
        frame.Draw()
        for p,pdf in enumerate(pdfs):
            chi2 = frame.chiSquare(pdf.GetName(), "data", n_par )
            leg.AddEntry(frame.getCurve(pdf.GetName()), legs[p]+", #chi^{2}/ndof=%.2f" % chi2, "L")
        leg.Draw()
        
        c1.SaveAs(self.saveDir+"/"+title+".png")

    def add_category(self, cat_btag="Had_MT", cat_kin="MinPt150_DH1p6"):
        self.cat_btag = cat_btag
        self.cat_kin = cat_kin

    def create_mass(self, name="MassFSR", xmin=550., xmax=1200.):        
        self.x = ROOT.RooRealVar("x", "", xmin, xmax)
        self.x_name = name
        self.x.setRange(name, xmin, xmax)
        self.imp(self.x)
    
    def add_syst_to_ws(self, sgn_name="Spin0_M750", rebin_factor=1.0):

        shifts = {}
        for syst in ["JECUp", "JECDown", "JERUp", "JERDown"]:
            hname = "signal_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+syst+"_"+sgn_name
            h = self.file.Get(hname)
            if rebin_factor>1. :
                h.Rebin(rebin_factor)
            norm = h.Integral()

            data_sgn = ROOT.RooDataHist("data_sgn_"+syst+"_"+sgn_name, "", ROOT.RooArgList(self.x), h, 1.0)
            hist_pdf_sgn = ROOT.RooHistPdf("hist_pdf_sgn_"+syst+"_"+sgn_name,"", ROOT.RooArgSet(self.x), data_sgn, 0)        
            mean = ROOT.RooRealVar("mean_sgn_"+syst+"_"+sgn_name, "", FitParam[sgn_name]['mean'][0], FitParam[sgn_name]['mean'][1])
            sigma = ROOT.RooRealVar("sigma_sgn_"+syst+"_"+sgn_name, "", FitParam[sgn_name]['sigma'][0], FitParam[sgn_name]['sigma'][1])
            mean.setVal( self.w.var("mean_sgn_"+sgn_name).getVal() )
            sigma.setVal( self.w.var("sigma_sgn_"+sgn_name).getVal() )
            if "JEC" in syst:
                sigma.setConstant()
            if "JER" in syst:
                mean.setConstant()
            xi = ROOT.RooRealVar("xi_sgn_"+syst+"_"+sgn_name, "", self.w.var("xi_sgn_"+sgn_name).getVal())
            rho1 = ROOT.RooRealVar("rho1_sgn_"+syst+"_"+sgn_name, "", self.w.var("rho1_sgn_"+sgn_name).getVal())
            rho2 = ROOT.RooRealVar("rho2_sgn_"+syst+"_"+sgn_name, "", self.w.var("rho2_sgn_"+sgn_name).getVal())
            xi.setConstant()
            rho1.setConstant()
            rho2.setConstant()

            buk_pdf_sgn = ROOT.RooBukinPdf("buk_pdf_sgn_"+syst+"_"+sgn_name,"", self.x, mean, sigma, xi, rho1, rho2)
            buk_pdf_sgn.fitTo(data_sgn, RooFit.Strategy(2), RooFit.Minos(1), RooFit.Range(sgn_name), RooFit.SumCoefRange(sgn_name))
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
        self.save( self.w.data("data_sgn_"+sgn_name), pdfs, legs, RooFit.Range(sgn_name), 5, 
                   self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+sgn_name+"JEC_JER")


    def add_sgn_to_ws(self, sgn_name="Spin0_M750", rebin_factor=1.0, set_param_const=True):

        hname = "signal_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+sgn_name
        print hname
        h = self.file.Get(hname)
        if rebin_factor>1. :
            h.Rebin(rebin_factor)

        norm = h.Integral()

        data_sgn = ROOT.RooDataHist("data_sgn_"+sgn_name, "", ROOT.RooArgList(self.x), h, 1.0)
        self.imp(data_sgn)

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

        self.x.setRange(sgn_name, FitParam[sgn_name]['range'][0], FitParam[sgn_name]['range'][1])
        buk_pdf_sgn.fitTo(data_sgn, RooFit.Strategy(2), RooFit.Minos(1), RooFit.Range(sgn_name), RooFit.SumCoefRange(sgn_name))

        self.save( data_sgn, [buk_pdf_sgn], ["Bukin"], RooFit.Range(sgn_name) , 5, 
                   self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+sgn_name)

        if set_param_const:
            mean.setConstant()
            sigma.setConstant()
            xi.setConstant()
            rho1.setConstant()
            rho2.setConstant()

        self.imp(buk_pdf_sgn)
        self.imp(buk_pdf_sgn_norm)


    def add_bkg_to_ws(self, pdf_name="dijet", rebin_factor=1.0, set_param_const=False):

        hname = "background_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name
        print hname
        h = self.file.Get(hname)
        if rebin_factor>1. :
            h.Rebin(rebin_factor)

        norm = h.Integral()

        data_bkg = ROOT.RooDataHist("data_bkg", "", ROOT.RooArgList(self.x), h, 1.0)
        self.imp(data_bkg)

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

        self.x.setRange(pdf_name, FitParam[pdf_name]['range'][0], FitParam[pdf_name]['range'][1])
        pdf_bkg.fitTo(data_bkg, RooFit.Strategy(2), RooFit.Minos(1), RooFit.Range(pdf_name), RooFit.SumCoefRange(pdf_name))

        self.save( data_bkg, [pdf_bkg], [pdf_name], RooFit.Range(pdf_name) , 2, 
                   self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_background")

        if set_param_const:
            p0.setConstant()
            p1.setConstant()
            p2.setConstant()

        self.imp(pdf_bkg)
        self.imp(pdf_bkg_norm)

    def add_data_to_ws(self, rebin_factor=1.0):

        hname = "data_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name
        print hname
        h = self.file.Get(hname)
        if rebin_factor>1. :
            h.Rebin(rebin_factor)
        data_obs = ROOT.RooDataHist("data_obs", "", ROOT.RooArgList(self.x), h, 1.0)
        self.imp(data_obs)

    def create_workspace(self, signals=[]):                            

        for sgn in signals:
            self.add_sgn_to_ws(sgn_name=sgn, rebin_factor=400, set_param_const=True)
            self.add_syst_to_ws(sgn_name=sgn, rebin_factor=400)
        
        self.add_bkg_to_ws(pdf_name="dijet", rebin_factor=400, set_param_const=False)
        self.add_data_to_ws(rebin_factor=-1)

        self.w.Print()
        savename = self.saveDir+self.ws_name+"_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+("%.0f" % self.x.getMin())+"to"+("%.0f" % self.x.getMax())
        self.w.writeToFile(savename+".root")

        self.file.Close()

###########################

xbbfact = XbbFactory(fname="plot.root", ws_name="Xbb_workspace", version="V3", saveDir="/scratch/bianchi/")
xbbfact.add_category(cat_btag="Had_LT", cat_kin="MinPt150_DH1p6")
xbbfact.create_mass(name="MassFSR", xmin=550., xmax=1200.)
xbbfact.create_workspace( ["Spin0_M650"] )

