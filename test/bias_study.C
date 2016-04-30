#include "TFile.h"
#include "TH1F.h"
#include "TCanvas.h"
#include "TLegend.h"
#include "TSystem.h"
#include "TMath.h"

#include "RooRealVar.h"
#include "RooDataHist.h"
#include "RooBukinPdf.h"
#include "RooCBShape.h"
#include "RooExponential.h"
#include "RooFitResult.h"
#include "RooBernstein.h"
#include "RooPlot.h"
#include "RooGenericPdf.h"
#include "RooWorkspace.h"
#include "RooHistPdf.h"
#include "RooAbsPdf.h"
#include "RooAbsData.h"
#include "RooAddPdf.h"
#include "RooExtendPdf.h"

using namespace std;
using namespace RooFit;


int doFTest( TString formula="pol", RooRealVar* x=0, RooAbsData* data=0, TString saveDir="", TString saveAs=""){

  int order = -1;

  // Polynomial family: 1 + a1*x + a2*x*x + ...
  if(formula=="pol"){

    TCanvas* c1 = new TCanvas("c1_ftest_pol","c1",800,800);
    TLegend* leg = new TLegend(0.20,0.55,0.80,0.88, "","brNDC");
    leg->SetFillStyle(0);
    leg->SetBorderSize(0);
    leg->SetTextSize(0.05);
    leg->SetFillColor(10);
    leg->SetHeader("Bernstein polynomial");
    RooPlot* frame = x->frame();
    frame->SetName("frame_pol");
    frame->SetTitle("F-test");

    vector<TString> results;
    RooArgSet coeff;
    RooRealVar* a0 = new RooRealVar("a0", "", 1); a0->setConstant();
    RooRealVar* a1 = new RooRealVar("a1", "", -1., 1.);
    RooRealVar* a2 = new RooRealVar("a2", "", -1., 1.);
    RooRealVar* a3 = new RooRealVar("a3", "", -1., 1.);
    coeff.add( *a0 );
    coeff.add( *a1 );
    coeff.add( *a2 );
    coeff.add( *a3 );

    int firstOrder = coeff.getSize()-1;
    RooBernstein* pol = new RooBernstein(Form("pol_deg%d", firstOrder),"Polynomial for background", *x, coeff);
    double prevNll = (pol->fitTo(*data, PrintLevel(-1), PrintEvalErrors(0), Warnings(kFALSE), Save(kTRUE)))->minNll();
    results.push_back( TString(Form("Deg. %dth: OLD nll=%f, NEW nll=%f: chi2=%f, prob=%f", firstOrder, prevNll, prevNll, 0., 0. )) );    

    if(saveDir!=""){
      data->plotOn(frame, Name("data"));
      pol->plotOn(frame, Name(Form("pol_deg%d",firstOrder)), LineColor(1));
      double ch2 = frame->chiSquare( Form("pol_deg%d",firstOrder), "data" ,firstOrder-1);
      leg->AddEntry(frame->getCurve(Form("pol_deg%d",firstOrder)), Form("Deg. %dth, #chi^{2}=%.2f, p=%.3f", firstOrder, ch2, 0.), "L");
    }

    bool found = false;
    for(int i = 0; i < 4; ++i){
      RooRealVar* ai = new RooRealVar(Form("a%d",firstOrder+i+1), "", -1., 1.);
      coeff.add( *ai );
      int thisOrder = coeff.getSize()-1;
      // reset
      a1->setVal(0.);
      a2->setVal(0.);
      a3->setVal(0.);
      RooBernstein* poli = new RooBernstein(Form("pol_deg%d",thisOrder),"Polynomial for background", *x, coeff);
      RooFitResult* resi = poli->fitTo(*data, PrintLevel(-1), PrintEvalErrors(0), Warnings(kFALSE), Save(kTRUE));

      double thisNll = resi->minNll();
      double chi2 = 2.*( prevNll - thisNll );
      if( chi2<0. ) chi2=1e+3;
      float prob = TMath::Prob(chi2, 1);
      results.push_back( TString(Form("Deg. %dth: OLD nll=%f, NEW nll=%f: chi2=%f, prob=%f", thisOrder, prevNll, thisNll, chi2, prob )) );

      if( thisNll<prevNll ) prevNll = thisNll;
      if( prob > 0.05 && !found){
	order = thisOrder-1;
	found = true;
      }

      if(saveDir!=""){
	poli->plotOn(frame, Name(Form("pol_deg%d",thisOrder)), LineColor(i+2));
	double ch2 = frame->chiSquare( Form("pol_deg%d",thisOrder), "data" ,thisOrder-1);
	leg->AddEntry(frame->getCurve(Form("pol_deg%d",thisOrder)), Form("Deg. %dth, #chi^{2}=%.2f, p=%.3f", thisOrder, ch2, prob), "L");
      }

      delete poli;
    }

    // print results
    for(unsigned int r = 0 ; r < results.size(); ++r) cout << string(results[r].Data()) << endl;

    if(saveDir!=""){
      c1->cd();
      frame->Draw();
      leg->Draw();
      c1->SaveAs(saveDir+"/ftest_pol_"+saveAs+".png");
    }
    delete pol;
    delete c1;
    delete leg;
  }

  // Exponential family: e^{a0*x + a1*x*x + a2*x*x*x + ...}
  else if(formula=="exp"){

    TCanvas* c1 = new TCanvas("c1_ftest_exp","c1",800,800);
    TLegend* leg = new TLegend(0.20,0.55,0.80,0.88, "","brNDC");
    leg->SetFillStyle(0);
    leg->SetBorderSize(0);
    leg->SetTextSize(0.05);
    leg->SetFillColor(10);
    leg->SetHeader("Exponential family");
    RooPlot* frame = x->frame();
    frame->SetName("frame_exp");
    frame->SetTitle("F-test");

    vector<TString> results;
    RooArgSet coeff;
    RooRealVar* a0 = new RooRealVar("a0", "", -0.2, 0.);
    coeff.add(*x);
    coeff.add(*a0);

    // number of parameters (-1 needed because of 'x')
    int firstOrder = coeff.getSize()-1;
    RooGenericPdf* exp = new RooGenericPdf(Form("exp_deg%d",firstOrder),"TMath::Exp(x*a0)", coeff);    
    double prevNll = (exp->fitTo(*data, PrintLevel(-1), PrintEvalErrors(0), Warnings(kFALSE), Save(kTRUE)))->minNll();
    results.push_back( TString(Form("Deg. %dth: OLD nll=%f, NEW nll=%f: chi2=%f, prob=%f", firstOrder, prevNll, prevNll, 0., 0. )) );

    if(saveDir!=""){
      data->plotOn(frame, Name("data"));
      exp->plotOn(frame, Name(Form("exp_deg%d",firstOrder)), LineColor(1));
      double ch2 = frame->chiSquare( Form("exp_deg%d",firstOrder), "data" ,firstOrder);
      leg->AddEntry(frame->getCurve(Form("exp_deg%d",firstOrder)), Form("Deg. %dth, #chi^{2}=%.2f, p=%.3f", firstOrder, ch2, 0.), "L");
    }

    bool found = false;
    for(int i = 1; i < 5; ++i){
      RooRealVar* ai = new RooRealVar(Form("a%d",firstOrder-1+i), "", -2., 2.);
      coeff.add( *ai );
      int thisOrder = coeff.getSize()-1;
      TString formula = "TMath::Exp(a0*x)";
      switch(i){
      case 1:
	formula = "TMath::Exp(a0*x + a1*x*x)";
	break;
      case 2:
	formula = "TMath::Exp(a0*x + a1*x*x + a2*x*x*x)";
	break;
      case 3:
	formula = "TMath::Exp(a0*x + a1*x*x + a2*x*x*x + a3*x*x*x*x)";
	break;
      case 4:
	formula = "TMath::Exp(a0*x + a1*x*x + a2*x*x*x + a3*x*x*x*x + a4*x*x*x*x*x)";
	break;
      default: 
	break;
      }
      RooGenericPdf* expi = new RooGenericPdf(Form("exp_deg%d",firstOrder+i), formula , coeff);         
      RooFitResult* resi = expi->fitTo(*data, PrintLevel(-1), PrintEvalErrors(0), Warnings(kFALSE), Save(kTRUE));
      double thisNll = resi->minNll();
      double chi2 = 2.*( prevNll - thisNll );
      if( chi2<0. ) chi2=1e+3;
      float prob = TMath::Prob(chi2, 1);
      results.push_back( TString(Form("Deg. %dth: OLD nll=%f, NEW nll=%f: chi2=%f, prob=%f", thisOrder, prevNll, thisNll, chi2, prob )) );
      if( thisNll<prevNll ) prevNll = thisNll;
      if( prob > 0.05 && !found){
	order = thisOrder-1;
	found = true;
      }

      if(saveDir!=""){
	expi->plotOn(frame, Name(Form("exp_deg%d",thisOrder)), LineColor(i+1));
	double ch2 = frame->chiSquare( Form("exp_deg%d",thisOrder), "data" ,thisOrder);
	leg->AddEntry(frame->getCurve(Form("exp_deg%d",thisOrder)), Form("Deg. %dth, #chi^{2}=%.2f, p=%.3f", thisOrder, ch2, prob), "L");
      }

      delete expi;
    }
    // print results
    for(unsigned int r = 0 ; r < results.size(); ++r) cout << string(results[r].Data()) << endl;
    
    if(saveDir!=""){
      c1->cd();
      frame->Draw();
      leg->Draw();
      c1->SaveAs(saveDir+"/ftest_exp_"+saveAs+".png");
    }
    delete exp;
    delete c1;
    delete leg;
  } // end Exp

  // Power-law family: x^{a0 + a1*x + a2*x*x + ...}
  else if(formula=="pow"){

    TCanvas* c1 = new TCanvas("c1_ftest_pow","c1",800,800);
    TLegend* leg = new TLegend(0.20,0.55,0.80,0.88, "","brNDC");
    leg->SetFillStyle(0);
    leg->SetBorderSize(0);
    leg->SetTextSize(0.05);
    leg->SetFillColor(10);
    leg->SetHeader("Power law family");
    RooPlot* frame = x->frame();
    frame->SetName("frame_pow");
    frame->SetTitle("F-test");

    vector<TString> results;
    RooArgSet coeff;
    RooRealVar* a0 = new RooRealVar("a0", "", -10., 10.);
    coeff.add(*x);
    coeff.add(*a0);

    // number of parameters (-1 needed because of 'x')
    int firstOrder = coeff.getSize()-1;
    RooGenericPdf* pow = new RooGenericPdf(Form("pow_deg%d",firstOrder),"TMath::Power(x,a0)", coeff);    
    double prevNll = (pow->fitTo(*data, PrintLevel(-1), PrintEvalErrors(0), Warnings(kFALSE), Save(kTRUE)))->minNll();
    results.push_back( TString(Form("Deg. %dth: OLD nll=%f, NEW nll=%f: chi2=%f, prob=%f", firstOrder, prevNll, prevNll, 0., 0. )) );

    if(saveDir!=""){
      data->plotOn(frame, Name("data"));
      pow->plotOn(frame, Name(Form("pow_deg%d",firstOrder)), LineColor(1));
      double ch2 = frame->chiSquare( Form("pow_deg%d",firstOrder), "data" ,firstOrder);
      leg->AddEntry(frame->getCurve(Form("pow_deg%d",firstOrder)), Form("Deg. %dth, #chi^{2}=%.2f, p=%.3f", firstOrder, ch2, 0.), "L");
    }

    bool found = false;
    for(int i = 1; i < 4; ++i){
      RooRealVar* ai = new RooRealVar(Form("a%d",firstOrder-1+i), "", -10., 10.);
      coeff.add( *ai );
      int thisOrder = coeff.getSize()-1;
      TString formula = "TMath::Power(x,a0)";
      switch(i){
      case 1:
	formula = "TMath::Power(x, a0 + a1*x)";
	break;
      case 2:
	formula = "TMath::Power(x, a0 + a1*x + a2*x*x)";
	break;
      case 3:
	formula = "TMath::Power(x, a0 + a1*x + a2*x*x + a3*x*x*x)";
	break;
      default: 
	break;
      }
      RooGenericPdf* powi = new RooGenericPdf(Form("pow_deg%d",firstOrder+i), formula , coeff);         
      RooFitResult* resi = powi->fitTo(*data, PrintLevel(-1), PrintEvalErrors(0), Warnings(kFALSE), Save(kTRUE));
      double thisNll = resi->minNll();
      double chi2 = 2.*( prevNll - thisNll );
      if( chi2<0. ) chi2=1e+3;
      float prob = TMath::Prob(chi2, 1);
      results.push_back( TString(Form("Deg. %dth: OLD nll=%f, NEW nll=%f: chi2=%f, prob=%f", thisOrder, prevNll, thisNll, chi2, prob )) );
      if( thisNll<prevNll ) prevNll = thisNll;
      if( prob > 0.05 && !found){
	order = thisOrder-1;
	found = true;
      }

      if(saveDir!=""){
	powi->plotOn(frame, Name(Form("pow_deg%d",thisOrder)), LineColor(i+1));
	double ch2 = frame->chiSquare( Form("pow_deg%d",thisOrder), "data" ,thisOrder);
	leg->AddEntry(frame->getCurve(Form("pow_deg%d",thisOrder)), Form("Deg. %dth, #chi^{2}=%.2f, p=%.3f", thisOrder, ch2, prob), "L");
      }

      delete powi;
    }
    // print results
    for(unsigned int r = 0 ; r < results.size(); ++r) cout << string(results[r].Data()) << endl;
    
    if(saveDir!=""){
      c1->cd();
      frame->Draw();
      leg->Draw();
      c1->SaveAs(saveDir+"/ftest_pow_"+saveAs+".png");
    }
    delete pow;
    delete c1;
    delete leg;
  } // end Power

  // Poly*Exp family: {1 + a1*x + a2*x*x + ...}*e^(a0*x)
  else if(formula=="polyexp"){

    TCanvas* c1 = new TCanvas("c1_ftest_polyexp","c1",800,800);
    TLegend* leg = new TLegend(0.20,0.55,0.80,0.88, "","brNDC");
    leg->SetFillStyle(0);
    leg->SetBorderSize(0);
    leg->SetTextSize(0.05);
    leg->SetFillColor(10);
    leg->SetHeader("Polynomial*Exp family");
    RooPlot* frame = x->frame();
    frame->SetName("frame_polyexp");
    frame->SetTitle("F-test");

    vector<TString> results;
    RooArgSet coeff;
    RooRealVar* a0 = new RooRealVar("a0", "", -0.2, 0.);
    coeff.add(*x);
    coeff.add(*a0);

    // number of parameters (-1 needed because of 'x')
    int firstOrder = coeff.getSize()-1;
    RooGenericPdf* polyexp = new RooGenericPdf(Form("polyexp_deg%d",firstOrder),"TMath::Exp(x*a0)", coeff);    
    double prevNll = (polyexp->fitTo(*data, PrintLevel(-1), PrintEvalErrors(0), Warnings(kFALSE), Save(kTRUE)))->minNll();
    results.push_back( TString(Form("Deg. %dth: OLD nll=%f, NEW nll=%f: chi2=%f, prob=%f", firstOrder, prevNll, prevNll, 0., 0. )) );

    if(saveDir!=""){
      data->plotOn(frame, Name("data"));
      polyexp->plotOn(frame, Name(Form("polyexp_deg%d",firstOrder)), LineColor(1));
      double ch2 = frame->chiSquare( Form("polyexp_deg%d",firstOrder), "data" ,firstOrder);
      leg->AddEntry(frame->getCurve(Form("polyexp_deg%d",firstOrder)), Form("Deg. %dth, #chi^{2}=%.2f, p=%.3f", firstOrder, ch2, 0.), "L");
    }

    bool found = false;
    for(int i = 1; i < 5; ++i){
      RooRealVar* ai = new RooRealVar(Form("a%d",firstOrder-1+i), "", -10., 10.);
      coeff.add( *ai );
      int thisOrder = coeff.getSize()-1;
      TString formula = "TMath::Exp(x*a0)";
      switch(i){
      case 1:
	formula = "TMath::Max(1e-50,(1 + a1*x)*TMath::Exp(x*a0))";
	break;
      case 2:
	formula = "TMath::Max(1e-50,(1 + a1*x + a2*x*x)*TMath::Exp(x*a0))";
	break;
      case 3:
	formula = "TMath::Max(1e-50,(1 + a1*x + a2*x*x + a3*x*x*x)*TMath::Exp(x*a0))";
	break;
      case 4:
	formula = "TMath::Max(1e-50,(1 + a1*x + a2*x*x + a3*x*x*x + a4*x*x*x*x)*TMath::Exp(x*a0))";
	break;
      default: 
	break;
      }
      RooGenericPdf* polyexpi = new RooGenericPdf(Form("polyexp_deg%d",firstOrder+i), formula , coeff);         
      RooFitResult* resi = polyexpi->fitTo(*data, PrintLevel(-1), PrintEvalErrors(0), Warnings(kFALSE), Save(kTRUE));
      double thisNll = resi->minNll();
      double chi2 = 2.*( prevNll - thisNll );
      if( chi2<0. ) chi2=1e+3;
      float prob = TMath::Prob(chi2, 1);
      results.push_back( TString(Form("Deg. %dth: OLD nll=%f, NEW nll=%f: chi2=%f, prob=%f", thisOrder, prevNll, thisNll, chi2, prob )) );
      if( thisNll<prevNll ) prevNll = thisNll;
      if( prob > 0.05 && !found){
	order = thisOrder-1;
	found = true;
      }

      if(saveDir!=""){
	polyexpi->plotOn(frame, Name(Form("polyexp_deg%d",thisOrder)), LineColor(i+1));
	double ch2 = frame->chiSquare( Form("polyexp_deg%d",thisOrder), "data" ,thisOrder);
	leg->AddEntry(frame->getCurve(Form("polyexp_deg%d",thisOrder)), Form("Deg. %dth, #chi^{2}=%.2f, p=%.3f", thisOrder, ch2, prob), "L");
      }

      delete polyexpi;
    }
    // print results
    for(unsigned int r = 0 ; r < results.size(); ++r) cout << string(results[r].Data()) << endl;
    
    if(saveDir!=""){
      c1->cd();
      frame->Draw();
      leg->Draw();
      c1->SaveAs(saveDir+"/ftest_polyexp_"+saveAs+".png");
    }
    delete polyexp;
    delete c1;
    delete leg;
  } // end Poly*Exp
  
  else{
    /* ... */
  }

  return order;
}


