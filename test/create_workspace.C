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
#include "RooBernstein.h"
#include "RooPlot.h"
#include "RooGenericPdf.h"
#include "RooWorkspace.h"
#include "RooHistPdf.h"

using namespace std;
using namespace RooFit;



void add_systematics(RooWorkspace* w=0,
		     RooRealVar* x=0,
		     TString input_fname="plots/V2/plot.root",
		     TString cat = "signal_Had_MT_MinPt200_DH2p0", 
		     TString cat_CSVSFUp = "signal_Had_MT_CSVSFUp_MinPt200_DH2p0", 
		     TString cat_CSVSFDown = "signal_Had_MT_CSVSFDown_MinPt200_DH2p0", 
		     TString h_name_sgn = "MassFSR",
		     TString proc = "M750",
		     int rebin_factor = 1,
		     TString title = "",
		     TString version = "V2"
		     ){

  TCanvas* c1 = new TCanvas("c1_systematics","c1",800,800);

  TLegend* leg = new TLegend(0.55,0.65,0.80,0.88, "","brNDC");
  leg->SetFillStyle(0);
  leg->SetBorderSize(0);
  leg->SetTextSize(0.05);
  leg->SetFillColor(10);

  TFile* input_file = TFile::Open(input_fname, "READ");
  if(input_file==0 || input_file->IsZombie()){
    cout << "File " << string(input_fname.Data()) << " could not be found." << endl;
    return;
  }

  TH1F* h_sgn_nominal = (TH1F*)input_file->Get(cat+"_"+h_name_sgn+"_"+proc);
  TH1F* h_sgn_CSVSFUp = (TH1F*)input_file->Get(cat_CSVSFUp+"_"+h_name_sgn+"_"+proc);    
  TH1F* h_sgn_CSVSFDown = (TH1F*)input_file->Get(cat_CSVSFDown+"_"+h_name_sgn+"_"+proc);    
  
  if(h_sgn_nominal!=0 && h_sgn_CSVSFUp!=0 && h_sgn_CSVSFDown!=0){
    float nominal = h_sgn_nominal->Integral(); 
    float CSVSFUp = h_sgn_CSVSFUp->Integral();
    float CSVSFDown = h_sgn_CSVSFDown->Integral();
    RooRealVar CSV_shift_sgn("CSV_shift_sgn", "CSV_shift_sgn",  TMath::Max(TMath::Abs(CSVSFUp-nominal), TMath::Abs(CSVSFDown-nominal))/nominal );
    w->import(CSV_shift_sgn);
  }
  else{
    cout << "No CSV shifted histogram with names " << string((cat_CSVSFDown+"_"+h_name_sgn+"_"+proc).Data()) << ", " << string((cat_CSVSFUp+"_"+h_name_sgn+"_"+proc).Data())  << endl;
    RooRealVar CSV_shift_sgn("CSV_shift_sgn", "CSV_shift_sgn",  0.05);
    w->import(CSV_shift_sgn);
  }

  TH1F* h_sgn_JECUp = (TH1F*)input_file->Get(cat+"_"+h_name_sgn+"_JECUp_"+proc);
  TH1F* h_sgn_JECDown = (TH1F*)input_file->Get(cat+"_"+h_name_sgn+"_JECDown_"+proc);
  TH1F* h_sgn_JERUp = (TH1F*)input_file->Get(cat+"_"+h_name_sgn+"_JERUp_"+proc);
  TH1F* h_sgn_JERDown = (TH1F*)input_file->Get(cat+"_"+h_name_sgn+"_JERDown_"+proc);

  if( h_sgn_nominal==0 
      || h_sgn_JECUp==0 || h_sgn_JECDown==0 
      || h_sgn_JERDown==0 || h_sgn_JERUp==0){
    cout << "No signal histogram!" << endl;
    input_file->Close();
    return;
  }

  if(rebin_factor>1){
    h_sgn_nominal->Rebin(rebin_factor);
    h_sgn_JECUp->Rebin(rebin_factor);
    h_sgn_JECDown->Rebin(rebin_factor);
    h_sgn_JERUp->Rebin(rebin_factor);
    h_sgn_JERDown->Rebin(rebin_factor);
  }

  // Nominal
  RooDataHist* data_sgn_nominal = new RooDataHist("data_sgn_nominal", "data signal nominal", *x, h_sgn_nominal);
  RooRealVar Xp_syst_nominal("Xp_syst_nominal", "Xp", 650.,850.);
  RooRealVar sP_syst_nominal("sP_syst_nominal", "sP", 50., 150.);
  RooRealVar xi_syst_nominal("xi_syst_nominal", "xi",-2.,0.);
  RooRealVar rho1_syst_nominal("rho1_syst_nominal", "rho1", -0.2,0.2);
  RooRealVar rho2_syst_nominal("rho2_syst_nominal", "rho2", -1.,1.);
  RooBukinPdf* buk_pdf_syst_nominal = new RooBukinPdf("buk_pdf_syst_nominal","RooBukinPdf for signal", *x, Xp_syst_nominal, sP_syst_nominal, xi_syst_nominal, rho1_syst_nominal, rho2_syst_nominal);
  buk_pdf_syst_nominal->fitTo(*data_sgn_nominal);  
  float m_nominal = Xp_syst_nominal.getVal();
  float s_nominal = sP_syst_nominal.getVal();

  // JEC up
  RooDataHist* data_sgn_JECUp = new RooDataHist("data_sgn_JECUp", "data signal JECUp", *x, h_sgn_JECUp);
  RooRealVar Xp_syst_JECUp("Xp_syst_JECUp", "Xp", 650.,850.);
  RooRealVar sP_syst_JECUp("sP_syst_JECUp", "sP", sP_syst_nominal.getVal());
  RooRealVar xi_syst_JECUp("xi_syst_JECUp", "xi", xi_syst_nominal.getVal());
  RooRealVar rho1_syst_JECUp("rho1_syst_JECUp", "rho1", rho1_syst_nominal.getVal());
  RooRealVar rho2_syst_JECUp("rho2_syst_JECUp", "rho2", rho2_syst_nominal.getVal());
  RooBukinPdf* buk_pdf_syst_JECUp = new RooBukinPdf("buk_pdf_syst_JECUp","RooBukinPdf for signal", *x, Xp_syst_JECUp, sP_syst_JECUp, xi_syst_JECUp, rho1_syst_JECUp, rho2_syst_JECUp);
  sP_syst_JECUp.setConstant();
  xi_syst_JECUp.setConstant();
  rho1_syst_JECUp.setConstant();
  rho2_syst_JECUp.setConstant();
  buk_pdf_syst_JECUp->fitTo(*data_sgn_JECUp);  
  float m_JECUp = Xp_syst_JECUp.getVal();

  // JEC down
  RooDataHist* data_sgn_JECDown = new RooDataHist("data_sgn_JECDown", "data signal JECDown", *x, h_sgn_JECDown);
  RooRealVar Xp_syst_JECDown("Xp_syst_JECDown", "Xp", 650.,850.);
  RooRealVar sP_syst_JECDown("sP_syst_JECDown", "sP", sP_syst_nominal.getVal());
  RooRealVar xi_syst_JECDown("xi_syst_JECDown", "xi", xi_syst_nominal.getVal());
  RooRealVar rho1_syst_JECDown("rho1_syst_JECDown", "rho1", rho1_syst_nominal.getVal());
  RooRealVar rho2_syst_JECDown("rho2_syst_JECDown", "rho2", rho2_syst_nominal.getVal());
  RooBukinPdf* buk_pdf_syst_JECDown = new RooBukinPdf("buk_pdf_syst_JECDown","RooBukinPdf for signal", *x, Xp_syst_JECDown, sP_syst_JECDown, xi_syst_JECDown, rho1_syst_JECDown, rho2_syst_JECDown);
  sP_syst_JECDown.setConstant();
  xi_syst_JECDown.setConstant();
  rho1_syst_JECDown.setConstant();
  rho2_syst_JECDown.setConstant();
  buk_pdf_syst_JECDown->fitTo(*data_sgn_JECDown);  
  float m_JECDown = Xp_syst_JECDown.getVal();

  // JER up
  RooDataHist* data_sgn_JERUp = new RooDataHist("data_sgn_JERUp", "data signal JERUp", *x, h_sgn_JERUp);
  RooRealVar Xp_syst_JERUp("Xp_syst_JERUp", "Xp", Xp_syst_nominal.getVal());
  RooRealVar sP_syst_JERUp("sP_syst_JERUp", "sP", 50., 150.);
  RooRealVar xi_syst_JERUp("xi_syst_JERUp", "xi", xi_syst_nominal.getVal());
  RooRealVar rho1_syst_JERUp("rho1_syst_JERUp", "rho1", rho1_syst_nominal.getVal());
  RooRealVar rho2_syst_JERUp("rho2_syst_JERUp", "rho2", rho2_syst_nominal.getVal());
  RooBukinPdf* buk_pdf_syst_JERUp = new RooBukinPdf("buk_pdf_syst_JERUp","RooBukinPdf for signal", *x, Xp_syst_JERUp, sP_syst_JERUp, xi_syst_JERUp, rho1_syst_JERUp, rho2_syst_JERUp);
  Xp_syst_JERUp.setConstant();
  xi_syst_JERUp.setConstant();
  rho1_syst_JERUp.setConstant();
  rho2_syst_JERUp.setConstant();
  buk_pdf_syst_JERUp->fitTo(*data_sgn_JERUp);  
  buk_pdf_syst_JERUp->fitTo(*data_sgn_JERUp);  
  float s_JERUp = sP_syst_JERUp.getVal();

  // JER down
  RooDataHist* data_sgn_JERDown = new RooDataHist("data_sgn_JERDown", "data signal JERDown", *x, h_sgn_JERDown);
  RooRealVar Xp_syst_JERDown("Xp_syst_JERDown", "Xp", Xp_syst_nominal.getVal());
  RooRealVar sP_syst_JERDown("sP_syst_JERDown", "sP", 50., 150.);
  RooRealVar xi_syst_JERDown("xi_syst_JERDown", "xi", xi_syst_nominal.getVal());
  RooRealVar rho1_syst_JERDown("rho1_syst_JERDown", "rho1", rho1_syst_nominal.getVal());
  RooRealVar rho2_syst_JERDown("rho2_syst_JERDown", "rho2", rho2_syst_nominal.getVal());
  RooBukinPdf* buk_pdf_syst_JERDown = new RooBukinPdf("buk_pdf_syst_JERDown","RooBukinPdf for signal", *x, Xp_syst_JERDown, sP_syst_JERDown, xi_syst_JERDown, rho1_syst_JERDown, rho2_syst_JERDown);
  Xp_syst_JERDown.setConstant();
  xi_syst_JERDown.setConstant();
  rho1_syst_JERDown.setConstant();
  rho2_syst_JERDown.setConstant();
  buk_pdf_syst_JERDown->fitTo(*data_sgn_JERDown);  
  buk_pdf_syst_JERDown->fitTo(*data_sgn_JERDown);  
  float s_JERDown = sP_syst_JERDown.getVal();

  // remove constant option
  w->var("Xp_sgn")->setConstant(kFALSE);
  w->var("sP_sgn")->setConstant(kFALSE);

  cout << "JEC:" << endl;
  cout << "\tNominal: " << m_nominal << endl;
  cout << "\tUp     : " << m_JECUp << endl;
  cout << "\tDown   : " << m_JECDown << endl;
  cout << "JER:" << endl;
  cout << "\tNominal: " << s_nominal << endl;
  cout << "\tUp     : " << s_JERUp << endl;
  cout << "\tDown   : " << s_JERDown << endl;


  RooRealVar Xp_shift_sgn("Xp_shift_sgn","Xp_shift_sgn", TMath::Max( TMath::Abs(m_nominal-m_JECDown), 
								     TMath::Abs(m_nominal-m_JECUp) ));
  w->import(Xp_shift_sgn);

  RooRealVar sP_shift_sgn("sP_shift_sgn","sP_shift_sgn", TMath::Max( TMath::Abs(s_nominal-s_JERDown), 
								     TMath::Abs(s_nominal-s_JERUp) ));
  w->import(sP_shift_sgn);

  RooPlot* frame = x->frame();
  frame->SetName("frame");
  frame->SetTitle(title);
  data_sgn_nominal->plotOn(frame, MarkerColor(kBlack));
  buk_pdf_syst_nominal->plotOn(frame, LineColor(kBlack), Name("buk_pdf_syst_nominal"));     
  buk_pdf_syst_JECUp->plotOn(frame, LineColor(kRed), LineStyle(kSolid), Name("buk_pdf_syst_JECUp"));     
  buk_pdf_syst_JECDown->plotOn(frame, LineColor(kRed), LineStyle(kDashed), Name("buk_pdf_syst_JECDown"));     
  buk_pdf_syst_JERUp->plotOn(frame, LineColor(kBlue), LineStyle(kSolid), Name("buk_pdf_syst_JERUp"));     
  buk_pdf_syst_JERDown->plotOn(frame, LineColor(kBlue), LineStyle(kDashed), Name("buk_pdf_syst_JERDown"));     

  leg->AddEntry(frame->getCurve("buk_pdf_syst_nominal"),"Nominal", "L");
  leg->AddEntry(frame->getCurve("buk_pdf_syst_JECUp"),"JES up", "L");
  leg->AddEntry(frame->getCurve("buk_pdf_syst_JECDown"),"JES down", "L");
  leg->AddEntry(frame->getCurve("buk_pdf_syst_JERUp"),"JER up", "L");
  leg->AddEntry(frame->getCurve("buk_pdf_syst_JERDown"),"JER down", "L");
  
  c1->cd();
  frame->Draw();
  leg->Draw();
  c1->SaveAs("plots/"+version+"/Systematics_mass_spectra_"+cat+".png");

  delete data_sgn_nominal;
  delete data_sgn_JECUp;
  delete data_sgn_JECDown;
  delete data_sgn_JERUp;
  delete data_sgn_JERDown;
  delete buk_pdf_syst_nominal;
  delete buk_pdf_syst_JECUp;
  delete buk_pdf_syst_JECDown;
  delete buk_pdf_syst_JERUp;
  delete buk_pdf_syst_JERDown;
  delete c1;

  return;
}

