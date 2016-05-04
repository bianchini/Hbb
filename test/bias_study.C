#include "TFile.h"
#include "TTree.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TCanvas.h"
#include "TObject.h"
#include "TLegend.h"
#include "TSystem.h"
#include "TMath.h"

#include "RooRealVar.h"
#include "RooDataHist.h"
#include "RooDataSet.h"
#include "RooBukinPdf.h"
#include "RooCBShape.h"
#include "RooExponential.h"
#include "RooFitResult.h"
#include "RooGaussian.h"
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

#define SAVE true
#define MINUIT_STRATEGY 2

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




void bias_study(TString ws_name="Xbb_workspace", 
		TString path = "./plots/V2/", 
		TString fname = "Had_LT_MinPt150_DH1p6_MassFSR_550to1200",
		TString nominal_sgn_model = "buk",
		TString nominal_bkg_model = "mass",
		TString alternative_bkg_model = "mass",
		float sgn_xsec = 1.0,
		int ntoys = 10,
		float xMin = -1.,
		float xMax = -1.
		){

  TFile* out = TFile::Open(path+"/bias_study_"+fname+"_Nom-"+nominal_bkg_model+"_Alt-"+alternative_bkg_model+"_xSec"+TString(Form("%.0f",sgn_xsec))+"_Range"+TString(Form("%.0fto%.0f",xMin,xMax))+".root","RECREATE");
  TTree* tree = new TTree("toys","");
  float ns_gen, ns_fit, ns_err, nb_gen, nb_fit, nb_err, xsec, xL, xH;
  float param[8];
  int nf, nt;
  tree->Branch("ns_gen", &ns_gen, "ns_gen/F");
  tree->Branch("ns_fit", &ns_fit, "ns_fit/F");
  tree->Branch("ns_err", &ns_err, "ns_err/F");
  tree->Branch("nb_gen", &nb_gen, "nb_gen/F");
  tree->Branch("nb_fit", &nb_fit, "nb_fit/F");
  tree->Branch("nb_err", &nb_err, "nb_err/F");
  tree->Branch("xsec", &xsec, "xsec/F");
  tree->Branch("nf", &nf, "nf/I");
  tree->Branch("toy", &nt, "nt/I");
  tree->Branch("param", param, "param[8]/F");
  tree->Branch("xmin", &xL, "xmin/F"); 
  tree->Branch("xmax", &xH, "xmax/F"); 
  

  TFile* file = TFile::Open(path+"/"+ws_name+"_"+fname+".root","READ");
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
  RooDataHist* data_bkg = (RooDataHist*)w->data("data_obs");
  double xmin, xmax;
  data_bkg->getRange(*x, xmin, xmax);
  double binVolume = data_bkg->binVolume(*x);
  xmin -= binVolume/2;
  xmax += binVolume/2;
  if( xMin>=0. & xMax>xMin ){
    xmin = xMin;
    xmax = xMax;
  }
  xL = xmin;
  xH = xmax;
  x->setMin( xmin );
  x->setMax( xmax );
  x->setBins( int(xmax-xmin)/binVolume );
  x->setRange("ref", xmin, xmax);
  cout << string(Form("[%.0f, %.0f], bins=%d",x->getMin(),x->getMax(),x->getBins())) << endl;

  // the nominal bkg pdf
  RooRealVar* n_bkg_nominal = new RooRealVar("n_bkg_nominal", "", w->data("data_obs")->sumEntries(0, "ref"));
  cout << "Total background: " << n_bkg_nominal->getVal() << endl;

  // container for fit parameters
  RooArgSet fit_param;
  map<TString, double> reset_values;
  RooAbsPdf* pdf_bkg_nominal_fit = 0;

  // NOMINAL
  if(nominal_bkg_model=="mass"){
    fit_param.add(*x);
    for(int i = 0; i < 3; ++i){
      RooRealVar* pi = 0;
      if(i==0){
	pi = new RooRealVar(Form("p%d",i), "", 0., 10.);
	pi->setVal(.0);
	pi->setConstant();
      }
      else if(i==1) pi = new RooRealVar(Form("p%d",i), "",  0., 50.);
      else pi = new RooRealVar(Form("p%d",i), "", -5., 5.);
      fit_param.add( *pi );
    }
    double sqrts = 1.3e+04;
    TString mass_formula(Form("TMath::Max(1e-50,TMath::Power(1-x/%E,p0)/(TMath::Power(x/%E,p1+p2*TMath::Log(x/%E))))", sqrts, sqrts, sqrts));
    pdf_bkg_nominal_fit = new RooGenericPdf("pdf_bkg_nominal_fit", mass_formula, fit_param);
    cout << "Nominal background pdf created! (RooGenericPdf)" << endl;
  }

  // POLYNOMIAL
  else if(nominal_bkg_model=="pol"){
    for(int i = 0; i < 6; ++i){
      RooRealVar* pi = new RooRealVar(Form("p%d",i), "", -1., 1.);
      if(i==0){
	pi->setVal(1.0);
	pi->setConstant();
      }
      fit_param.add( *pi );
    }
    pdf_bkg_nominal_fit = new RooBernstein( "pdf_bkg_nominal_fit" ,"Polynomial for background", *x, fit_param);
    cout << "Nominal background pdf created! (RooBernstein)" << endl;
  }

  // EXPONENTIAL OF POLYNOM
  else if( nominal_bkg_model=="exp" ){
    fit_param.add(*x);
    for(int i = 0; i < 4; ++i){
      RooRealVar* pi = 0;
      if(i==0) pi = new RooRealVar(Form("p%d",i), "", -300., 0.);
      else if(i<3) pi = new RooRealVar(Form("p%d",i), "", 0., 1000.);
      else pi = new RooRealVar(Form("p%d",i), "", -100., 100.);
      fit_param.add( *pi );
    }	
    double sqrts = 1.3e+04;
    TString formula_exp(Form("TMath::Exp(p0*x/%E + p1*x*x/%E + p2*x*x*x/%E + p3*x*x*x*x/%E)", TMath::Power(sqrts,1), TMath::Power(sqrts,2), TMath::Power(sqrts,3), TMath::Power(sqrts,3)));
    pdf_bkg_nominal_fit = new RooGenericPdf("pdf_bkg_nominal_fit", formula_exp , fit_param);
    cout << "Nominal background pdf created! (RooGenericPdf)" << endl;
  }    

  // POWER LAW
  else if( nominal_bkg_model=="pow" ){
    fit_param.add(*x);
    for(int i = 0; i < 3; ++i){
      RooRealVar* pi = 0;
      if(i==0) pi = new RooRealVar(Form("p%d",i), "", 0., 100.);
      else if(i==1) pi = new RooRealVar(Form("p%d",i), "", 0., 200.);
      else pi = new RooRealVar(Form("p%d",i), "", -1000., 0.);
      fit_param.add( *pi );
    }	
    double sqrts = 1.3e+04;
    TString formula_pow(Form("TMath::Power(x/%E, p0 + p1*x/%E + p2*x*x/%E)", TMath::Power(sqrts,1), TMath::Power(sqrts,1), TMath::Power(sqrts,2)));
    pdf_bkg_nominal_fit = new RooGenericPdf("pdf_bkg_nominal_fit", formula_pow , fit_param); 
    cout << "Nominal background pdf created! (RooGenericPdf)" << endl;
  }    

  // EXPONENTIAL * POLYNOM
  else if( nominal_bkg_model=="polyexp" ){
    fit_param.add(*x);
    for(int i = 0; i < 3; ++i){
      RooRealVar* pi = 0;
      if(i==0) pi = new RooRealVar(Form("p%d",i), "", -200, 0.);
      else if(i==1) pi = new RooRealVar(Form("p%d",i), "", -100, 100.);
      else pi = new RooRealVar(Form("p%d",i), "", 0., 1000);
      fit_param.add( *pi );
    }	
    double sqrts = 1.3e+04;
    TString formula_polyexp(Form("TMath::Max(1e-50,(1 + p1*x/%E + p2*x*x/%E)*TMath::Exp(x/%E*p0))", TMath::Power(sqrts,1), TMath::Power(sqrts,2), TMath::Power(sqrts,1)));
    pdf_bkg_nominal_fit = new RooGenericPdf("pdf_bkg_nominal_fit", formula_polyexp , fit_param);
    cout << "Nominal background pdf created! (RooGenericPdf)" << endl;
  }    

  // ANYTHING ELSE 
  else { /*...*/ }


  if(pdf_bkg_nominal_fit==0){
    cout << "No pdf_bkg_nominal_fit! Return" << endl;
    file->Close();
    return;
  }   

  
  // the nominal sgn pdf
  RooAbsPdf* pdf_sgn_nominal = w->pdf(nominal_sgn_model+"_pdf_sgn");
  RooRealVar* n_sgn_nominal = new RooRealVar("n_sgn_nominal", "", w->data("data_sgn")->sumEntries(0, "ref") );
  //RooAbsReal* n_sgn_nominal = pdf_sgn_nominal->createIntegral(*x,*x,"ref");
  float n_sgn_nominal_input = n_sgn_nominal->getVal();
  cout << "Total signal: " << n_sgn_nominal_input << endl;
  RooAbsPdf* pdf_sgn_nominal_fit = 0;
  RooRealVar Xp("Xp", "Xp", w->var("Xp_sgn")->getVal());
  RooRealVar sP("sP", "sP", w->var("sP_sgn")->getVal());
  RooRealVar xi("xi", "xi", w->var("xi_sgn")->getVal());
  RooRealVar rho1("rho1", "rho1", w->var("rho1_sgn")->getVal());
  RooRealVar rho2("rho2", "rho2", w->var("rho2_sgn")->getVal());
  Xp.setConstant();
  sP.setConstant();
  xi.setConstant();
  rho1.setConstant();
  rho2.setConstant();
  pdf_sgn_nominal_fit = new RooBukinPdf("pdf_sgn_nominal_fit","", *x, Xp, sP, xi, rho1, rho2);
  //pdf_sgn_nominal_fit = new RooGaussian("pdf_sgn_nominal_fit", "", *x, Xp, sP);
  //pdf_sgn_nominal_fit = w->pdf("hist_pdf_sgn");
  cout << "Nominal signal pdf created! (RooBukinPdf)" << endl;


  // alternative models
  vector<TString> formulas = { alternative_bkg_model };

  // vary cross section for linearity check
  vector<float> sgn_xsec_facts = { sgn_xsec };
  
  // start formulas loops
  for(unsigned int xs = 0 ; xs < sgn_xsec_facts.size() ; ++xs){

    // update signal cross section
    float sgn_xsec_fact = sgn_xsec_facts[xs];
    n_sgn_nominal->setVal(n_sgn_nominal_input*sgn_xsec_fact);
    xsec = sgn_xsec_fact;

    // start formulas loops
    for(unsigned int f = 0 ; f < formulas.size() ; ++f){   
      TString formula = formulas[f];

      // this is to choose the alternative bkg model to generate toys
      RooAbsPdf* pdf_bkg_alternative = 0;
      nf = 0;

      // NOMINAL
      if(formula=="mass"){
	RooArgSet coeff;
	coeff.add(*x);
 	for(int i = 0; i < 3; ++i){
	  RooRealVar* ai = 0;
	  if(i==0){
	    ai = new RooRealVar(Form("a%d",i), "", 0., 10.);
	    ai->setVal(0.);
	    ai->setConstant();
	  }
	  else if(i==1) ai = new RooRealVar(Form("a%d",i), "", 0., 50.);
	  else ai = new RooRealVar(Form("a%d",i), "", -5., 5.);
	  coeff.add( *ai );
	}	
	double sqrts = 1.3e+04;
	TString formula_mass(Form("TMath::Max(1e-50,TMath::Power(1-x/%E,a0)/(TMath::Power(x/%E,a1+a2*TMath::Log(x/%E))))", sqrts, sqrts, sqrts ));
	pdf_bkg_alternative = new RooGenericPdf("mass_deg3", formula_mass , coeff);
	nf = 0;
      }

      // POLYNOMIAL
      else if(formula=="pol"){
	RooArgSet coeff;
	for(int i = 0; i < 6; ++i){
	  RooRealVar* ai = new RooRealVar(Form("a%d",i), "", -1., 1.);
	  if(i==0){
	    ai->setVal(1.0);
	    ai->setConstant();
	  }
	  coeff.add( *ai );
	}
	pdf_bkg_alternative = new RooBernstein( "pol_deg5" ,"Polynomial for background", *x, coeff);
	nf = 1;
      }

      // EXPONENTIAL OF POLYNOM
      else if( formula=="exp" ){
	RooArgSet coeff;
	coeff.add(*x);
 	for(int i = 0; i < 4; ++i){
	  RooRealVar* ai = 0;
	  if(i==0) ai = new RooRealVar(Form("a%d",i), "", -300., 0.);
	  else if(i<3) ai = new RooRealVar(Form("a%d",i), "", 0., 1000.);
	  else ai = new RooRealVar(Form("a%d",i), "", -100., 100.);
	  coeff.add( *ai );
	}	
	double sqrts = 1.3e+04;
	TString formula_exp(Form("TMath::Exp(a0*x/%E + a1*x*x/%E + a2*x*x*x/%E + a3*x*x*x*x/%E)", TMath::Power(sqrts,1), TMath::Power(sqrts,2), TMath::Power(sqrts,3), TMath::Power(sqrts,3)));
	pdf_bkg_alternative = new RooGenericPdf("exp_deg4", formula_exp , coeff);
	nf = 2;
      }    

      // POWER LAW
      else if( formula=="pow" ){
	RooArgSet coeff;
	coeff.add(*x);
 	for(int i = 0; i < 3; ++i){
	  RooRealVar* ai = 0;
	  if(i==0) ai = new RooRealVar(Form("a%d",i), "", 0., 100.);
	  else if(i==1) ai = new RooRealVar(Form("a%d",i), "", 0., 200.);
	  else ai = new RooRealVar(Form("a%d",i), "", -1000., 0.);
	  coeff.add( *ai );
	}	
	double sqrts = 1.3e+04;
	TString formula_pow(Form("TMath::Power(x/%E, a0 + a1*x/%E + a2*x*x/%E)", TMath::Power(sqrts,1), TMath::Power(sqrts,1), TMath::Power(sqrts,2)));
	pdf_bkg_alternative = new RooGenericPdf("pow_deg3", formula_pow , coeff); 
	nf = 3;
      }    

      // EXPONENTIAL * POLYNOM
      else if( formula=="polyexp" ){
	RooArgSet coeff;
	coeff.add(*x);
 	for(int i = 0; i < 3; ++i){
	  RooRealVar* ai = 0;
	  if(i==0) ai = new RooRealVar(Form("a%d",i), "", -200, 0.);
	  else if(i==1) ai = new RooRealVar(Form("a%d",i), "", -100, 100.);
	  else ai = new RooRealVar(Form("a%d",i), "", 0., 1000);
	  coeff.add( *ai );
	}	
	double sqrts = 1.3e+04;
	TString formula_polyexp(Form("TMath::Max(1e-50,(1 + a1*x/%E + a2*x*x/%E)*TMath::Exp(x/%E*a0))", TMath::Power(sqrts,1), TMath::Power(sqrts,2), TMath::Power(sqrts,1)));
	pdf_bkg_alternative = new RooGenericPdf("polyexp_deg3", formula_polyexp , coeff);
	nf = 4;
      }    

      // ANY...
      else if( formula=="" ){
	/* ... */
      }    

      // sanity check!
      if( pdf_bkg_alternative==0) continue;

      // fit alternative model to data!
      RooFitResult* res_alt = pdf_bkg_alternative->fitTo(*data_bkg, Strategy(1), Minimizer("Minuit2"), PrintLevel(-1), PrintEvalErrors(0), Warnings(kFALSE), Save(kTRUE), Range("ref"), SumCoefRange("ref"));

      // fit nominal model to data!
       RooFitResult* res_nom = pdf_bkg_nominal_fit->fitTo(*data_bkg, Strategy(1), Minimizer("Minuit2"), PrintLevel(-1), PrintEvalErrors(0), Warnings(kFALSE), Save(kTRUE), Range("ref"), SumCoefRange("ref"));

      for(unsigned int par = 0 ; par<8 ; ++par){
	if( fit_param.find(Form("p%d",par)) )
	  reset_values[ TString(Form("p%d",par)) ] = ((RooRealVar*)fit_param.find(Form("p%d",par)))->getVal();
	else reset_values[ TString(Form("p%d",par)) ] = 0.0;
	cout << string(Form("Reset value for p%d = %f",par, (reset_values.find(TString(Form("p%d",par))))->second )) << endl;
      }
      

      if(SAVE || true){
	RooPlot* frame = x->frame();
	frame->SetTitle(formula+" vs "+nominal_bkg_model);
	data_bkg->plotOn(frame);
	pdf_bkg_alternative->plotOn(frame, LineStyle(kSolid), LineColor(kRed));
	pdf_bkg_nominal_fit->plotOn(frame, LineStyle(kSolid), LineColor(kBlue), VisualizeError(*res_nom, 1, kFALSE) );
	frame->Draw();
	out->cd();
	frame->Write(Form("fit_%s_vs_%s", nominal_bkg_model.Data(), formula.Data()), TObject::kOverwrite);
      }

      // Build the alternative model: Ns and Nb fixed to original values
      if( sgn_xsec_fact <= 0.) n_sgn_nominal->setVal( 1e-03 );
      RooExtendPdf pdf_sgn_model_alternative("pdf_sgn_model_alternative", "", *pdf_sgn_nominal, *n_sgn_nominal);
      RooExtendPdf pdf_bkg_model_alternative("pdf_bkg_model_alternative", "", *pdf_bkg_alternative, *n_bkg_nominal);
      RooArgList model_components;
      model_components.add( pdf_bkg_model_alternative );
      model_components.add( pdf_sgn_model_alternative );
      RooAddPdf model_alternative("model_alternative","", model_components ) ;
      
      // Build the nominal fit model
      double nbkg = n_bkg_nominal->getVal();
      double nbkge = TMath::Sqrt(nbkg);
      RooRealVar n_bkg_fit("n_bkg_fit","", nbkg, nbkg - 10*nbkge , nbkg + 10*nbkge);
      RooRealVar n_sgn_fit("n_sgn_fit","", n_sgn_nominal->getVal(), -5000., 5000.);
      RooAddPdf model_fit("model_fit","", RooArgList(*pdf_sgn_nominal_fit, *pdf_bkg_nominal_fit), RooArgList(n_sgn_fit,n_bkg_fit)) ;
      
      // start toys
      int toy = 0;
      while(toy<ntoys){
	cout << "Generate toy n. " << toy << endl;    
	nt = toy;

	// reset
	n_bkg_fit.setVal( n_bkg_nominal->getVal() );
	n_sgn_fit.setVal( n_sgn_nominal->getVal() );
	for(unsigned int par = 0 ; par<8 ; ++par){
	  if( !fit_param.find(Form("p%d",par)) ) continue;
	  double reset_val = (reset_values.find(TString(Form("p%d",par))))->second;
	  ((RooRealVar*)fit_param.find(Form("p%d",par)))->setVal( reset_val );
	  cout << string(Form("Reset value for p%d = %f",par, reset_val )) << endl;
	}

	RooDataSet *data_toy = pdf_bkg_model_alternative.generate(*x, Extended()) ;
	cout << "\tNumber of background toys: " << data_toy->sumEntries() << endl;
	RooDataSet *data_sgn_toy = 0;
	if(sgn_xsec_fact>0.){ 
	  data_sgn_toy = pdf_sgn_model_alternative.generate(*x, Extended()) ;
	  data_toy->append(*data_sgn_toy);
	  cout << "\tNumber of signal toys: " << data_sgn_toy->sumEntries() << endl;
	}
	cout << "\tTotal number of entries in toy n. " << toy << ": " << data_toy->sumEntries() << endl;

	// binned!
	x->setBins( int((x->getMax()-x->getMin())/0.100) );
	RooDataHist data("data", "", *x, *data_toy);
	cout << "\tToy dataset has " << data.numEntries() << " bins" << endl;

	// fit to toy dataset
	RooFitResult* res = model_fit.fitTo(data, Strategy(MINUIT_STRATEGY), Minos(1), Minimizer("Minuit2"), PrintLevel(-1), PrintEvalErrors(0), Warnings(kFALSE), Save(kTRUE));
	if(res==0 || res->status()!=0){
	  cout << "No valid status" << endl;
	  continue;     
	}

	// save toy variables into the tree
	ns_gen = data_sgn_toy!=0 ? data_sgn_toy->sumEntries() : 0.0; 
	nb_gen = data_toy->sumEntries() - ns_gen; 

	ns_fit = n_sgn_fit.getVal();
	ns_err = n_sgn_fit.getError();
	nb_fit = n_bkg_fit.getVal();
	nb_err = n_bkg_fit.getError();

	for(unsigned int par = 0 ; par<8 ; ++par){
	  if( fit_param.find(Form("p%d",par)) )
	    param[par] = ((RooRealVar*)fit_param.find(Form("p%d",par)))->getVal(); 
	  else
	    param[par] = 0.0;
	}

	cout << string(Form("Ns(fit): %f +/- %f, Ns(gen): %f", ns_fit, ns_err, ns_gen)) << endl;
	tree->Fill();

	if(SAVE && toy<10){
	  RooPlot* frame = x->frame(Name(Form("toy%d",toy)));
	  data.plotOn(frame);
	  model_alternative.plotOn(frame, Components(pdf_bkg_model_alternative), LineStyle(kDashed), LineColor(kRed));
	  model_fit.plotOn(frame, Components(*pdf_bkg_nominal_fit), LineStyle(kSolid), LineColor(kRed));
	  if(sgn_xsec_fact>0.){
	    model_alternative.plotOn(frame, Components(pdf_sgn_model_alternative), LineStyle(kDashed), LineColor(kBlue));
	    cout << "Plotting signal nominal" << sgn_xsec_fact << endl;
	  }
	  model_fit.plotOn(frame, Components(*pdf_sgn_nominal_fit), LineStyle(kSolid), LineColor(kBlue));
	  frame->Draw();
	  out->cd();
	  frame->Write(Form("toy_%s_xsec%d_toy%d",formula.Data(), xs, toy), TObject::kOverwrite);
	}

	++toy;
      } // end toys      

      delete pdf_bkg_alternative;
    } // end formulas
  } // end factors

  /////////////
  out->cd();
  tree->Write("", TObject::kOverwrite);
  out->Close();
  /////////////
  file->Close();

  cout << "Delete vars..." << endl;
  delete n_bkg_nominal;
  delete n_sgn_nominal;
  cout << "Delete fits..." << endl;
  delete pdf_sgn_nominal_fit;
  delete pdf_bkg_nominal_fit;

  return;
}

