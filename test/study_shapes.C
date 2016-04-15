{

  using namespace RooFit;

  RooRealVar x("x","x", 500,1500);
  x.setRange(520,1500);

  TFile* fs = TFile::Open("plot.root", "READ");

  TH1F* mass_s = (TH1F*)fs->Get("signal_BTag_TT_MassFSR");
  RooDataHist data_s("data_s", "data signal", x, mass_s);
  RooRealVar Xp("Xp", "Xp", 200,1000);
  RooRealVar sP("sP", "sP", 0, 200);
  RooRealVar xi("xi", "xi",-20,20);
  RooRealVar rho1("rho1", "rho1", -20,20);
  RooRealVar rho2("rho2", "rho2", -20,20);
  RooBukinPdf buk_s("buk_s","buk_s", x, Xp, sP, xi, rho1, rho2);
  buk_s.fitTo(data_s);

  TH1F* mass_b = (TH1F*)fs->Get("background_BTag_TT_MassFSR");
  RooDataHist data_b("data_b", "data signal", x, mass_b);
  RooRealVar c("c","c",-20,20);
  RooExponential exp_b("exp_b","exp_b",x,c);
  exp_b.fitTo(data_b);

  RooRealVar a0("a0","a0",  0.,4000.);
  RooRealVar a1("a1","a1", -2000.,2000.);
  RooRealVar a2("a2","a2", -1000.,1000.);
  RooRealVar a3("a3","a3", -100.,100.);
  RooRealVar a4("a4","a4",-200.,200.);
  RooRealVar a5("a5","a5",-10.,10.);
  RooRealVar a6("a6","a6",-10.,10.);
  RooBernstein ch_b("ch_b","ch_b",x,RooArgList(a0,a1,a2,a3,a4,a5/*,a6*/));
  ch_b.chi2FitTo(data_b);

  TCanvas* c1 = new TCanvas("c1","c1",1200,400);
  c1->Divide(2);

  RooPlot* frame_s = x.frame();
  frame_s->SetName("frame_s");
  frame_s->SetTitle("Signal: Bukin function");
  data_s.plotOn(frame_s);
  buk_s.plotOn(frame_s, LineColor(kRed));
  c1->cd(1);
  frame_s->Draw();

  RooPlot* frame_b = x.frame();
  frame_b->SetName("frame_b");
  frame_b->SetTitle("Background: 5th order polynomial");
  data_b.plotOn(frame_b);
  ch_b.plotOn(frame_b,  LineColor(kBlue));
  c1->cd(2);
  frame_b->Draw();

}