void compare_mass_spectra(float x_min=550., float x_max=1500.,
			  TString input_fname="plots/V2/plot.root",
			  TString cat = "signal_Had_MT_MinPt200_DH2p0", 
			  TString h_name_sgn_1 = "Mass_M750",
			  TString h_name_sgn_2 = "MassFSR_M750",
			  TString h_name_sgn_3 = "MassAK08_M750",
			  int rebin_factor = 1,
			  TString title = "",
			  TString version = "V2"
			  ){

  TCanvas* c1 = new TCanvas("c1","c1",800,800);

  RooRealVar* x = new RooRealVar("x","x", 400., 4000.);
  x->setMin(x_min);
  x->setMax(x_max);

  TFile* input_file = TFile::Open(input_fname, "READ");
  if(input_file==0 || input_file->IsZombie()){
    cout << "File " << string(input_fname.Data()) << " could not be found." << endl;
    return;
  }

  TH1F* h_sgn_1 = (TH1F*)input_file->Get(cat+"_"+h_name_sgn_1);
  TH1F* h_sgn_2 = (TH1F*)input_file->Get(cat+"_"+h_name_sgn_2);
  TH1F* h_sgn_3 = (TH1F*)input_file->Get(cat+"_"+h_name_sgn_3);
  if( h_sgn_1==0 || h_sgn_2==0 || h_sgn_3==0){
    cout << "No signal histogram!" << endl;
    input_file->Close();
    return;
  }

  // optionally rebin the histogram before making the RooDataHist
  if(rebin_factor>1){
    h_sgn_1->Rebin(rebin_factor);
    h_sgn_2->Rebin(rebin_factor);
    h_sgn_3->Rebin(rebin_factor);
  }

  // the signal data set
  RooDataHist* data_sgn_1 = new RooDataHist("data_sgn_1", "data signal 1", *x, h_sgn_1);
  RooDataHist* data_sgn_2 = new RooDataHist("data_sgn_2", "data signal 2", *x, h_sgn_2);
  RooDataHist* data_sgn_3 = new RooDataHist("data_sgn_3", "data signal 3", *x, h_sgn_3);

  // Bukin pdf: http://arxiv.org/abs/0711.4449
  RooRealVar Xp_1("Xp_sgn_1", "Xp", 650.,850.);
  RooRealVar sP_1("sP_sgn_1", "sP", 50., 150.);
  RooRealVar xi_1("xi_sgn_1", "xi",-2.,0.);
  RooRealVar rho1_1("rho1_sgn_1", "rho1", -0.2,0.2);
  RooRealVar rho2_1("rho2_sgn_1", "rho2", -1.,1.);
  RooBukinPdf* buk_pdf_sgn_1 = new RooBukinPdf("buk_pdf_sgn_1","RooBukinPdf for signal 1", *x, Xp_1, sP_1, xi_1, rho1_1, rho2_1);
  std::cout << "######## FIT BUKIN  ###########" << std::endl;
  buk_pdf_sgn_1->fitTo(*data_sgn_1);

  // Bukin pdf: http://arxiv.org/abs/0711.4449
  RooRealVar Xp_2("Xp_sgn_2", "Xp", 650.,850.);
  RooRealVar sP_2("sP_sgn_2", "sP", 50., 150.);
  RooRealVar xi_2("xi_sgn_2", "xi",-2.,0.);
  RooRealVar rho1_2("rho1_sgn_2", "rho1", -0.2,0.2);
  RooRealVar rho2_2("rho2_sgn_2", "rho2", -1.,1.);
  RooBukinPdf* buk_pdf_sgn_2 = new RooBukinPdf("buk_pdf_sgn_2","RooBukinPdf for signal 1", *x, Xp_2, sP_2, xi_2, rho1_2, rho2_2);
  std::cout << "######## FIT BUKIN  ###########" << std::endl;
  buk_pdf_sgn_2->fitTo(*data_sgn_2);

  // Bukin pdf: http://arxiv.org/abs/0711.4449
  RooRealVar Xp_3("Xp_sgn_3", "Xp", 650.,850.);
  RooRealVar sP_3("sP_sgn_3", "sP", 50., 150.);
  RooRealVar xi_3("xi_sgn_3", "xi",-2.,0.);
  RooRealVar rho1_3("rho1_sgn_3", "rho1", -0.2,0.2);
  RooRealVar rho2_3("rho2_sgn_3", "rho2", -1.,1.);
  RooBukinPdf* buk_pdf_sgn_3 = new RooBukinPdf("buk_pdf_sgn_3","RooBukinPdf for signal 1", *x, Xp_3, sP_3, xi_3, rho1_3, rho2_3);
  std::cout << "######## FIT BUKIN  ###########" << std::endl;
  buk_pdf_sgn_3->fitTo(*data_sgn_3);

  TLegend* leg = new TLegend(0.55,0.65,0.80,0.88, "","brNDC");
  leg->SetFillStyle(0);
  leg->SetBorderSize(0);
  leg->SetTextSize(0.05);
  leg->SetFillColor(10);
  
  RooPlot* frame = x->frame();
  frame->SetName("frame");
  frame->SetTitle(title);
  data_sgn_1->plotOn(frame, MarkerColor(kBlue));
  data_sgn_2->plotOn(frame, MarkerColor(kRed));
  data_sgn_3->plotOn(frame, MarkerColor(kMagenta));
  buk_pdf_sgn_1->plotOn(frame, LineColor(kBlue), Name("buk_pdf_sgn_1"));
  buk_pdf_sgn_2->plotOn(frame, LineColor(kRed), Name("buk_pdf_sgn_2"));
  buk_pdf_sgn_3->plotOn(frame, LineColor(kMagenta), Name("buk_pdf_sgn_3"));

  leg->AddEntry(frame->getCurve("buk_pdf_sgn_1"), Form("Reco: #mu=%.0f,#sigma=%.0f", Xp_1.getVal(), sP_1.getVal() ), "L");
  leg->AddEntry(frame->getCurve("buk_pdf_sgn_2"), Form("FSR: #mu=%.0f,#sigma=%.0f", Xp_2.getVal(), sP_2.getVal() ), "L");
  leg->AddEntry(frame->getCurve("buk_pdf_sgn_3"), Form("aK_{T}08: #mu=%.0f,#sigma=%.0f", Xp_3.getVal(), sP_3.getVal() ), "L");

  c1->cd();  
  frame->Draw();
  leg->Draw();
  c1->cd();
  c1->Update();
  c1->SaveAs("plots/"+version+"/compare_mass_spectra_"+cat+".png");

  delete c1;
  delete leg;
  delete x;
  delete data_sgn_1;
  delete data_sgn_2;
  delete data_sgn_3;
  delete buk_pdf_sgn_1;
  delete buk_pdf_sgn_2;
  delete buk_pdf_sgn_3;
  input_file->Close();
}

