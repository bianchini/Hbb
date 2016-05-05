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

    def save(self, data=None, pdf=None, ran=ROOT.RooCmdArg(), n_par=1, title=""):

        c1 = ROOT.TCanvas("c1_"+title,"c1",600,600)

        leg = ROOT.TLegend(0.45,0.65,0.80,0.88, "","brNDC")
        leg.SetFillStyle(0)
        leg.SetBorderSize(0)
        leg.SetTextSize(0.05)
        leg.SetFillColor(10)
        
        frame = self.x.frame(ran)
        frame.SetName("x frame")
        frame.SetTitle(title)
        data.plotOn(frame, RooFit.Name("data"))
        pdf.plotOn(frame, RooFit.LineColor(ROOT.kRed), RooFit.Name(pdf.GetName()))

        c1.cd()  
        frame.Draw()
        chi2 = frame.chiSquare(pdf.GetName(), "data", n_par )
        leg.SetHeader( "Range: [%.0f,%.0f] GeV" % (self.x.getMin(), self.x.getMax()) )  
        leg.AddEntry(frame.getCurve(pdf.GetName()), "#chi^{2}/ndof=%.2f" % chi2, "L")
        leg.Draw()
        
        c1.SaveAs(self.saveDir+"/"+pdf.GetName()+"_"+data.GetName()+".png")

    def add_category(self, cat_btag="Had_MT", cat_kin="MinPt150_DH1p6"):
        self.cat_btag = cat_btag
        self.cat_kin = cat_kin

    def create_mass(self, name="MassFSR", xmin=550., xmax=1200.):        
        self.x = ROOT.RooRealVar("x", "", xmin, xmax)
        self.x_name = name
        self.x.setRange(name, xmin, xmax)
        self.imp(self.x)
    
    def add_sgn_to_ws(self, sgn_name="Spin0_M750", rebin_factor = 1.0, set_param_const = True, title=""):

        hname = "signal_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+sgn_name
        print hname
        h = self.file.Get(hname)
        if rebin_factor>1. :
            h.Rebin(rebin_factor)

        data_sgn = ROOT.RooDataHist("data_sgn_"+sgn_name, "data signal", ROOT.RooArgList(self.x), h, 1.0)
        self.imp(data_sgn)

        hist_pdf_sgn = ROOT.RooHistPdf("hist_pdf_sgn_"+sgn_name,"", ROOT.RooArgSet(self.x), data_sgn, 0)

        norm = self.x.createIntegral(ROOT.RooArgSet(self.x), ROOT.RooArgSet(self.x), self.x_name).getVal()        
        hist_pdf_sgn_norm = ROOT.RooRealVar("hist_pdf_sgn_"+sgn_name+"_norm", "signal normalisation", norm )
        self.imp(hist_pdf_sgn)
        self.imp(hist_pdf_sgn_norm)

        mean = ROOT.RooRealVar("mean_sgn_"+sgn_name, "", FitParam[sgn_name]['mean'][0], FitParam[sgn_name]['mean'][1])
        sigma = ROOT.RooRealVar("sigma_sgn_"+sgn_name, "", FitParam[sgn_name]['sigma'][0], FitParam[sgn_name]['sigma'][1])
        xi = ROOT.RooRealVar("xi_sgn_"+sgn_name, "", FitParam[sgn_name]['xi'][0], FitParam[sgn_name]['xi'][1])
        rho1 = ROOT.RooRealVar("rho1_sgn_"+sgn_name, "", FitParam[sgn_name]['rho1'][0], FitParam[sgn_name]['rho1'][1])
        rho2 = ROOT.RooRealVar("rho2_sgn_"+sgn_name, "", FitParam[sgn_name]['rho2'][0], FitParam[sgn_name]['rho2'][1])
    
        buk_pdf_sgn = ROOT.RooBukinPdf("buk_pdf_sgn_"+sgn_name,"", self.x, mean, sigma, xi, rho1, rho2)
        buk_pdf_sgn_norm = ROOT.RooRealVar("buk_pdf_sgn_"+sgn_name+"_norm","", data_sgn.sumEntries())

        self.x.setRange(sgn_name, FitParam[sgn_name]['range'][0], FitParam[sgn_name]['range'][1])
        buk_pdf_sgn.fitTo(data_sgn, RooFit.Strategy(2), RooFit.Minos(1), RooFit.Range(sgn_name), RooFit.SumCoefRange(sgn_name))

        self.save( data_sgn, buk_pdf_sgn, RooFit.Range(sgn_name) , 5, "")

        if set_param_const:
            mean.setConstant()
            sigma.setConstant()
            xi.setConstant()
            rho1.setConstant()
            rho2.setConstant()

        self.imp(buk_pdf_sgn)
        self.imp(buk_pdf_sgn_norm)


    def create_workspace(self, signals=[]):                            

        for sgn in signals:
            self.add_sgn_to_ws(sgn_name=sgn, rebin_factor=400, set_param_const=True, title="")
        
        self.w.Print()
        #savename = "./plots/"+self.version+"/"+self.ws_name+"_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+str(self.x.getMin())+"to"+str(self.x.getMax())
        savename = self.saveDir+self.ws_name+"_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+("%.0f" % self.x.getMin())+"to"+("%.0f" % self.x.getMax())
        self.w.writeToFile(savename+".root")

        self.file.Close()

###########################

xbbfact = XbbFactory(fname="plot.root", ws_name="Xbb_workspace", version="V3", saveDir="/scratch/bianchi/")
xbbfact.add_category(cat_btag="Had_LT", cat_kin="MinPt150_DH1p6")
xbbfact.create_mass(name="MassFSR", xmin=550., xmax=1200.)
xbbfact.create_workspace( ["Spin0_M650", "Spin0_M750","Spin0_M850"] )

