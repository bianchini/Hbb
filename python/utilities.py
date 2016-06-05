import ROOT
from ROOT import RooFit
import math

import sys
sys.path.append('./')

from parameters_cfi import FitCfg


sqrts = 1.3e+04

FitParam = {
    "Spin0_M650" : {
        'mean' : [550.,650.],
        'sigma' : [30., 100.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [400., 900.],
        'bias' : 0.01,
        },
    "Spin0_M750" : {
        'mean' : [650.,750.],
        'sigma' : [20., 100.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [400., 1000.],
        'bias' : 0.01,
        },
    "Spin0_M850" : {
        'mean' : [750.,900.],
        'sigma' : [20., 200.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [400., 1100.],
        'bias' : 0.01,
        },
    "Spin0_M1000" : {
        'mean' : [800.,1100.],
        'sigma' : [50., 400.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [400., 1200.],
        'bias' : 0.01,
        },
    "Spin0_M1200" : {
        'mean' : [900.,1300.],
        'sigma' : [50., 400.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [600., 1400.],
        'bias' : 0.01,
        },
    "Spin2_M650" : {
        'mean' : [550.,650.],
        'sigma' : [30., 100.],
        'xi' : [-3., +3.],
        'rho1' : [-1.0, +1.0],
        'rho2' : [-1.0, +1.0],
        'fit_range' : [400., 900.],
        'bias' : 0.01,
        },
    "Spin2_M750" : {
        'mean' : [650.,750.],
        'sigma' : [20., 100.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [400., 1000.],
        'bias' : 0.01,
        },
    "Spin2_M850" : {
        'mean' : [750.,900.],
        'sigma' : [20., 200.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [400., 1100.],
        'bias' : 0.01,
        },
    "Spin2_M1000" : {
        'mean' : [800.,1100.],
        'sigma' : [50., 400.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [400., 1200.],
        'bias' : 0.01,
        },
    "Spin2_M1200" : {
        'mean' : [900.,1300.],
        'sigma' : [50., 400.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [600., 1400.],
        'bias' : 0.01,
        }
}


PdfsFTest = {
    "pol" : {
        "FirstOrder" : 4,
        "LastOrder" : 8,
        "Match" : -1,
        "MaxOrder" : 6, #8,
        "ndof" : 6,
        "fit_range" : [400., 1200.], 
        },
    "exp" : {
        "FirstOrder" : 1,
        "LastOrder" : 3,
        "Match" : -1,
        "MaxOrder" : 3, #3,
        "ndof" : 3, #3,
        "fit_range" : [400., 1200.], 
        },
    "pow" : {
        "FirstOrder" : 1,
        "LastOrder" : 3,
        "Match" : -1,
        "MaxOrder" : 2,
        "ndof" : 2,
        "fit_range" : [400., 1200.], 
        },
    "polyexp" : {
        "FirstOrder" : 1,
        "LastOrder" : 4,
        "Match" : -1,
        "MaxOrder" : 3,
        "ndof" : 3,
        "fit_range" : [400., 1200.], 
        },
    "dijet" : {
        "FirstOrder" : 1,
        "LastOrder" : 5,
        "Match" : -1,
        "MaxOrder" : 2,
        "ndof" : 2,
        "fit_range" : [400., 1200.], 
        },
    "polydijet" : {
        "FirstOrder" : 1,
        "LastOrder" : 3,
        "Match" : -1,
        "MaxOrder" : 1,#2
        "ndof" : 2,#3
        "fit_range" : [400., 1200.], 
        },
    "expdijet" : {
        "FirstOrder" : 1,
        "LastOrder" : 3,
        "Match" : -1,
        "MaxOrder" : 3,
        "ndof" : 3,
        "fit_range" : [400., 1200.], 
        },
}

def generate_pdf(x=ROOT.RooRealVar(), pdf_name="pol", n_param=4, n_iter=0, gcs=[]):

    pdf = None
    coeff = ROOT.RooArgList()

    # P(x;n)
    if pdf_name=="pol":            
        coeff.removeAll()
        for p in xrange(n_param):            
            p_min = -1. 
            p_max = +1. 
            if p==0:
                p_min = -1. 
                p_max = +1.                 
            elif p==1:
                p_min = -1 
                p_max = +1
            elif p==2:
                p_min = -1 
                p_max = +1 
            elif p==3:
                p_min = -1
                p_max = +1
            elif p==4:
                p_min = -1. 
                p_max = +1. 
            elif p==5:
                p_min = -1. 
                p_max = +1. 
            elif p==6:
                p_min = -1. 
                p_max = +1. 
            elif p==7:
                p_min = -1. 
                p_max = +1. 
            elif p==8:
                p_min = -1. 
                p_max = +1.                 

            param = ROOT.RooRealVar( ("a%d_%s_deg%d_%d" % (p,pdf_name,n_param,n_iter)), "", p_min, p_max)
            if p==0:
                param.setVal(1.)
                param.setConstant(1)
            gcs.append(param)
            coeff.add(param)
        coeff.Print()
        pdf = ROOT.RooBernstein( ("%s_deg%d_%d" % (pdf_name,n_param,n_iter)) , "", x, coeff)
        
    # exp(P(x;n))
    elif pdf_name=="exp":            
        coeff.removeAll()
        formula = "TMath::Exp("
        for p in xrange(n_param):
            p_name = ("a%d_%s_deg%d_%d" % (p,pdf_name,n_param,n_iter))
            formula += p_name
            for exp in xrange(p+1):
                formula += "*x"
            p_min = -1
            p_max = +1
            if p==0:
                p_min = -0.015
                p_max = -0.013
            elif p==1:
                p_min = +0.5e-06
                p_max = +2e-05
            elif p==2:
                p_min = -1.0e-9
                p_max = -1.0e-10
            elif p==2:
                p_min = -math.pow(10,-p*3-2) if p!=0 else -0.02
                p_max = +math.pow(10,-p*3-2) if p!=0 else -0.
                
            param = ROOT.RooRealVar( p_name, "", p_min, p_max)
            gcs.append(param)
            coeff.add(param)
            if p<(n_param-1):
                formula += " + "
        formula += ")"
        print formula
        coeff.add(x)
        coeff.Print()
        pdf = ROOT.RooGenericPdf( ("%s_deg%d_%d" % (pdf_name,n_param,n_iter)), "", formula, coeff )

    # x^P(x;n)
    elif pdf_name=="pow":            
        coeff.removeAll()
        formula = "TMath::Power(x, "
        for p in xrange(n_param):
            p_name = ("a%d_%s_deg%d_%d" % (p,pdf_name,n_param,n_iter))
            formula += p_name
            for exp in xrange(p):
                formula += "*x"
            p_min = -10.
            p_max = +10.
            if p==0:
                p_min = -4.2 #-10
                p_max = -3.3 #+10.
            elif p==1:
                p_min = -4.2e-04 #-math.pow(10,-2) 
                p_max = -3.1e-04 #+math.pow(10,-2) 
            elif p==2:
                p_min = -2.2e-08 #-math.pow(10,-5) 
                p_max = -1.8e-08 #+math.pow(10,-5) 
            elif p==3:
                p_min = +0.5e-11 #-math.pow(10,-9) 
                p_max = +2.0e-11 #+math.pow(10,-9) 
            elif p==4:
                p_min = -math.pow(10,-12) 
                p_max = +math.pow(10,-12) 

            param = ROOT.RooRealVar( p_name, "", p_min, p_max)
            gcs.append(param)
            if p<(n_param-1):
                formula += " + "
            coeff.add(param)
        formula += ")"
        print formula
        coeff.add(x)
        coeff.Print()
        pdf = ROOT.RooGenericPdf( ("%s_deg%d_%d" % (pdf_name,n_param,n_iter)), "", formula, coeff )

    # P(x;n) * exp(-kx)
    elif pdf_name=="polyexp":            
        coeff.removeAll()
        formula = "TMath::Max(1e-30,"
        for p in xrange(n_param):
            p_name = ("a%d_%s_deg%d_%d" % (p,pdf_name,n_param,n_iter))
            p_min = -1.
            p_max = +1.
            if p==0:
                p_min = -0.015
                p_max = -0.005
            elif p==1:
                p_min = -0.5e-02 if n_param>2 else +1.0e-07
                p_max = -0.5e-03 if n_param>2 else +5.0e-05
            elif p==2:
                p_min = +1.0e-07
                p_max = +1.0e-05
            elif p==3:
                p_min = +1.0e-12
                p_max = +1.0e-10

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
        coeff.add(x)
        coeff.Print()
        pdf = ROOT.RooGenericPdf( ("%s_deg%d_%d" % (pdf_name,n_param,n_iter)), "", formula, coeff )

    # (1-x)^c/(x^(a+b*log(x)))
    elif pdf_name=="dijet":            
        coeff.removeAll()
        formula = ""
        if n_param==1:
            #formula = ("TMath::Max(1e-30,1./TMath::Power(x/%E, @0))" % (sqrts))
            formula = ("TMath::Exp(-@0*TMath::Log(x/%E))" % (sqrts))
        elif n_param==2:
            #formula = ("TMath::Max(1e-30,1./TMath::Power(x/%E, @0*(1 + @1*TMath::Log(x/%E))))" % (sqrts, sqrts))
            formula = ("TMath::Exp(-@0*TMath::Log(x/%E)-@0*@1*TMath::Log(x/%E)*TMath::Log(x/%E))" % (sqrts, sqrts, sqrts))
        elif n_param==3:
            #formula = ("TMath::Max(1e-30,1./TMath::Power(x/%E, @0*(1 + @1*TMath::Log(x/%E)))*TMath::Power(1-x/%E,@2))" % (sqrts, sqrts, sqrts))
            formula = ("TMath::Exp(-@0*TMath::Log(x/%E)-@0*@1*TMath::Log(x/%E)*TMath::Log(x/%E))*TMath::Power(1-x/%E,@2)" % (sqrts, sqrts, sqrts, sqrts))
        elif n_param==4:
            return [None,None]
        elif n_param==5:
            #formula = ("TMath::Max(1e-30,1./TMath::Power(x/%E, @0*(1 + @1*TMath::Log(x/%E)))*TMath::Power(1-x/%E,@2)*0.5*(TMath::Erf((x-@3)/@4)+1))" % (sqrts, sqrts, sqrts))
            formula = ("TMath::Exp(-@0*TMath::Log(x/%E)-@0*@1*TMath::Log(x/%E)*TMath::Log(x/%E))*0.5*(TMath::Erf((x-@3)/@4)+1)" % (sqrts, sqrts, sqrts))
        for p in xrange(n_param):
            p_name = ("a%d_%s_deg%d_%d" % (p,pdf_name,n_param,n_iter))
            p_min = -1.
            p_max = +1.
            if p==0:
                p_min = 0. 
                p_max = 15.
            elif p==1:
                p_min = -0.05
                p_max = +0.2 
            elif p==2:
                p_min = 0.
                p_max = 1e-04
            elif p==3:
                p_min = 200.
                p_max = 450.
            elif p==4:
                p_min = 100.
                p_max = 300.
            param = ROOT.RooRealVar( p_name, "", p_min, p_max)
            if p==3:
                param.setVal(260.)
                param.setConstant(1)
            gcs.append(param)
            coeff.add(param)

        print formula
        coeff.add(x)
        coeff.Print()
        pdf = ROOT.RooGenericPdf( ("%s_deg%d_%d" % (pdf_name,n_param,n_iter)), "", formula, coeff )

    #  e^(-a*log(x) - b*log(x)*log(x))*P(x;n)
    elif pdf_name=="polydijet":            
        coeff.removeAll()
        formula = ""
        if n_param==1:
            formula = ("TMath::Exp(-@0*TMath::Log(x/%E)-@1*@0*TMath::Log(x/%E)*TMath::Log(x/%E))" % (sqrts, sqrts, sqrts))
        elif n_param==2:
            formula = ("TMath::Exp(-@0*TMath::Log(x/%E)-@1*@0*TMath::Log(x/%E)*TMath::Log(x/%E))*(-1+@2*(x/%E))" % (sqrts, sqrts, sqrts, sqrts))
        elif n_param==3:
            formula = ("TMath::Exp(-@0*TMath::Log(x/%E)-@1*@0*TMath::Log(x/%E)*TMath::Log(x/%E))*(-1+@2*(x/%E)+@3*(x*x/%E/%E))" % (sqrts, sqrts, sqrts, sqrts, sqrts, sqrts))
            
        for p in xrange(n_param+1):
            p_name = ("a%d_%s_deg%d_%d" % (p,pdf_name,n_param,n_iter))
            [p_min, p_max] = FitCfg[pdf_name][("deg%d" % n_param)]["default"]["default"][("a%d" % p)]
            #if p==0:
            #    p_min = 6.0  #10.0
            #    p_max = 10.0 #12.
            #elif p==1:
            #    p_min = #+0.02 #-0.05
            #    p_max = #+0.08 #+0.20
            #elif p==2:
            #    p_min = #35  #35.
            #    p_max = #100 #+1e+02
            #elif p==3:
            #    p_min = -1e+04 #0.
            #    p_max = +1e+04
            #elif p==4:
            #    p_min = -1e+04 #0.
            #    p_max = +1e+04 #0.

            param = ROOT.RooRealVar( p_name, "", p_min, p_max)
            gcs.append(param)
            coeff.add(param)

        print formula
        coeff.add(x)
        coeff.Print()
        pdf = ROOT.RooGenericPdf( ("%s_deg%d_%d" % (pdf_name,n_param,n_iter)), "", formula, coeff )

    #  e^(-a*log(x) - b*log(x)*log(x) - c*x)
    elif pdf_name=="expdijet":            
        coeff.removeAll()
        formula = ""
        if n_param==1:
            formula = ("TMath::Exp(-@0*TMath::Log(x/%E))" % (sqrts))
        elif n_param==2:
            formula = ("TMath::Exp(-@0*TMath::Log(x/%E)-@1*TMath::Log(x/%E)*TMath::Log(x/%E))" % (sqrts, sqrts, sqrts))
        elif n_param==3:
            formula = ("TMath::Exp(-@0*TMath::Log(x/%E)-@1*TMath::Log(x/%E)*TMath::Log(x/%E)-@2*x/%E)" % (sqrts, sqrts, sqrts, sqrts))
            
        for p in xrange(n_param):
            p_name = ("a%d_%s_deg%d_%d" % (p,pdf_name,n_param,n_iter))
            p_min = -1.
            p_max = +1. 
            if p==0:
                p_min =  5. if n_param<3 else +5.0 
                p_max = 15. if n_param<3 else +50.0
            elif p==1:
                p_min = -2.0 if n_param<3 else -1.0 
                p_max = +2.0 if n_param<3 else +5.0
            elif p==2:
                p_min = 35. if n_param<3 else -200. 
                p_max = +1e+02 if n_param<3 else 20. 

            param = ROOT.RooRealVar( p_name, "", p_min, p_max)
            gcs.append(param)
            coeff.add(param)

        print formula
        coeff.add(x)
        coeff.Print()
        pdf = ROOT.RooGenericPdf( ("%s_deg%d_%d" % (pdf_name,n_param,n_iter)), "", formula, coeff )

    pdf.Print()
    return [pdf, coeff]