void add_signal_to_workspace(TCanvas* c1 = 0,
			     RooWorkspace* w=0,
			     TString input_fname="plots/V2/plot.root",
			     TString h_name_sgn = "signal_Had_MT_MinPt150_DH1p6_MassFSR_M750",
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
    cout << "No signal histogram " << string(h_name_sgn.Data()) << endl;
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
  RooRealVar a0("a0_bkg","a0",  1); a0.setConstant();
  RooRealVar a1("a1_bkg","a1",  -1.,1.);
  RooRealVar a2("a2_bkg","a2",  -1.,1.);
  RooRealVar a3("a3_bkg","a3",  -1.,1.);
  RooRealVar a4("a4_bkg","a4",  -1.,1.);
  RooRealVar a5("a5_bkg","a5",  -1.,1.);
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

  // Empirical mass function with turn-on
  RooRealVar m0_t("m0_t_bkg","m0",300., 600.);
  RooRealVar s0_t("s0_t_bkg","s0",10., 200.);
  RooRealVar p1_t("p1_t_bkg","p1",0.0, 20.);
  RooRealVar p2_t("p2_t_bkg","p2",10., 40.);
  RooRealVar p3_t("p3_t_bkg","p3",0.5, 5.0);
  TString mass_formula_t = "0.5*(TMath::Erf((x-m0_t_bkg)/s0_t_bkg)+1)*TMath::Power(1-x/13000.,p1_t_bkg)/(TMath::Power(x/13000.,p2_t_bkg+p3_t_bkg*TMath::Log(x/13000.)))";
  RooGenericPdf* mass_t_pdf_bkg = new RooGenericPdf("mass_t_pdf_bkg", mass_formula_t, RooArgSet(*x,m0_t,s0_t,p1_t,p2_t,p3_t));
  RooRealVar mass_t_pdf_bkg_norm("mass_t_pdf_bkg_norm", "background normalisation", data_bkg->sumEntries());
  mass_t_pdf_bkg->fitTo(*data_bkg, PrintLevel(-1), PrintEvalErrors(0), Warnings(kFALSE));
  if( set_param_const ){  
    m0_t.setConstant();  
    s0_t.setConstant();  
    p1_t.setConstant();  
    p2_t.setConstant();  
    p3_t.setConstant();  
  }
  w->import(*mass_t_pdf_bkg);
  w->import(mass_t_pdf_bkg_norm);

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
  mass_t_pdf_bkg->plotOn(frame, LineColor(kBlue), LineStyle(kDashed),Name("mass_t_pdf_bkg"));

  c1->cd(2);  
  frame->Draw();

  double chi2_exp = frame->chiSquare("exp_pdf_bkg","data", 1);
  double chi2_pol = frame->chiSquare("pol_pdf_bkg","data", 5);
  double chi2_mass = frame->chiSquare("mass_pdf_bkg","data", 3);
  double chi2_mass_t = frame->chiSquare("mass_t_pdf_bkg","data", 3+2);

  leg->SetHeader(Form("Range: [%.0f,%.0f] GeV", x->getMin(), x->getMax()) );
  
  leg->AddEntry(frame->getCurve("exp_pdf_bkg"), Form("Exponential: #chi^{2}/ndof=%.2f", chi2_exp), "L");
  leg->AddEntry(frame->getCurve("pol_pdf_bkg"), Form("Pol. 5th: #chi^{2}/ndof=%.2f", chi2_pol), "L");
  leg->AddEntry(frame->getCurve("mass_pdf_bkg"), Form("Mass: #chi^{2}/ndof=%.2f", chi2_mass), "L");
  leg->AddEntry(frame->getCurve("mass_t_pdf_bkg"), Form("Mass w/ turn-on: #chi^{2}/ndof=%.2f", chi2_mass_t), "L");
  leg->Draw();

  return;  
}