void doFTests(TString input_fname="plots/V2/plot.root",
	      TString h_name_bkg = "background_Had_LT_MinPt150_DH1p6_MassFSR",
	      float x_min = 540.,
	      float x_max = 1200.,
	      int rebin_factor = 1,
	      TString saveDir = "plots/V2/"
	      ){

  // the fitting variable
  RooRealVar x("x","x", 400., 4000.);
  x.setMin(x_min);
  x.setMax(x_max);

  TFile* input_file = TFile::Open(input_fname, "READ");
  if(input_file==0 || input_file->IsZombie()){
    cout << "File " << string(input_fname.Data()) << " could not be found." << endl;
    return;
  }
  
  TH1F* h_bkg = (TH1F*)input_file->Get(h_name_bkg);
  if( h_bkg==0 ){
    cout << "No background histogram!" << endl;
    input_file->Close();
    return;
  }
  
  // optionally rebin the histogram before making the RooDataHist
  if(rebin_factor>1) h_bkg->Rebin(rebin_factor);

  // the signal data set
  RooDataHist* data_bkg = new RooDataHist("data_bkg", "data background", x, h_bkg);

  vector<TString> formulas = {"pol" ,"exp", "pow", "polyexp"};

  for(unsigned int f = 0 ; f < formulas.size() ; ++f){
    int order = doFTest(formulas[f], &x, data_bkg, saveDir, h_name_bkg);
    cout << string(formulas[f].Data()) << " has found order " << order << endl;
  }

  input_file->Close();  
  return;
}




