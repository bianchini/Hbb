#include "TFile.h"
#include "TH1F.h"
#include "TCanvas.h"
#include "TLegend.h"
#include "TSystem.h"

#include "RooRealVar.h"
#include "RooDataHist.h"
#include "RooBukinPdf.h"
#include "RooCBShape.h"
#include "RooExponential.h"
#include "RooBernstein.h"
#include "RooPlot.h"
#include "RooGenericPdf.h"
#include "RooWorkspace.h"
#include "RooHistPdf.h"

using namespace std;
using namespace RooFit;


void add_signal_to_workspace(TCanvas* c1 = 0,
			     RooWorkspace* w=0,
			     TString input_fname="plots/plot.root",
			     TString h_name_sgn = "signal_BTag_MT_MassFSR_M750",
			     RooRealVar* x=0,
			     int rebin_factor = 1,
			     bool set_param_const = true,
			     TString title = ""
			     ){

  TFile* input_file = TFile::Open(input_fname, "READ");
  if(input_file==0 || input_file->IsZombie()){
    cout << "File " << string(input_fname.Data()) << " could not be found." << endl;
    return;
  }

  TH1F* h_sgn = (TH1F*)input_file->Get(h_name_sgn);
  if( h_sgn==0 ){
    cout << "No signal histogram!" << endl;
    input_file->Close();
    return;
  }

  // optionally rebin the histogram before making the RooDataHist
  if(rebin_factor>1) h_sgn->Rebin(rebin_factor);

  // the signal data set
  RooDataHist* data_sgn = new RooDataHist("data_sgn", "data signal", *x, h_sgn);
  w->import(*data_sgn);

  // the hist pdf of the signal
  RooHistPdf* hist_pdf_sgn = new RooHistPdf("hist_pdf_sgn","hist pdf for signal", *x, *data_sgn);
  RooRealVar hist_pdf_sgn_norm("hist_pdf_sgn_norm", "signal normalisation", data_sgn->sumEntries());
  w->import(*hist_pdf_sgn);
  w->import(hist_pdf_sgn_norm);

  // Bukin pdf: http://arxiv.org/abs/0711.4449
  RooRealVar Xp("Xp_sgn", "Xp", 650.,850.);
  RooRealVar sP("sP_sgn", "sP", 50., 150.);
  RooRealVar xi("xi_sgn", "xi",-2.,0.);
  RooRealVar rho1("rho1_sgn", "rho1", -0.2,0.2);
  RooRealVar rho2("rho2_sgn", "rho2", -1.,1.);
  RooBukinPdf* buk_pdf_sgn = new RooBukinPdf("buk_pdf_sgn","RooBukinPdf for signal", *x, Xp, sP, xi, rho1, rho2);
  RooRealVar buk_pdf_sgn_norm("buk_pdf_sgn_norm","signal normalisation", data_sgn->sumEntries());
  std::cout << "######## FIT BUKIN  ###########" << std::endl;
  buk_pdf_sgn->fitTo(*data_sgn);
  if(set_param_const){
    Xp.setConstant();
    sP.setConstant();
    xi.setConstant();
    rho1.setConstant();
    rho2.setConstant();
  }
  w->import(*buk_pdf_sgn);
  w->import(buk_pdf_sgn_norm);
  
  // CB pdf
  RooRealVar mean("mean_sgn", "mean", 710, 600, 900);
  RooRealVar sigma("sigma_sgn", "sigma", 60, 0,150);
  RooRealVar alpha("alpha_sgn", "alpha", -2, -10,10);
  RooRealVar n("n_sgn", "n", 2, -10,10);
  RooCBShape* cb_pdf_sgn = new RooCBShape("cb_pdf_sgn", "RooCBShape for signal", *x, mean, sigma, alpha, n); 
  RooRealVar cb_pdf_sgn_norm("cb_pdf_sgn_norm","signal normalisation", data_sgn->sumEntries());
  std::cout << "######## FIT Crystal Ball  ###########" << std::endl;
  cb_pdf_sgn->fitTo(*data_sgn);
  if(set_param_const){
    mean.setConstant(); 
    sigma.setConstant(); 
    alpha.setConstant(); 
    n.setConstant(); 
  }
  w->import(*cb_pdf_sgn);
  w->import(cb_pdf_sgn_norm);

  TLegend* leg = new TLegend(0.55,0.65,0.80,0.88, "","brNDC");
  leg->SetFillStyle(0);
  leg->SetBorderSize(0);
  leg->SetTextSize(0.05);
  leg->SetFillColor(10);
  
  RooPlot* frame = x->frame();
  frame->SetName("frame");
  frame->SetTitle(title);
  data_sgn->plotOn(frame, Name("data"));
  buk_pdf_sgn->plotOn(frame, LineColor(kRed), Name("buk_pdf_sgn"));
  cb_pdf_sgn->plotOn(frame, LineColor(kOrange), Name("cb_pdf_sgn"));

  c1->cd(1);  
  frame->Draw();

  double chi2_buk = frame->chiSquare("buk_pdf_sgn","data", 5);
  double chi2_cb = frame->chiSquare("cb_pdf_sgn","data", 1);

  leg->SetHeader(Form("Range: [%.0f,%.0f] GeV", x->getMin(), x->getMax()) );
  
  leg->AddEntry(frame->getCurve("buk_pdf_sgn"), Form("Bukin: #chi^{2}/ndof=%.2f", chi2_buk), "L");
  leg->AddEntry(frame->getCurve("cb_pdf_sgn"), Form("CB: #chi^{2}/ndof=%.2f", chi2_cb), "L");
  leg->Draw();

  //input_file->Close();
  return;
}