void add_data_to_workspace(TCanvas* c1 = 0,
			   RooWorkspace* w=0,
			   TString input_fname="plots/plot.root",
			   TString h_name_data = "data_BTag_MT_MassFSR_M750",
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
  
  TH1F* h_data = (TH1F*)input_file->Get(h_name_data);
  if( h_data==0 ){
    cout << "No data histogram!" << endl;
    input_file->Close();
    return;
  }

  // optionally rebin the histogram before making the RooDataHist
  if(rebin_factor>1) h_data->Rebin(rebin_factor);

  // the signal data set
  RooDataHist* data_obs = new RooDataHist("data_obs", "data observed", *x, h_data);
  w->import(*data_obs);

  return;
}

void create_workspace(TString ws_name="Xbb_workspace", 
		      TString cat_btag = "Had_MT",		      
		      TString cat_kin = "MinPt150_DH1p6",		      
		      float x_min=550., float x_max=1500.,
		      TString mass = "MassFSR",
		      TString proc="M750",
		      TString version="V2"){

  TString cat = cat_btag+"_"+cat_kin;

  TCanvas* c1 = new TCanvas("c1"+cat,"c1",1200,400);
  c1->Divide(2);

  RooWorkspace *w = new RooWorkspace( ws_name, "workspace") ;

  // the fitting variable
  RooRealVar x("x","x", 400., 4000.);
  x.setMin(x_min);
  x.setMax(x_max);
  w->import(x);

  add_signal_to_workspace(c1, w, 
			  "plots/"+version+"/plot.root", "signal_"+cat+"_"+mass+"_"+proc,
			  &x, 1, true,
			  ("Signal, m_{X}="+proc+" GeV")
			  );

  add_systematics(w, &x,
		  "plots/"+version+"/plot.root",
		  "signal_"+cat,
		  "signal_"+cat_btag+"_CSVSFUp_"+cat_kin,
		  "signal_"+cat_btag+"_CSVSFDown_"+cat_kin,
		  mass, proc,  
		  1, "JEC/JER", version
		  );

  
  add_background_to_workspace(c1, w, 
			      "plots/"+version+"/plot.root", "background_"+cat+"_"+mass,
			      &x, 1, false,
			      "Background"
			      );

  add_data_to_workspace(c1, w, 
			"plots/"+version+"/plot.root", "data_"+cat+"_"+mass,
			&x, 1, false,
			"Data"
			);

  // print workspace contents  
  w->Print() ; 

  // save the workspace into a ROOT file
  TString savename = "./plots/"+version+"/"+ws_name+"_"+cat+"_"+mass+"_"+TString(Form("%.0fto%.0f",x_min,x_max));
  w->writeToFile(savename+".root") ;

  // draw fit results
  c1->Draw();
  c1->SaveAs(savename+".png");

  delete w;
}