void bias_study( TString fname = "./plots/V2/Xbb_workspace_Had_LT_MinPt150_DH1p6_MassFSR_550to1200.root",
		 TString ws_name="Xbb_workspace",
		 TString nominal_bkg_model = "mass_pdf_bkg",
		 TString nominal_sgn_model = "buk_pdf_sgn",
		 int ntoys=1,
		 float sgn_xsec_fact = 1.0
		 ){

  TFile* file = TFile::Open(fname,"READ");
  if( file==0 || file->IsZombie()){
    cout << "No file!" << endl;
    return;
  }

  RooWorkspace *w = (RooWorkspace*)file->Get(ws_name);
  if(w==0){
    cout << "No workspace found!" << endl;
    file->Close();
    return;
  }

  // the variable
  RooRealVar* x = w->var("x");
  // the background data set
  RooDataHist* data_bkg = (RooDataHist*)w->data("data_bkg");
  double xmin, xmax;
  data_bkg->getRange(*x, xmin, xmax);
  double binVolume = data_bkg->binVolume(*x);
  xmin -= binVolume/2;
  xmax += binVolume/2;
  x->setMin( xmin );
  x->setMax( xmax );
  x->setBins( int(xmax-xmin)/binVolume );
  cout << string(Form("[%.0f, %.0f], bins=%d",x->getMin(),x->getMax(),x->getBins())) << endl;

  // The Nominal bkg pdf
  RooAbsPdf* pdf_bkg_nominal = w->pdf(nominal_bkg_model);
  RooRealVar* n_bkg_nominal = w->var(nominal_bkg_model+"_norm");
  cout << "Total background: " << n_bkg_nominal->getVal() << endl;
  RooAbsPdf* pdf_bkg_nominal_fit = 0;
  RooRealVar p1("p1","p1", w->var("p1_bkg")->getVal(), 0.0, 20.);
  RooRealVar p2("p2","p2", w->var("p2_bkg")->getVal(), 10., 40.);
  RooRealVar p3("p3","p3", w->var("p3_bkg")->getVal(), 0.5, 5.0);
  TString mass_formula = "TMath::Power(1-x/13000.,p1)/(TMath::Power(x/13000.,p2+p3*TMath::Log(x/13000.)))";
  pdf_bkg_nominal_fit = new RooGenericPdf("pdf_bkg_nominal_fit", mass_formula, RooArgSet(*x,p1,p2,p3));
  cout << "Nominal background pdf created! (RooGenericPdf)" << endl;

  // the nominal sgn pdf
  RooAbsPdf* pdf_sgn_nominal = w->pdf(nominal_sgn_model);
  RooRealVar* n_sgn_nominal = w->var(nominal_sgn_model+"_norm");
  cout << "Total signal: " << n_sgn_nominal->getVal() << endl;
  n_sgn_nominal->setVal(n_sgn_nominal->getVal()*sgn_xsec_fact);
  RooAbsPdf* pdf_sgn_nominal_fit = 0;
  RooRealVar Xp("Xp", "Xp", w->var("Xp_sgn")->getVal(), 650.,850.);
  RooRealVar sP("sP", "sP", w->var("sP_sgn")->getVal(),50., 150.);
  RooRealVar xi("xi", "xi", w->var("xi_sgn")->getVal(),-2.,0.);
  RooRealVar rho1("rho1", "rho1", w->var("rho1_sgn")->getVal(),-0.2,0.2);
  RooRealVar rho2("rho2", "rho2", w->var("rho2_sgn")->getVal(),-1.,1.);
  Xp.setConstant();
  sP.setConstant();
  xi.setConstant();
  rho1.setConstant();
  rho2.setConstant();
  pdf_sgn_nominal_fit = new RooBukinPdf("pdf_sgn_nominal_fit","", *x, Xp, sP, xi, rho1, rho2);
  cout << "Nominal signal pdf created! (RooBukinPdf)" << endl;


  // alternative models
  vector<TString> formulas = {"mass"
			      //,"pol" ,"exp", "pow", "polyexp"
  };
  
  // start formulas loops
  for(unsigned int f = 0 ; f < formulas.size() ; ++f){
    
    TString formula = formulas[f];

    // this is to choose the alternative bkg model to generate toys
    RooAbsPdf* pdf_bkg_alternative = 0;

    // NOMINAL
    if(formula=="mass"){
      pdf_bkg_alternative = pdf_bkg_nominal;
    }

    // POLYNOM
    else if(formula=="pol"){

      RooArgSet coeff;
      RooRealVar* a0 = new RooRealVar("a0", "", 1); a0->setConstant();
      RooRealVar* a1 = new RooRealVar("a1", "", -1., 1.);
      RooRealVar* a2 = new RooRealVar("a2", "", -1., 1.);
      RooRealVar* a3 = new RooRealVar("a3", "", -1., 1.);
      RooRealVar* a4 = new RooRealVar("a4", "", -1., 1.);
      RooRealVar* a5 = new RooRealVar("a5", "", -1., 1.);
      coeff.add( *a0 );
      coeff.add( *a1 );
      coeff.add( *a2 );
      coeff.add( *a3 );
      coeff.add( *a4 );
      coeff.add( *a5 );
      
      pdf_bkg_alternative = new RooBernstein( "pol_deg5" ,"Polynomial for background", *x, coeff);
      pdf_bkg_alternative->fitTo(*data_bkg, PrintLevel(-1), PrintEvalErrors(0), Warnings(kFALSE), Save(kTRUE));
    }
    else if( formula=="" ){
      /* ... */
    }    
    if( pdf_bkg_alternative==0) continue;

    // Build the alternative model: Ns and Nb fixed to original values
    RooExtendPdf pdf_sgn_model_alternative("pdf_sgn_model_alternative", "", *pdf_sgn_nominal, *n_sgn_nominal);
    RooExtendPdf pdf_bkg_model_alternative("pdf_bkg_model_alternative", "", *pdf_bkg_alternative, *n_bkg_nominal);
    RooAddPdf model_alternative("model_alternative","", RooArgList(pdf_sgn_model_alternative,pdf_bkg_model_alternative) ) ;

    // Build the nominal fit model
    RooRealVar n_bkg_fit("n_bkg_fit","", n_bkg_nominal->getVal(),  1000., 1000000.);
    RooRealVar n_sgn_fit("n_sgn_fit","", n_sgn_nominal->getVal(), -10000., 10000.);
    RooAddPdf model_fit("model_fit","", RooArgList(*pdf_sgn_nominal_fit, *pdf_bkg_nominal_fit), RooArgList(n_sgn_fit,n_bkg_fit)) ;

    // start toys
    int toy = 0;
    while(toy<ntoys){
      cout << "Generate toy n. " << toy << endl;      
      RooDataHist *data_toy = model_alternative.generateBinned(*x, Extended()) ;
      cout << "\tNumber of entries: " << data_toy->sumEntries() << endl;
      RooFitResult* res = model_fit.fitTo(*data_toy, PrintLevel(-1), PrintEvalErrors(0), Warnings(kFALSE), Save(kTRUE));
      if(res->status()!=0) continue;     
      float ns_gen = n_sgn_nominal->getVal();
      float ns_fit = n_sgn_fit.getVal();
      float ns_err = n_sgn_fit.getError();
      cout << string(Form("Ns(fit): %f +/- %f, Ns(gen): %f", ns_fit, ns_err, ns_gen)) << endl;
      ++toy;
    } // end toys

  } // end formulas


  /////////////
  file->Close();
  return;
}
