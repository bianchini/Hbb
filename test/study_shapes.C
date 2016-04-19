{

  using namespace RooFit;

  TFile* fs = TFile::Open("plots/plot.root", "READ");

  TH1F* mass_s = (TH1F*)fs->Get("signal_BTag_MT_MassFSR_M750");
  if( mass_s==0 ){
    cout << "No signal histogram!" << endl;
    fs->Close();
    return;
  }
  //mass_s->Rebin(2);

  RooRealVar x("x","x", 530,1200);
  x.setBins(mass_s->GetNbinsX());

  RooDataHist data_s("data_s", "data signal", x, mass_s);
  RooHistPdf histpdf_s("histpdf_s","histpdf_s", x, data_s);
  RooRealVar Xp("Xp", "Xp", 650.,850.);
  RooRealVar sP("sP", "sP", 50., 150.);
  RooRealVar xi("xi", "xi",-2.,0.);
  RooRealVar rho1("rho1", "rho1", -0.2,0.2);
  RooRealVar rho2("rho2", "rho2", -1.,1.);
  RooBukinPdf buk_s("buk_s","buk_s", x, Xp, sP, xi, rho1, rho2);
  std::cout << "######## FIT BUKIN  ###########" << std::endl;
  buk_s.fitTo(data_s);
  

  //  w.factory("RooCBShape:sig_pdf(x[110.,150.], mean[125.,120.,130.], sigma[3.,1.,5.], alpha[-5.,-30.,0.],n[0.1,0.,1000.])");

  RooRealVar mean("mean", "mean", 710, 500, 900);
  RooRealVar sigma("sigma", "sigma", 60, 0,100);
  RooRealVar alpha("alpha", "alpha", -2, -10,10);
  RooRealVar n("n", "n", 2, -10,10);
  RooCBShape cb_s("cb_s", "Crystal Ball Function", x, mean, sigma, alpha, n); 
  std::cout << "######## FIT Crystal Ball  ###########" << std::endl;
  //cb_s.fitTo(data_s);


  TH1F* mass_b = (TH1F*)fs->Get("background_BTag_MT_MassFSR");

  if( mass_b==0 ){
    cout << "Ho background histogram!" << endl;
    fs->Close();
    return;
  }
  //mass_b->Rebin(2);

  RooDataHist data_b("data_b", "data signal", x, mass_b);
  RooRealVar c("c","c",-20,20);
  RooExponential exp_b("exp_b","exp_b",x,c);
  //exp_b.fitTo(data_b);

  RooRealVar a0("a0","a0",  0.,4000.);
  RooRealVar a1("a1","a1", -2000.,2000.);
  RooRealVar a2("a2","a2", -1000.,1000.);
  RooRealVar a3("a3","a3", -100.,100.);
  RooRealVar a4("a4","a4",-200.,200.);
  RooRealVar a5("a5","a5",-10.,10.);
  RooRealVar a6("a6","a6",-10.,10.);
  RooBernstein ch_b("ch_b","ch_b",x,RooArgList(a0,a1,a2,a3,a4,a5/*,a6*/));
  std::cout << "######## FIT Pol 6  ###########" << std::endl;
  ch_b.fitTo(data_b);

  TCanvas* c1 = new TCanvas("c1","c1",1200,400);
  c1->Divide(2);

  TLegend* leg_s = new TLegend(0.55,0.65,0.80,0.88, "","brNDC");
  leg_s->SetFillStyle(0);
  leg_s->SetBorderSize(0);
  leg_s->SetTextSize(0.03);
  leg_s->SetFillColor(10);

  RooPlot* frame_s = x.frame();
  frame_s->SetName("frame_s");
  frame_s->SetTitle("Signal: Bukin function (Red), CB (Orange)");
  //  frame_s->SetTitle("Signal: CB function");
  data_s.plotOn(frame_s, Name("data"));
  buk_s.plotOn(frame_s, LineColor(kRed), Name("model"));
  cb_s.plotOn(frame_s, LineColor(kOrange));
  c1->cd(1);
  frame_s->Draw();
  double chi2_s = frame_s->chiSquare("model","data", 5);
  cout << chi2_s << endl;
  leg_s->SetHeader(Form("#splitline{Range: [%.0f,%.0f]}{#chi^{2}/ndof = %.3f}", x.getMin(), x.getMax(), 
		      chi2_s));
  leg_s->Draw();

  TLegend* leg_b = new TLegend(0.55,0.65,0.80,0.88, "","brNDC");
  leg_b->SetFillStyle(0);
  leg_b->SetBorderSize(0);
  leg_b->SetTextSize(0.03);
  leg_b->SetFillColor(10);

  RooPlot* frame_b = x.frame();
  frame_b->SetName("frame_b");
  frame_b->SetTitle("Background: 5th order polynomial");
  data_b.plotOn(frame_b,Name("data"));
  ch_b.plotOn(frame_b,  LineColor(kBlue), Name("model"));
  c1->cd(2);
  frame_b->Draw();
  double chi2_b = frame_b->chiSquare("model","data", 6);
  cout << chi2_b << endl;
  leg_b->SetHeader(Form("#splitline{Range: [%.0f,%.0f]}{#chi^{2}/ndof = %.3f}", x.getMin(), x.getMax(), 
			chi2_b));
  leg_b->Draw();

  RooWorkspace *w = new RooWorkspace("w","workspace") ;

  Xp.setConstant();
  sP.setConstant();
  xi.setConstant();
  rho1.setConstant();
  rho2.setConstant();

  w->import(cb_s);
  w->import(buk_s);
  w->import(histpdf_s);
  w->import(ch_b);
  w->import(data_b);
  w->import(data_s);

  RooDataHist* toy = ch_b.generateBinned(x, data_b.sumEntries());
  toy->SetName("signalX10");
  RooDataHist* toyX10 = buk_s.generateBinned(x, data_s.sumEntries()*10.);  
  toy->add( *toyX10 );
  w->import(*toy);
  //RooPlot* frame_toy = x.frame();  
  //toy->plotOn(frame_toy);
  //frame_toy->Draw();

  RooRealVar ns1("buk_s_norm", "signal norm", data_s.sumEntries());
  RooRealVar ns2("histpdf_s_norm", "signal norm", data_s.sumEntries());
  RooRealVar nb("ch_b_norm", "bkg norm", data_b.sumEntries());
  w->import(ns1);
  w->import(ns2);
  w->import(nb);

  // Print workspace contents
  w->Print() ;

  // Save the workspace into a ROOT file
  w->writeToFile("Xbb_workspace.root") ;

  cout << "Signal yield: " << data_s.sumEntries() << endl;
  cout << "Background yield: " << data_b.sumEntries() << endl;
  
  gDirectory->Add(w) ;
 
}