//  LocalWords:  TMath


void plot_bias(){

  TCanvas* c1 = new TCanvas("c1_ftest_pol","c1",800,800);
  c1->SetGridx();
  c1->SetGridy();
  TLegend* leg = new TLegend(0.1,0.5,0.4,0.85, "","brNDC");
  leg->SetFillStyle(0);
  leg->SetBorderSize(0);
  leg->SetTextSize(0.03);
  leg->SetFillColor(10);
    
  vector<TString> files = { 
    "540to1200_Nom-mass",
    "550to1200_Nom-mass",
    "560to1200_Nom-mass",
    "570to1200_Nom-mass",
    "580to1200_Nom-mass",
    "550to1300_Nom-mass",
    "550to1400_Nom-mass"
  };

  vector<TH1F*> histos;

  for(unsigned int nf = 0 ; nf < files.size() ; ++nf){
    TFile* f = TFile::Open("./plots/V2/bias_study_Had_LT_MinPt150_DH1p6_MassFSR_"+files[nf]+".root");
    TTree* toys = (TTree*)f->Get("toys");
    TH2F* hf = new TH2F("h_"+files[nf], "", 5,0, 5,100,-4,4);
    toys->Draw("(ns_fit-ns_gen)/ns_err:nf>>h_"+files[nf],"", "");

    TH1F* h = new TH1F("h_"+files[nf], "", 5,0, 5);
    for(int b = 1; b <= h->GetNbinsX(); ++b){
      TH1D* proj = hf->ProjectionY("_py", b, b);
      h->SetBinContent(b, proj->GetMean());
      h->SetBinError(b, proj->GetMeanError());
    }
    h->SetMarkerColor(1+nf);
    h->SetMarkerSize(2);
    h->SetLineColor(1);
    h->SetMarkerStyle(kFullCircle);
    leg->AddEntry(h, files[nf], "P");
    histos.push_back(h);
  }

  c1->cd();
  for(unsigned int nh = 0 ; nh < histos.size(); ++nh){
    if(nh==0){
      histos[nh]->SetStats(0);
      histos[nh]->SetMinimum(-2.0);
      histos[nh]->SetMaximum(+4.0);
      histos[nh]->GetXaxis()->SetBinLabel(1, "dijet");
      histos[nh]->GetXaxis()->SetBinLabel(2, "poly");
      histos[nh]->GetXaxis()->SetBinLabel(3, "exp");
      histos[nh]->GetXaxis()->SetBinLabel(4, "pow");
      histos[nh]->GetXaxis()->SetBinLabel(5, "poly*exp");
      histos[nh]->GetYaxis()->SetTitle("Mean of #frac{#hat{#mu}-#mu}{#sigma_{#mu}}");
      histos[nh]->Draw("PE");      
    }
    else
      histos[nh]->Draw("PESAME");
  }    
  leg->Draw();
  c1->Draw();

}