void add_background_to_workspace(TCanvas* c1 = 0,
				 RooWorkspace* w=0,
				 TString input_fname="plots/plot.root",
				 TString h_name_bkg = "background_BTag_MT_MassFSR_M750",
				 RooRealVar* x=0,
				 int rebin_factor = 1,
				 bool set_param_const = false,
				 TString title = ""
			     ){

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
  RooDataHist* data_bkg = new RooDataHist("data_bkg", "data background", *x, h_bkg);
  w->import(*data_bkg);

  // the hist pdf of the signal
  RooHistPdf* hist_pdf_bkg = new RooHistPdf("hist_pdf_bkg","hist pdf for background", *x, *data_bkg);
  RooRealVar hist_pdf_bkg_norm("hist_pdf_bkg_norm", "background normalisation", data_bkg->sumEntries());
  w->import(*hist_pdf_bkg);
  w->import(hist_pdf_bkg_norm);

  // Exponential Pdf
  RooRealVar c("c_bkg","c", -0.008, -0.004);
  RooExponential* exp_pdf_bkg = new RooExponential("exp_pdf_bkg","Exponential for background", *x, c);
  RooRealVar exp_pdf_bkg_norm("exp_pdf_bkg_norm", "background normalisation", data_bkg->sumEntries());
  std::cout << "######## FIT Exponential  ###########" << std::endl;
  exp_pdf_bkg->fitTo(*data_bkg); 
  if( set_param_const ){
    c.setConstant();
  }
  w->import(*exp_pdf_bkg);
  w->import(exp_pdf_bkg_norm);

  // Polynomial Pdf
  RooRealVar a0("a0_bkg","a0",  0.,4000.);
  RooRealVar a1("a1_bkg","a1", -2000.,2000.);
  RooRealVar a2("a2_bkg","a2", -1000.,1000.);
  RooRealVar a3("a3_bkg","a3", -100.,100.);
  RooRealVar a4("a4_bkg","a4",-200.,200.);
  RooRealVar a5("a5_bkg","a5",-10.,10.);
  RooBernstein* pol_pdf_bkg = new RooBernstein("pol_pdf_bkg","Polynomial for background", *x, RooArgList(a0,a1,a2,a3,a4,a5));
  RooRealVar pol_pdf_bkg_norm("pol_pdf_bkg_norm", "background normalisation", data_bkg->sumEntries());
  std::cout << "######## FIT Pol 6  ###########" << std::endl;
  pol_pdf_bkg->fitTo(*data_bkg, PrintLevel(-1), PrintEvalErrors(0), Warnings(kFALSE));
  if( set_param_const ){ 
    a0.setConstant();
    a1.setConstant();
    a2.setConstant();
    a3.setConstant();
    a4.setConstant();
    a5.setConstant();
  }
  w->import(*pol_pdf_bkg);
  w->import(pol_pdf_bkg_norm);

  // Empirical mass function
  RooRealVar p1("p1_bkg","p1",0.0, 20.);
  RooRealVar p2("p2_bkg","p2",10., 40.);
  RooRealVar p3("p3_bkg","p3",0.5, 5.0);
  TString mass_formula = "TMath::Power(1-x/13000.,p1_bkg)/(TMath::Power(x/13000.,p2_bkg+p3_bkg*TMath::Log(x/13000.)))";
  RooGenericPdf* mass_pdf_bkg = new RooGenericPdf("mass_pdf_bkg", mass_formula, RooArgSet(*x,p1,p2,p3));
  RooRealVar mass_pdf_bkg_norm("mass_pdf_bkg_norm", "background normalisation", data_bkg->sumEntries());
  mass_pdf_bkg->fitTo(*data_bkg, PrintLevel(-1), PrintEvalErrors(0), Warnings(kFALSE));
  if( set_param_const ){  
    p1.setConstant();  
    p2.setConstant();  
    p3.setConstant();  
  }
  w->import(*mass_pdf_bkg);
  w->import(mass_pdf_bkg_norm);

  TLegend* leg = new TLegend(0.45,0.65,0.75,0.88, "","brNDC");
  leg->SetFillStyle(0);
  leg->SetBorderSize(0);
  leg->SetTextSize(0.05);
  leg->SetFillColor(10);
  
  RooPlot* frame = x->frame();
  frame->SetName("frame");
  frame->SetTitle(title);
  data_bkg->plotOn(frame, Name("data"));
  exp_pdf_bkg->plotOn(frame, LineColor(kRed), Name("exp_pdf_bkg"));
  pol_pdf_bkg->plotOn(frame, LineColor(kOrange), Name("pol_pdf_bkg"));
  mass_pdf_bkg->plotOn(frame, LineColor(kBlue), Name("mass_pdf_bkg"));

  c1->cd(2);  
  frame->Draw();

  double chi2_exp = frame->chiSquare("exp_pdf_bkg","data", 1);
  double chi2_pol = frame->chiSquare("pol_pdf_bkg","data", 5);
  double chi2_mass = frame->chiSquare("mass_pdf_bkg","data", 3);

  leg->SetHeader(Form("Range: [%.0f,%.0f] GeV", x->getMin(), x->getMax()) );
  
  leg->AddEntry(frame->getCurve("exp_pdf_bkg"), Form("Exponential: #chi^{2}/ndof=%.2f", chi2_exp), "L");
  leg->AddEntry(frame->getCurve("pol_pdf_bkg"), Form("Pol. 5th: #chi^{2}/ndof=%.2f", chi2_pol), "L");
  leg->AddEntry(frame->getCurve("mass_pdf_bkg"), Form("Mass: #chi^{2}/ndof=%.2f", chi2_mass), "L");
  leg->Draw();

  return;  
}