void create_all(TString version="V2"){

  vector<TString> cats_btag = {
    "Had_MT",
    "Had_LT"
  };

  vector<TString> cats_kin = {
    "MinPt150_DH2p0",
    "MinPt150_DH1p6",
    //"MinPt150_DH1p1",
    "MinPt200_DH2p0",
    "MinPt200_DH1p6"
    //"MinPt200_DH1p1"
  };

  vector<TString> masses = {"MassFSR"};

  for(unsigned int btag = 0 ; btag < cats_btag.size(); ++btag){
    for(unsigned int kin = 0 ; kin < cats_kin.size(); ++kin){
      for(unsigned int m = 0 ; m < masses.size(); ++m){
	create_workspace("Xbb_workspace", cats_btag[btag], cats_kin[kin], 540., 1200., masses[m], "M750", version);
	create_workspace("Xbb_workspace", cats_btag[btag], cats_kin[kin], 550., 1200., masses[m], "M750", version);
	create_workspace("Xbb_workspace", cats_btag[btag], cats_kin[kin], 560., 1200., masses[m], "M750", version);
	create_workspace("Xbb_workspace", cats_btag[btag], cats_kin[kin], 570., 1200., masses[m], "M750", version);
	create_workspace("Xbb_workspace", cats_btag[btag], cats_kin[kin], 580., 1200., masses[m], "M750", version);
	create_workspace("Xbb_workspace", cats_btag[btag], cats_kin[kin], 550., 1300., masses[m], "M750", version);
	create_workspace("Xbb_workspace", cats_btag[btag], cats_kin[kin], 550., 1400., masses[m], "M750", version);
	create_workspace("Xbb_workspace", cats_btag[btag], cats_kin[kin], 550., 1500., masses[m], "M750", version);
      }
    }
  }
  
}
