from sys import argv
argv.append( '-b-' )

import ROOT
from ROOT import RooFit
ROOT.gROOT.SetBatch(True)
argv.remove( '-b-' )

import math
import sys
sys.path.append('./')

PdfsFTest = {
    "pol" : {
        "FirstOrder" : 4,
        "LastOrder" : 9,
        "Match" : -1
        },
    "exp" : {
        "FirstOrder" : 1,
        "LastOrder" : 4,
        "Match" : -1
        },
    "pow" : {
        "FirstOrder" : 1,
        "LastOrder" : 4,
        "Match" : -1
        },
    "polyexp" : {
        "FirstOrder" : 1,
        "LastOrder" : 5,
        "Match" : -1
        },
}

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
        self.coeff = ROOT.RooArgList()

    def generate_pdf(self, pdf_name="pol", n_param=4):

        pdf = None
        
        if pdf_name=="pol":            
            self.coeff.removeAll()
            for p in xrange(n_param):
                param = ROOT.RooRealVar( ("a%d_deg%d" % (p,n_param)), "", -1.5, 1.5)
                if p==0:
                    param.setVal(1.)
                    param.setConstant(1)
                gcs.append(param)
                self.coeff.add(param)
            self.coeff.Print()
            pdf = ROOT.RooBernstein( ("pol_deg%d" % n_param) , "", self.x, self.coeff)

        elif pdf_name=="exp":            
            self.coeff.removeAll()
            formula = "TMath::Exp("
            for p in xrange(n_param):
                p_name = ("a%d_deg%d" % (p,n_param))
                formula += p_name
                for exp in xrange(p+1):
                    formula += "*x"
                p_min = -1e-04 if p!=0 else -0.2
                p_max = +1e-04 if p!=0 else -0.
                param = ROOT.RooRealVar( p_name, "", p_min, p_max)
                gcs.append(param)
                self.coeff.add(param)
                if p<(n_param-1):
                    formula += " + "
            formula += ")"
            print formula
            self.coeff.add(self.x)
            self.coeff.Print()
            pdf = ROOT.RooGenericPdf( ("exp_deg%d" % n_param), "", formula, self.coeff )

        elif pdf_name=="pow":            
            self.coeff.removeAll()
            formula = "TMath::Power(x, "
            for p in xrange(n_param):
                p_name = ("a%d_deg%d" % (p,n_param))
                formula += p_name
                for exp in xrange(p):
                    formula += "*x"
                p_min = -ROOT.TMath.Power(10,-3*p + 1)
                p_max = +ROOT.TMath.Power(10,-3*p + 1) 
                param = ROOT.RooRealVar( p_name, "", p_min, p_max)
                gcs.append(param)
                if p<(n_param-1):
                    formula += " + "
                self.coeff.add(param)
            formula += ")"
            print formula
            self.coeff.add(self.x)
            self.coeff.Print()
            pdf = ROOT.RooGenericPdf( ("pow_deg%d" % n_param), "", formula, self.coeff )

        elif pdf_name=="polyexp":            
            self.coeff.removeAll()
            formula = "TMath::Max(1e-50,"
            for p in xrange(n_param):
                p_name = ("a%d_deg%d" % (p,n_param))
                p_min = -5. if p!=0 else -0.2
                p_max = +5. if p!=0 else -0.
                param = ROOT.RooRealVar( p_name, "", p_min, p_max)
                gcs.append(param)
                self.coeff.add(param)
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
            self.coeff.add(self.x)
            self.coeff.Print()
            pdf = ROOT.RooGenericPdf( ("polyexp_deg%d" % n_param), "", formula, self.coeff )

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


    def doFTest(self, data_name="data_bkg"):

        self.data = self.w.data(data_name)
        self.data.Print()

        for pdf_name in [
            #"pol"
            #"exp"
            #"pow"
            "polyexp"
            ]:         
            pdfs = []
            npars = []
            legs = []
            probs = []
            firstOrder = PdfsFTest[pdf_name]["FirstOrder"]
            lastOrder = PdfsFTest[pdf_name]["LastOrder"]
            prevNll = 0.
            match = False
            for p in range(firstOrder, lastOrder+1):
                pdf = self.generate_pdf(pdf_name, p)
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

########################
bs = BiasStudy(fname="Xbb_workspace_Had_MT_MinPt150_DH1p6_MassFSR_550to1200", 
               ws_name="Xbb_workspace", version="V4", saveDir="/scratch/bianchi/")
bs.doFTest(data_name="data_bkg")

for gc in gcs:
    gc.Print()
