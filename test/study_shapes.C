{

  using namespace RooFit;

  //  RooRealVar x("x","x", 594,1506);
  RooRealVar x("x","x", 518,1506);
  //  x.setRange(520,1500);

  TFile* fs = TFile::Open("TTsigLumi.root", "READ");

  // KEY: TH1Fsignal_BTag_TT_MassFSR;1M750: BTag_TT_MassFSR
  //				   KEY: TH1Fbackground_BTag_TT_MassFSR;1HT100to200: BTag_TT_MassFSR


  TH1F* mass_s = (TH1F*)fs->Get("signal_BTag_TT_MassFSR");
  RooDataHist data_s("data_s", "data signal", x, mass_s);
  RooRealVar Xp("Xp", "Xp", 200,1000);
  RooRealVar sP("sP", "sP", 0, 200);
  RooRealVar xi("xi", "xi",-20,20);
  RooRealVar rho1("rho1", "rho1", -20,20);
  RooRealVar rho2("rho2", "rho2", -20,20);
  RooBukinPdf buk_s("buk_s","buk_s", x, Xp, sP, xi, rho1, rho2);
  std::cout << "######## FIT BUKIN  ###########" << std::endl;
  buk_s.fitTo(data_s);
  


  //  w.factory("RooCBShape:sig_pdf(x[110.,150.], mean[125.,120.,130.], sigma[3.,1.,5.], alpha[-5.,-30.,0.],n[0.1,0.,1000.])");

  //  RooRealVar xp("xp", "xp", 200,2000);
  RooRealVar mean("mean", "mean", 710, 500, 900);
  RooRealVar sigma("sigma", "sigma", 60, 0,100);
  RooRealVar alpha("alpha", "alpha", -2, -10,10);
  RooRealVar n("n", "n", 2, -10,10);
  RooCBShape cb_s("cb_s", "Crystal Ball Function", x, mean, sigma, alpha, n); 
  std::cout << "######## FIT Crystal Ball  ###########" << std::endl;
  cb_s.fitTo(data_s);


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
  std::cout << "######## FIT Pol 6  ###########" << std::endl;

  ch_b.chi2FitTo(data_b);

  TCanvas* c1 = new TCanvas("c1","c1",1200,400);
  c1->Divide(2);

  RooPlot* frame_s = x.frame();
  frame_s->SetName("frame_s");
  frame_s->SetTitle("Signal: Bukin function (Red), CB (Orange)");
  //  frame_s->SetTitle("Signal: CB function");
  data_s.plotOn(frame_s);
  buk_s.plotOn(frame_s, LineColor(kRed));
  cb_s.plotOn(frame_s, LineColor(kOrange));
  c1->cd(1);
  frame_s->Draw();

  RooPlot* frame_b = x.frame();
  frame_b->SetName("frame_b");
  frame_b->SetTitle("Background: 5th order polynomial");
  data_b.plotOn(frame_b);
  ch_b.plotOn(frame_b,  LineColor(kBlue));
  c1->cd(2);
  frame_b->Draw();




  RooWorkspace *w = new RooWorkspace("w","workspace") ;


  w->import(cb_s);
  w->import(buk_s);
  w->import(ch_b);
  w->import(data_b);
  w->import(data_s);
  //  w->import(SUM:model(buk_s,ch_b));  

 
  // Print workspace contents
  w->Print() ;

  /*
  RooAbsPdf * pdf = w.pdf("model");

  RooStats::ModelConfig mc("ModelConfig",&w);
  mc.SetPdf(*pdf);
  mc.SetParametersOfInterest(*w.var("nsig"));
  mc.SetObservables(*w.var("x"));
  // define set of nuisance parameters
  w.defineSet("nuisParams","alpha,n,a0,a1,a2,a3,a4,a5,nbkg");

  mc.SetNuisanceParameters(*w.set("nuisParams"));

  // import model in the workspace 
  w.import(mc);

  // write the workspace in the file
  TString fileName = "BkPoolModel.root";
  w.writeToFile(fileName,true);
  cout << "model written to file " << fileName << endl; 

   */

  // S a v e   w o r k s p a c e   i n   f i l e
  // -------------------------------------------

  // Save the workspace into a ROOT file
  w->writeToFile("US_workspace.root") ;


  // Workspace will remain in memory after macro finishes
  gDirectory->Add(w) ;



   
}
