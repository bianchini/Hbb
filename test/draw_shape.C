{

  TFile* f = TFile::Open("plots/V5/Xbb_workspace_Had_MT_MinPt100_DH1p6_MassFSR_400to1200.root");

  RooWorkspace* w = (RooWorkspace*)f->Get("Xbb_workspace");

  RooAbsPdf* pdf = (RooAbsPdf*)w->pdf("buk_pdf_sgn_Spin0_M1200");

  //cout << string(pdf->normRange()) << endl;

  RooRealVar* x = (RooRealVar*)w->var("x");

  for(int i = 0 ; i < 100; ++i){
    x->setVal(400+10*i);
    cout << 400+10*i << "GeV " << pdf->getVal() << endl;;
  }

  pdf->setNormRange("MassFSR");
  RooPlot* frame = x->frame(RooFit::Range(400., 1200.));
  pdf->plotOn(frame);

  frame->Draw();
  
}
