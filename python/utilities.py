import ROOT
from ROOT import RooFit
import math

import sys
sys.path.append('./')

from parameters_cfi import *

sqrts = 1.3e+04

def generate_pdf(x=ROOT.RooRealVar(), pdf_name="pol", n_param=4, n_iter=0, gcs=[], mass_range="default", parameter_set="default", is_data=True):

    pdf = None
    coeff = ROOT.RooArgList()

    FitBkgCfg = {}
    if is_data:
        FitBkgCfg = FitBkgCfg_data
    else:
        FitBkgCfg = FitBkgCfg_mc

    # P(x;n)
    if pdf_name=="pol":            
        coeff.removeAll()
        for p in xrange(n_param):            
            deg = ("deg%d" % n_param) if ("deg%d" % n_param) in FitBkgCfg[pdf_name].keys() else "any"
            m_range = mass_range if mass_range in FitBkgCfg[pdf_name][deg].keys() else "default"
            p_set = parameter_set if parameter_set in FitBkgCfg[pdf_name][deg][m_range].keys() else "default"
            [p_min, p_max] = FitBkgCfg[pdf_name][deg][m_range][p_set][("a%d" % p)]
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
            deg = ("deg%d" % n_param) if ("deg%d" % n_param) in FitBkgCfg[pdf_name].keys() else "any"
            m_range = mass_range if mass_range in FitBkgCfg[pdf_name][deg].keys() else "default"
            p_set = parameter_set if parameter_set in FitBkgCfg[pdf_name][deg][m_range].keys() else "default"
            [p_min, p_max] = FitBkgCfg[pdf_name][deg][m_range][p_set][("a%d" % p)]                
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
            deg = ("deg%d" % n_param) if ("deg%d" % n_param) in FitBkgCfg[pdf_name].keys() else "any"
            m_range = mass_range if mass_range in FitBkgCfg[pdf_name][deg].keys() else "default"
            p_set = parameter_set if parameter_set in FitBkgCfg[pdf_name][deg][m_range].keys() else "default"
            [p_min, p_max] = FitBkgCfg[pdf_name][deg][m_range][p_set][("a%d" % p)]                
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
            deg = ("deg%d" % n_param) if ("deg%d" % n_param) in FitBkgCfg[pdf_name].keys() else "any"
            m_range = mass_range if mass_range in FitBkgCfg[pdf_name][deg].keys() else "default"
            p_set = parameter_set if parameter_set in FitBkgCfg[pdf_name][deg][m_range].keys() else "default"
            [p_min, p_max] = FitBkgCfg[pdf_name][deg][m_range][p_set][("a%d" % p)]                
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
            formula = ("TMath::Exp(-@0*TMath::Log(x/%E))" % (sqrts))
        elif n_param==2:
            formula = ("TMath::Exp(-@0*TMath::Log(x/%E)-@0*@1*TMath::Log(x/%E)*TMath::Log(x/%E))" % (sqrts, sqrts, sqrts))
        elif n_param==3:
            formula = ("TMath::Exp(-@0*TMath::Log(x/%E)-@0*@1*TMath::Log(x/%E)*TMath::Log(x/%E))*TMath::Power(1-x/%E,@2)" % (sqrts, sqrts, sqrts, sqrts))
        elif n_param==4:
            return [None,None]
        elif n_param==5:
            formula = ("TMath::Exp(-@0*TMath::Log(x/%E)-@0*@1*TMath::Log(x/%E)*TMath::Log(x/%E))*0.5*(TMath::Erf((x-@3)/@4)+1)" % (sqrts, sqrts, sqrts))
        for p in xrange(n_param):
            p_name = ("a%d_%s_deg%d_%d" % (p,pdf_name,n_param,n_iter))
            deg = ("deg%d" % n_param) if ("deg%d" % n_param) in FitBkgCfg[pdf_name].keys() else "any"
            m_range = mass_range if mass_range in FitBkgCfg[pdf_name][deg].keys() else "default"
            p_set = parameter_set if parameter_set in FitBkgCfg[pdf_name][deg][m_range].keys() else "default"
            [p_min, p_max] = FitBkgCfg[pdf_name][deg][m_range][p_set][("a%d" % p)]                
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
            deg = ("deg%d" % n_param) if ("deg%d" % n_param) in FitBkgCfg[pdf_name].keys() else "any"
            m_range = mass_range if mass_range in FitBkgCfg[pdf_name][deg].keys() else "default"
            p_set = parameter_set if parameter_set in FitBkgCfg[pdf_name][deg][m_range].keys() else "default"
            [p_min, p_max] = FitBkgCfg[pdf_name][deg][m_range][p_set][("a%d" % p)]
            param = ROOT.RooRealVar( p_name, "", p_min, p_max)
            gcs.append(param)
            coeff.add(param)

        print formula
        coeff.add(x)
        coeff.Print()
        pdf = ROOT.RooGenericPdf( ("%s_deg%d_%d" % (pdf_name,n_param,n_iter)), "", formula, coeff )

    pdf.Print()
    return [pdf, coeff]


def get_bias(mass="750", pdf_name="polydijet", deg=2, is_data=True):

    bias = 0.0

    FitBkgCfg = {}
    if is_data:
        FitBkgCfg = FitBkgCfg_data
    else:
        FitBkgCfg = FitBkgCfg_mc

    if pdf_name not in FitBkgCfg.keys():
        print "No pdf_name: Return 0.0"
        return bias

    pdf_order = ("deg%d" % deg)
    if pdf_order not in FitBkgCfg[pdf_name].keys():
        pdf_order = "any"

    if "bias_formula" not in FitBkgCfg[pdf_name][pdf_order].keys():
        print "No bias_formula: Return 0.0"
        return bias

    formula = ROOT.TFormula("formula", FitBkgCfg[pdf_name][pdf_order]["bias_formula"])
    bias = formula.Eval( float(mass) )
    print ("\tbias for %s_%s at m=%.0f = %.2f" % (pdf_name, pdf_order, float(mass), bias))

    return bias


def get_sliding_edges(mass=700):
    ranges = [0.5*mass + 125, mass + 200]
    #ranges = [0.50*mass + 125 + (5 if mass==600 else 0), mass + 200]
    #ranges =  [0.5*mass + 125, m + 150]
    return ranges

def get_sgn_injected(mass=750):
    if mass <= 600:
        return 15
    elif mass <= 750:
        return 5
    elif mass <= 900:
        return 4
    else:
        return 3