void create_workspace(TString ws_name="Xbb_workspace", 
		      TString cat = "MT",		      
		      float x_min=550., float x_max=1500.){

  TCanvas* c1 = new TCanvas("c1"+cat,"c1",1200,400);
  c1->Divide(2);

  RooWorkspace *w = new RooWorkspace( ws_name, "workspace") ;

  // the fitting variable
  RooRealVar x("x","x", 400., 4000.);
  x.setMin(x_min);
  x.setMax(x_max);
  w->import(x);

  add_signal_to_workspace(c1, w, 
			  "plots/plot.root", "signal_BTag_"+cat+"_MassFSR_M750",
			  &x, 1, true,
			  "Signal for MT, m_{X}=750 GeV"
			  );
  
  add_background_to_workspace(c1, w, 
			      "plots/plot.root", "background_BTag_"+cat+"_MassFSR",
			      &x, 1, false,
			      "Background"
			      );

  // print workspace contents  
  w->Print() ; 

  // save the workspace into a ROOT file

  TString savename = "./plots/"+ws_name+"_"+cat+"_"+TString(Form("%.0fto%.0f",x_min,x_max));
  w->writeToFile(savename+".root") ;

  // draw fit results
  c1->Draw();
  c1->SaveAs(savename+".png");

  delete w;
}

void create_all(){
  create_workspace("Xbb_workspace", "MT", 550., 1200.);
  create_workspace("Xbb_workspace", "MT", 550., 1500.);
  create_workspace("Xbb_workspace", "MT", 550., 1800.);
  create_workspace("Xbb_workspace", "MT", 550., 2000.);
  create_workspace("Xbb_workspace", "MT", 525., 1500.);
  create_workspace("Xbb_workspace", "MT", 500., 1500.);

  create_workspace("Xbb_workspace", "TT", 550., 1200.);
  create_workspace("Xbb_workspace", "TT", 550., 1500.);
  create_workspace("Xbb_workspace", "TT", 550., 1800.);
  create_workspace("Xbb_workspace", "TT", 550., 2000.);
  create_workspace("Xbb_workspace", "TT", 525., 1500.);
  create_workspace("Xbb_workspace", "TT", 500., 1500.);
}
