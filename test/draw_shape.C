
  {

    TFile* f = TFile::Open("plots/V7/Xbb_workspace_Had_MT_MinPt100_DH1p6_MassFSR_425to800.root");
    
    RooWorkspace* w = (RooWorkspace*)f->Get("Xbb_workspace");

    RooAbsPdf* pdf = (RooAbsPdf*)w->pdf("buk_pdf_sgn_Spin0_M600");

    //cout << string(pdf->normRange()) << endl;

    RooRealVar* x = (RooRealVar*)w->var("x");

    for(int i = 0 ; i < 100; ++i){
      x->setVal(400+10*i);
      cout << 400+10*i << "GeV " << pdf->getVal() << endl;;
    }
    
    pdf->setNormRange("MassFSR");
    RooPlot* frame = x->frame(RooFit::Range(425., 800.));
    pdf->plotOn(frame);

    frame->Draw();
  
  }
