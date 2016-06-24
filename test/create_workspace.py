from sys import argv
argv.append( '-b-' )

import ROOT
from ROOT import RooFit
ROOT.gROOT.SetBatch(True)
argv.remove( '-b-' )

import math
import sys
sys.path.append('./')
sys.path.append('../python/')

from utilities import *
from parameters_cfi import *

# for memory issues
gcs = []

class XbbFactory:

    def __init__(self, fname="plot.root", ws_name="Xbb_workspace", read_dir="/scratch/bianchi/", save_dir="/scratch/bianchi/", save_ext=['png'], blind_plot=False):
        self.file = ROOT.TFile.Open(read_dir+"/"+fname, "READ")
        if self.file==None or self.file.IsZombie():
            return
        self.ws_name = ws_name
        self.save_dir = save_dir+'/'
        self.save_ext = save_ext
        self.w = ROOT.RooWorkspace( ws_name, "workspace")
        self.bin_size = 1.
        self.plot_blind = blind_plot

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
        for k in FitSgnCfg.keys():
            self.x.setRange(k, FitSgnCfg[k]['fit_range'][0], FitSgnCfg[k]['fit_range'][1])
        self.imp(self.x)
    
    # save plots to .png
    def plot(self, data=None, pdfs=[], res=None, add_pulls=False, legs=[], ran="", n_par=1, title="", header=""):

        #return
        c1 = ROOT.TCanvas("c1_"+self.get_save_name()+"_"+title,"c1",600,600)
        #if add_pulls:
        pad1 = ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
        pad1.SetBottomMargin(0) 
        #pad1.SetGridx()  
        pad1.Draw()      
        pad1.cd()    

        leg = ROOT.TLegend(0.12,0.55,0.45,0.88, "","brNDC")
        leg.SetHeader(header)  
        leg.SetFillStyle(0)
        leg.SetBorderSize(0)
        leg.SetTextSize(0.06)
        leg.SetFillColor(10)    

        frame = self.x.frame()
        frame.SetName("frame")
        frame.SetTitle("CMS Preliminary 2016 #sqrt{s}=13 TeV")
        frame.GetYaxis().SetTitleSize(20)
        frame.GetYaxis().SetTitleFont(43)
        frame.GetYaxis().SetTitleOffset(1.35)
        frame.GetYaxis().SetLabelFont(43) 
        frame.GetYaxis().SetLabelSize(15)
        frame.GetXaxis().SetTitleSize(20)
        frame.GetXaxis().SetTitleFont(43)
        frame.GetXaxis().SetLabelFont(43) 
        frame.GetXaxis().SetLabelSize(15)            

        if data!=None:
            data.plotOn(frame, RooFit.Name("data"))
            frame.GetYaxis().SetTitle("Events / "+str(data.binVolume())+" GeV")
        else:
            frame.GetYaxis().SetTitle("1/GeV")
            frame.GetXaxis().SetTitle("mass (GeV)")

        for p,pdf in enumerate(pdfs):
            opt_color = RooFit.LineColor(ROOT.kRed)
            opt_style = RooFit.LineStyle(ROOT.kSolid)
            if len(pdfs)>1:
                if p==0:
                    opt_color = RooFit.LineColor(1)
                    opt_style = RooFit.LineStyle(ROOT.kSolid)
                else:
                    opt_color = RooFit.LineColor(2+p/3)
                    if p%2==0:
                        opt_style = RooFit.LineStyle(ROOT.kDashed)

            if res!=None and res.status()==0:
                pdf.plotOn(frame, 
                           RooFit.VisualizeError(res, 1, ROOT.kFALSE), 
                           RooFit.LineColor(ROOT.kGreen), 
                           RooFit.LineStyle(ROOT.kSolid), 
                           RooFit.FillColor(ROOT.kGreen) )
                pdf.plotOn(frame, RooFit.LineColor(ROOT.kRed), RooFit.LineStyle(ROOT.kSolid), RooFit.Name(pdf.GetName()))
                if data!=None:
                    data.plotOn(frame, RooFit.Name("data"))
            else:
                pdf.plotOn(frame, opt_color, opt_style, RooFit.Name(pdf.GetName()))

        if add_pulls:
            pad1.cd()

        frame.Draw()
        for p,pdf in enumerate(pdfs):
            chi2 = frame.chiSquare(pdf.GetName(), "data", n_par )
            leg.AddEntry(frame.getCurve(pdf.GetName()), legs[p]+ (("{#chi^{2}=%.2f}" % chi2) if len(pdfs)==1 else ""), "L")
        leg.Draw()

        if add_pulls:
            c1.cd()
            pad2 = ROOT.TPad("pad2", "pad2", 0, 0.05, 1, 0.3)
            pad2.SetTopMargin(0)
            pad2.SetBottomMargin(0.2)
            #pad2.SetGridx()   
            pad2.SetGridy() 
            pad2.Draw()
            pad2.cd()       
            frame2 = self.x.frame()
            frame2.SetName("frame2")
            hresid = frame.pullHist()
            hresid.GetYaxis().SetRangeUser(-4,4)
            frame2.SetTitle("") 
            frame2.GetYaxis().SetTitle("Pulls")
            frame2.GetYaxis().SetNdivisions(505)
            frame2.GetYaxis().SetTitleSize(20)
            frame2.GetYaxis().SetTitleFont(43)
            frame2.GetYaxis().SetTitleOffset(1.35)
            frame2.GetYaxis().SetLabelFont(43) 
            frame2.GetYaxis().SetLabelSize(15)
            frame2.GetXaxis().SetTitle("mass (GeV)")
            frame2.GetXaxis().SetTitleSize(20)
            frame2.GetXaxis().SetTitleFont(43)
            frame2.GetXaxis().SetTitleOffset(3.0)
            frame2.GetXaxis().SetLabelFont(43) 
            frame2.GetXaxis().SetLabelSize(15)            
            frame2.addPlotable(hresid,"P")
            frame2.Draw()
            frame2.GetYaxis().SetRangeUser(-4,4)

        for ext in self.save_ext:
            c1.SaveAs(self.save_dir+self.ws_name+"_"+self.get_save_name()+"_"+title+"."+ext)

        # clean up memory
        c1.IsA().Destructor( c1 )
        leg.IsA().Destructor( leg )
        return

    # add a signal sample to the ws
    def add_sgn_to_ws(self, sgn_name="Spin0_M750", rebin_factor=1.0, set_param_const=True, spin_symmetric=False):

        hname = "signal_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+sgn_name
        print hname
        h = self.file.Get(self.cat_btag+"_"+self.cat_kin+"/"+hname).Clone(hname+"_clone")
        if rebin_factor>1. :
            h.Rebin(rebin_factor)
        ROOT.SetOwnership(h, False ) 

        self.x.setRange(self.x.getMin(self.x_name), self.x.getMax(self.x_name))
        data_sgn = ROOT.RooDataHist("data_sgn_"+sgn_name, "", ROOT.RooArgList(self.x), h, 1.0)
        self.imp(data_sgn)

        norm = data_sgn.sumEntries()

        hist_pdf_sgn = ROOT.RooHistPdf("hist_pdf_sgn_"+sgn_name,"", ROOT.RooArgSet(self.x), data_sgn, 0)        
        hist_pdf_sgn_norm = ROOT.RooRealVar("hist_pdf_sgn_"+sgn_name+"_norm", "signal normalisation", norm )
        hist_pdf_sgn_norm.setConstant(1)
        self.imp(hist_pdf_sgn)
        self.imp(hist_pdf_sgn_norm)

        # now make the fit and save the parameters
        h_fit = self.file.Get(self.cat_btag+"_"+self.cat_kin+"/"+hname).Clone(hname+"_clone_fit")
        if rebin_factor>1. :
            h_fit.Rebin(rebin_factor)
        ROOT.SetOwnership(h_fit, False ) 

        self.x.setRange( FitSgnCfg[sgn_name]['fit_range'][0], FitSgnCfg[sgn_name]['fit_range'][1] )
        data_sgn_fit = ROOT.RooDataHist("data_sgn_"+sgn_name+"_fit", "", ROOT.RooArgList(self.x), h_fit, 1.0)

        mean = ROOT.RooRealVar("mean_sgn_"+sgn_name, "", FitSgnCfg[sgn_name]['mean'][0], FitSgnCfg[sgn_name]['mean'][1])
        sigma = ROOT.RooRealVar("sigma_sgn_"+sgn_name, "", FitSgnCfg[sgn_name]['sigma'][0], FitSgnCfg[sgn_name]['sigma'][1])
        xi = ROOT.RooRealVar("xi_sgn_"+sgn_name, "", FitSgnCfg[sgn_name]['xi'][0], FitSgnCfg[sgn_name]['xi'][1])
        rho1 = ROOT.RooRealVar("rho1_sgn_"+sgn_name, "", FitSgnCfg[sgn_name]['rho1'][0], FitSgnCfg[sgn_name]['rho1'][1])
        rho2 = ROOT.RooRealVar("rho2_sgn_"+sgn_name, "", FitSgnCfg[sgn_name]['rho2'][0], FitSgnCfg[sgn_name]['rho2'][1])
        gcs.append(mean)
        gcs.append(sigma)
        gcs.append(xi)
        gcs.append(rho1)
        gcs.append(rho2)

        buk_pdf_sgn_fit = ROOT.RooBukinPdf("buk_pdf_sgn_"+sgn_name+"_fit","", self.x, mean, sigma, xi, rho1, rho2)       
        buk_pdf_sgn_norm = ROOT.RooRealVar("buk_pdf_sgn_"+sgn_name+"_norm","", norm)
        buk_pdf_sgn_norm.setConstant(1)

        if spin_symmetric:
            sgn_name2 = "Spin0"+sgn_name[5:] if "Spin2" in sgn_name else "Spin2"+sgn_name[5:]
            hname2 = "signal_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+sgn_name2
            print "\tAdding.....", hname2
            h2 = self.file.Get(self.cat_btag+"_"+self.cat_kin+"/"+hname2).Clone(hname2+"_clone_fit")
            if rebin_factor>1.:
                h2.Rebin(rebin_factor)            
            data_sgn2_fit = ROOT.RooDataHist("data_sgn_"+sgn_name2+"_fit", "", ROOT.RooArgList(self.x), h2, 1.0)
            data_sgn_fit.add(data_sgn2_fit)

        res = buk_pdf_sgn_fit.fitTo(data_sgn_fit, 
                                    RooFit.Strategy(1), 
                                    RooFit.Minimizer("Minuit2"), 
                                    RooFit.Minos(1), 
                                    RooFit.Save(1), 
                                    RooFit.PrintLevel(-1), 
                                    RooFit.PrintEvalErrors(0))
        res.Print()

        # save a snapshot
        self.plot( data=data_sgn_fit, pdfs=[buk_pdf_sgn_fit], res=res, add_pulls=True, legs=[("#splitline{#mu=%.0f, #sigma=%.0f}" % (mean.getVal(), sigma.getVal()))], ran=sgn_name, n_par=5, title=sgn_name, header=sgn_name)

        # create a new pdf with correct x range
        self.x.setRange(self.x.getMin(self.x_name), self.x.getMax(self.x_name))
        buk_pdf_sgn = ROOT.RooBukinPdf("buk_pdf_sgn_"+sgn_name,"", self.x, mean, sigma, xi, rho1, rho2)       

        if set_param_const:
            mean.setConstant(1)
            sigma.setConstant(1)
            xi.setConstant(1)
            rho1.setConstant(1)
            rho2.setConstant(1)

        self.imp(buk_pdf_sgn)
        self.imp(buk_pdf_sgn_norm)

        # add a bias term
        bias = ROOT.RooRealVar("bias_sgn_"+sgn_name, "", -5.0, +5.0)

        buk_pdf_sgn_bias = ROOT.RooBukinPdf("buk_pdf_sgn_bias_"+sgn_name,"", self.x, mean, sigma, xi, rho1, rho2)
        #buk_pdf_sgn_bias_norm = ROOT.RooRealVar("buk_pdf_sgn_bias_"+sgn_name+"_norm","", 0.0)
        buk_pdf_sgn_bias_norm = ROOT.RooFormulaVar("buk_pdf_sgn_bias_"+sgn_name+"_norm", "@0*@1", ROOT.RooArgList(buk_pdf_sgn_norm, bias) )
        #buk_pdf_sgn_norm.setConstant(1)

        self.imp(buk_pdf_sgn_bias)
        self.imp(buk_pdf_sgn_bias_norm)
        #self.imp(bias)

    # add signal systematics to ws
    def add_syst_to_ws(self, sgn_name="Spin0_M750", rebin_factor=1.0, spin_symmetric=False):

        # start with nominal pdf...
        pdfs = [self.w.pdf("buk_pdf_sgn_"+sgn_name)]

        # collect systematic variations
        shifts = {}

        # jet systematics
        for syst in ["JECUp", "JECDown", "JERUp", "JERDown"]:
            hname = "signal_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+syst+"_"+sgn_name
            h = self.file.Get(self.cat_btag+"_"+self.cat_kin+"/"+hname).Clone(hname+"_name")
            if rebin_factor>1. :
                h.Rebin(rebin_factor)
            ROOT.SetOwnership(h, False ) 

            self.x.setRange( FitSgnCfg[sgn_name]['fit_range'][0], FitSgnCfg[sgn_name]['fit_range'][1] )
            data_sgn = ROOT.RooDataHist("data_sgn_"+syst+"_"+sgn_name, "", ROOT.RooArgList(self.x), h, 1.0)

            if spin_symmetric:
                sgn_name2 = "Spin0"+sgn_name[5:] if "Spin2" in sgn_name else "Spin2"+sgn_name[5:]
                hname2 = "signal_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+syst+"_"+sgn_name2
                print "\tAdding.....", hname2
                h2 = self.file.Get(self.cat_btag+"_"+self.cat_kin+"/"+hname2).Clone(hname2+"_clone")
                if rebin_factor>1.:
                    h2.Rebin(rebin_factor)            
                data_sgn2 = ROOT.RooDataHist("data_sgn_"+syst+"_"+sgn_name2, "", ROOT.RooArgList(self.x), h2, 1.0)
                data_sgn.add(data_sgn2)

            norm = data_sgn.sumEntries()

            mean = ROOT.RooRealVar("mean_sgn_"+syst+"_"+sgn_name, "", FitSgnCfg[sgn_name]['mean'][0], FitSgnCfg[sgn_name]['mean'][1])
            sigma = ROOT.RooRealVar("sigma_sgn_"+syst+"_"+sgn_name, "", FitSgnCfg[sgn_name]['sigma'][0], FitSgnCfg[sgn_name]['sigma'][1])
            mean.setVal( self.w.var("mean_sgn_"+sgn_name).getVal() )
            sigma.setVal( self.w.var("sigma_sgn_"+sgn_name).getVal() )
            xi = ROOT.RooRealVar("xi_sgn_"+syst+"_"+sgn_name, "", self.w.var("xi_sgn_"+sgn_name).getVal())
            rho1 = ROOT.RooRealVar("rho1_sgn_"+syst+"_"+sgn_name, "", self.w.var("rho1_sgn_"+sgn_name).getVal())
            rho2 = ROOT.RooRealVar("rho2_sgn_"+syst+"_"+sgn_name, "", self.w.var("rho2_sgn_"+sgn_name).getVal())
            if "JEC" in syst:
                mean.setConstant(0)
                sigma.setConstant(1) #1
            if "JER" in syst:
                mean.setConstant(1) #1
                sigma.setConstant(0)
            xi.setConstant(1)
            rho1.setConstant(1)
            rho2.setConstant(1)

            buk_pdf_sgn = ROOT.RooBukinPdf("buk_pdf_sgn_"+syst+"_"+sgn_name,"", self.x, mean, sigma, xi, rho1, rho2)            
            ROOT.SetOwnership(buk_pdf_sgn, False )  

            buk_pdf_sgn.fitTo(data_sgn, 
                              RooFit.Strategy(1), 
                              RooFit.Minimizer("Minuit2"), 
                              RooFit.Minos(1), 
                              RooFit.PrintLevel(-1), 
                              RooFit.PrintEvalErrors(0))

            shifts[syst] = [mean.getVal(), sigma.getVal(), norm]

            gcs.append(mean)
            gcs.append(sigma)
            gcs.append(xi)
            gcs.append(rho1)
            gcs.append(rho2)
            pdfs.append(buk_pdf_sgn)
 

        # btag systematics
        for syst in ["CSVSFUp", "CSVSFDown"]:
            hname = "signal_"+self.cat_btag+"_"+syst+"_"+self.cat_kin+"_"+self.x_name+"_"+sgn_name
            h = self.file.Get(self.cat_btag+"_"+syst+"_"+self.cat_kin+"/"+hname)
            ROOT.SetOwnership(h, False ) 
            norm = self.w.var("buk_pdf_sgn_"+sgn_name+"_norm").getVal()
            if h!=None:
                self.x.setRange(self.x.getMin(self.x_name), self.x.getMax(self.x_name))
                data = ROOT.RooDataHist("data_sgn_"+syst+"_"+sgn_name, "", ROOT.RooArgList(self.x), h, 1.0)
                ROOT.SetOwnership(data, False )
                norm = data.sumEntries()
            shifts[syst] = [norm]

        # HLT systematics
        for syst in ["HLTKinUp", "HLTKinDown"]:
            hname = "signal_"+self.cat_btag+"_"+(self.cat_kin).split('_')[0]+"_"+syst+"_"+(self.cat_kin).split('_')[1]+"_"+self.x_name+"_"+sgn_name
            h = self.file.Get(self.cat_btag+"_"+(self.cat_kin).split('_')[0]+"_"+syst+"_"+(self.cat_kin).split('_')[1]+"/"+hname)
            ROOT.SetOwnership(h, False ) 
            norm = self.w.var("buk_pdf_sgn_"+sgn_name+"_norm").getVal()
            if h!=None:
                self.x.setRange(self.x.getMin(self.x_name), self.x.getMax(self.x_name))
                data = ROOT.RooDataHist("data_sgn_"+syst+"_"+sgn_name, "", ROOT.RooArgList(self.x), h, 1.0)
                ROOT.SetOwnership(data, False )
                norm = data.sumEntries()
            shifts[syst] = [norm]

        # jec scale systematics
        for syst in ["JECUp", "JECDown"]:
            hname = "signal_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+syst+"_"+sgn_name
            h = self.file.Get(self.cat_btag+"_"+self.cat_kin+"/"+hname)
            ROOT.SetOwnership(h, False ) 
            norm = self.w.var("buk_pdf_sgn_"+sgn_name+"_norm").getVal()
            if h!=None:
                self.x.setRange(self.x.getMin(self.x_name), self.x.getMax(self.x_name))
                data = ROOT.RooDataHist("data_sgn_"+syst+"_"+sgn_name, "", ROOT.RooArgList(self.x), h, 1.0)
                ROOT.SetOwnership(data, False )
                norm = data.sumEntries()
            shifts[syst][2] = norm

        csv = max( abs(shifts["CSVSFUp"][0]-self.w.var("buk_pdf_sgn_"+sgn_name+"_norm").getVal()), 
                   abs(shifts["CSVSFDown"][0]-self.w.var("buk_pdf_sgn_"+sgn_name+"_norm").getVal()))
        hlt_norm = max( abs(shifts["HLTKinUp"][0]-self.w.var("buk_pdf_sgn_"+sgn_name+"_norm").getVal()), 
                        abs(shifts["HLTKinDown"][0]-self.w.var("buk_pdf_sgn_"+sgn_name+"_norm").getVal()))

        jec = max( abs(shifts["JECUp"][0]-self.w.var("mean_sgn_"+sgn_name).getVal()), 
                   abs(shifts["JECDown"][0]-self.w.var("mean_sgn_"+sgn_name).getVal()))
        jer = max( abs(shifts["JERUp"][1]-self.w.var("sigma_sgn_"+sgn_name).getVal()), 
                   abs(shifts["JERDown"][1]-self.w.var("sigma_sgn_"+sgn_name).getVal()) ) 
        jec_norm = max( abs(shifts["JECUp"][2]-self.w.var("buk_pdf_sgn_"+sgn_name+"_norm").getVal()), 
                        abs(shifts["JECDown"][2]-self.w.var("buk_pdf_sgn_"+sgn_name+"_norm").getVal()))

        csv_shift = ROOT.RooRealVar("CSV_shift_"+sgn_name, "", csv )
        hlt_shift =  ROOT.RooRealVar("HLTKin_shift_"+sgn_name, "", hlt_norm )
        mean_shift = ROOT.RooRealVar("mean_shift_"+sgn_name, "", jec )
        sigma_shift = ROOT.RooRealVar("sigma_shift_"+sgn_name, "", jer )
        jec_norm_shift = ROOT.RooRealVar("jec_norm_shift_"+sgn_name, "", jec_norm )

        self.imp(csv_shift)
        self.imp(hlt_shift)
        self.imp(mean_shift)
        self.imp(sigma_shift)
        self.imp(jec_norm_shift)

        # set mean and sigma as floating
        self.w.var("mean_sgn_"+sgn_name).setConstant(0)
        self.w.var("sigma_sgn_"+sgn_name).setConstant(0)

        # save a snapshot
        for gc in gcs:
            if gc.GetName()=="mean_sgn_JECUp_"+sgn_name:
                gc.setVal( self.w.var("mean_sgn_"+sgn_name).getVal()+jec )
            elif gc.GetName()=="mean_sgn_JECDown_"+sgn_name:
                gc.setVal( self.w.var("mean_sgn_"+sgn_name).getVal()-jec )
            elif gc.GetName()=="sigma_sgn_JERUp_"+sgn_name:
                gc.setVal( self.w.var("sigma_sgn_"+sgn_name).getVal()+jer )
            elif gc.GetName()=="sigma_sgn_JERDown_"+sgn_name:
                gc.setVal( self.w.var("sigma_sgn_"+sgn_name).getVal()-jer )

        self.x.setRange( FitSgnCfg[sgn_name]['fit_range'][0], FitSgnCfg[sgn_name]['fit_range'][1] )
        self.plot(data=None, pdfs=pdfs, res=None, add_pulls=False, legs=["Nominal", "JEC up", "JEC down", "JER up", "JER down"], ran=sgn_name, n_par=5, title=sgn_name+"_JEC-JER", header=sgn_name)

    # Add background pdf to ws.
    # A preliminary fit is done. 
    # N.B.: the 'data' parameters are used for the fit
    def add_bkg_to_ws(self, pdf_names=["dijet"], rebin_factor=1.0, set_param_const=False):

        hname = "background_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name
        print hname
        h = self.file.Get(self.cat_btag+"_"+self.cat_kin+"/"+hname).Clone(hname+"_clone")
        if rebin_factor>1. :
            h.Rebin(rebin_factor)
        ROOT.SetOwnership(h, False ) 

        self.x.setRange(self.x.getMin(self.x_name), self.x.getMax(self.x_name))
        data_bkg = ROOT.RooDataHist("data_bkg", "", ROOT.RooArgList(self.x), h, 1.0)
        self.imp(data_bkg)

        norm = data_bkg.sumEntries()

        hist_pdf_bkg = ROOT.RooHistPdf("hist_pdf_bkg","", ROOT.RooArgSet(self.x), data_bkg, 0)        
        hist_pdf_bkg_norm = ROOT.RooRealVar("hist_pdf_bkg_norm", "", norm )
        hist_pdf_bkg_norm.setConstant(0)
        self.imp(hist_pdf_bkg)
        self.imp(hist_pdf_bkg_norm)
        
        for pdf_name in pdf_names:
            print pdf_name
            pdf_range = ('%.0fto%.0f' % (self.x.getMin(),self.x.getMax()))
            print "\tRange: "+pdf_range
            pdf_order = ('deg%d' % FTestCfg_data[pdf_name]['MaxOrder'][pdf_range]) if pdf_range in FTestCfg_data[pdf_name]['MaxOrder'].keys() else ('deg%d' % FTestCfg_data[pdf_name]['MaxOrder']["default"])
            if pdf_order not in FitBkgCfg_data[pdf_name].keys():
                pdf_order = "any"
            print "\tOrder matching 'range': "+pdf_order
            if pdf_range not in FitBkgCfg_data[pdf_name][pdf_order].keys():
                pdf_range = "default"
            print "\tRange matching 'order': "+pdf_range

            [pdf_bkg, param_bkg] = generate_pdf(self.x, pdf_name=pdf_name, n_param=FTestCfg_data[pdf_name]['MaxOrder'][pdf_range], n_iter=0, gcs=gcs, mass_range=pdf_range, parameter_set="default", is_data=True)
            pdf_bkg.SetName(pdf_name+"_pdf_bkg")

            pdf_bkg_norm = ROOT.RooRealVar(pdf_name+"_pdf_bkg_norm","", norm)
            pdf_bkg_norm.setConstant(0) 

            res = pdf_bkg.fitTo(data_bkg, 
                                RooFit.Strategy(1), 
                                RooFit.Minimizer("Minuit2"), 
                                RooFit.Minos(1), 
                                RooFit.Save(1), 
                                RooFit.PrintLevel(-1), 
                                RooFit.PrintEvalErrors(0))
            res.Print()
            
            h_rebinned = data_bkg.createHistogram(hname+"_"+pdf_name+"_rebinned", self.x, RooFit.Binning( int((self.x.getMax()-self.x.getMin())/5.0) , self.x.getMin(), self.x.getMax()) )
            data_bkg_rebinned = ROOT.RooDataHist("data_"+pdf_name+"_rebinned","", ROOT.RooArgList(self.x), h_rebinned, 1.0)

            self.plot( data=data_bkg_rebinned, pdfs=[pdf_bkg], res=None, add_pulls=True, legs=["#splitline{"+pdf_name+"}"], ran=pdf_name, n_par=FTestCfg_data[pdf_name]['ndof'][pdf_range], title="background_"+pdf_name, header="Simulation, L=2.63 fb^{-1}")

            # reset parameters to be used in RooWorkspace
            parameter_set = "combine" if "combine" in FitBkgCfg_data[pdf_name][pdf_order][pdf_range].keys() else "default"
            for p in xrange( FTestCfg_data[pdf_name]['ndof'][pdf_range] ):            
                [p_low, p_high] = FitBkgCfg_data[pdf_name][pdf_order][pdf_range][parameter_set][("a%d" % p)]
                param_bkg[p].setRange(p_low, p_high)
                param_bkg[p].setVal( (p_high+p_low)*0.5 )
                if set_param_const:
                    param_bkg[p].setConstant(1)

            self.imp(pdf_bkg)
            self.imp(pdf_bkg_norm)


    # add data_obs to ws
    def add_data_to_ws(self, rebin_factor=1.0):

        hname = "data_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name
        print hname
        h = self.file.Get(self.cat_btag+"_"+self.cat_kin+"/"+hname).Clone(hname+"_clone")
        if rebin_factor>1. :
            h.Rebin(rebin_factor)            
        ROOT.SetOwnership(h, False ) 

        data_norm = h.Integral()
        data_notm_int = int(data_norm)
        h.Scale(data_notm_int/data_norm)

        # set default range to Range(self.x_name)
        self.w.var("x").setRange(self.x.getMin(self.x_name), self.x.getMax(self.x_name))

        self.x.setRange(self.x.getMin(self.x_name), self.x.getMax(self.x_name))
        data_obs = ROOT.RooDataHist("data_obs", "", ROOT.RooArgList(self.x), h, 1.0)
        self.imp(data_obs)
        self.bin_size = data_obs.binVolume(ROOT.RooArgSet(self.x))

        if not self.plot_blind:
            self.plot( data=data_obs, pdfs=[], res=None, add_pulls=False, legs=[], ran='dijet', n_par=0, title="data", header="Data, L=2.63 fb^{-1}")

    # add data_obs to ws
    def test_datafit(self, pdf_names=['dijet'], rebin_factor=1.0):

        hname = "data_"+self.cat_btag+"_"+self.cat_kin+"_"+self.x_name
        print hname
        h = self.file.Get(self.cat_btag+"_"+self.cat_kin+"/"+hname).Clone(hname+"_clone")
        if rebin_factor>1. :
            h.Rebin(rebin_factor)            
        ROOT.SetOwnership(h, False ) 

        self.x.setRange(self.x.getMin(self.x_name), self.x.getMax(self.x_name))
        data_bkg = ROOT.RooDataHist("data", "", ROOT.RooArgList(self.x), h, 1.0)

        for pdf_name in pdf_names:
            print pdf_name
            pdf_range = ('%.0fto%.0f' % (self.x.getMin(),self.x.getMax()))
            print "\tRange: "+pdf_range
            pdf_order = ('deg%d' % FTestCfg_data[pdf_name]['MaxOrder'][pdf_range]) if pdf_range in FTestCfg_data[pdf_name]['MaxOrder'].keys() else ('deg%d' % FTestCfg_data[pdf_name]['MaxOrder']["default"])
            if pdf_order not in FitBkgCfg_data[pdf_name].keys():
                pdf_order = "any"
            print "\tOrder matching 'range': "+pdf_order
            if pdf_range not in FitBkgCfg_data[pdf_name][pdf_order].keys():
                pdf_range = "default"
            print "\tRange matching 'order': "+pdf_range

            [pdf_bkg, param_bkg] = generate_pdf(self.x, pdf_name=pdf_name, n_param=FTestCfg_data[pdf_name]['MaxOrder'][pdf_range], n_iter=1, gcs=gcs, mass_range=pdf_range, parameter_set="default", is_data=True)

            res = pdf_bkg.fitTo(data_bkg, 
                                RooFit.Strategy(2), 
                                RooFit.Minimizer("Minuit2"), 
                                RooFit.Minos(1), 
                                RooFit.Save(1), 
                                RooFit.PrintLevel(-1), 
                                RooFit.PrintEvalErrors(0))
            res.Print()
            
            h_rebinned = data_bkg.createHistogram(hname+"_"+pdf_name+"_rebinned", self.x, RooFit.Binning( int((self.x.getMax()-self.x.getMin())/5.0) , self.x.getMin(), self.x.getMax()) )
            data_bkg_rebinned = ROOT.RooDataHist("data_"+pdf_name+"_rebinned","", ROOT.RooArgList(self.x), h_rebinned, 1.0)

            self.plot( data=data_bkg_rebinned, pdfs=[pdf_bkg], res=None, add_pulls=True, legs=[pdf_name], ran=pdf_name, n_par=FTestCfg_data[pdf_name]['ndof'][pdf_range], title="datafit_"+pdf_name)

    # name for final root and png
    def get_save_name(self):        
        return  self.cat_btag+"_"+self.cat_kin+"_"+self.x_name+"_"+("%.0f" % (self.x.getMin(self.x_name)))+"to"+("%.0f" % (self.x.getMax(self.x_name)))

    # create the ws
    def create_workspace(self, signals=[], pdf_names=["dijet"], debug_sgn=True):

        for sgn in signals:
            self.add_sgn_to_ws(sgn_name=sgn, rebin_factor=100, set_param_const=True, spin_symmetric=False)
            self.add_syst_to_ws(sgn_name=sgn, rebin_factor=10, spin_symmetric=False)
        
        if debug_sgn:            
            self.file.Close()
            return

        self.add_bkg_to_ws(pdf_names=pdf_names, rebin_factor=-1, set_param_const=False)
        self.add_data_to_ws(rebin_factor=-1)

        if not self.plot_blind:
            self.test_datafit(pdf_names=pdf_names, rebin_factor=-1)

        self.w.Print()
        self.w.writeToFile(self.save_dir+self.ws_name+"_"+self.get_save_name()+".root")

        self.file.Close()

###########################

cfg_cat_btag = argv[1] if len(argv)>=2 else "Had_MT"
cfg_cat_kin = argv[2] if len(argv)>=3 else "MinPt100_DH1p6" 
cfg_name = argv[3] if len(argv)>=4 else "MassFSR"
cfg_xmin = float(argv[4]) if len(argv)>=5 else 550.
cfg_xmax = float(argv[5]) if len(argv)>=6 else 1200.

signals = []
for mass in [550, 600, 650, 700, 750, 800, 850, 900, 1000, 1100, 1200]:
#for mass in [600]:
    for spin in [0,2]:
        sample = ("Spin%d_M%d" % (spin, mass))
        "Adding signal sample....", sample
        signals.append(sample)

xbbfact = XbbFactory(fname="plot.root", ws_name="Xbb_workspace", read_dir="./plots/V7/", save_dir="./plots/V7/", save_ext=['png','pdf'], blind_plot=True)
xbbfact.add_category(cat_btag=cfg_cat_btag, cat_kin=cfg_cat_kin)
xbbfact.create_mass(name=cfg_name, xmin=cfg_xmin, xmax=cfg_xmax)
xbbfact.create_workspace( signals=signals,
                          #signals=["Spin0_M750"],    
                          #pdf_names=["polydijet", "dijet"],
                          pdf_names=["dijet", "polydijet"],
                          #pdf_names=["dijet", "polydijet", "pol", "exp", "pow", "polyexp"] 
                          debug_sgn=False
                          )

for gc in gcs:
    gc.Print()

