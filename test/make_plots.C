#include "THStack.h"
#include "TH1F.h"
#include "TMath.h"
#include "TFile.h"
#include<vector>
#include<iostream>
#include "TCanvas.h"
#include "TLegend.h"


#define SAVE false

using namespace std;

void plot(TString dir_name, TString h_name, TString postfix="", TString option1="HIST",  TString option2="PE", TString option3="", TString out_name="plot"){
  
  TFile* out = TFile::Open(out_name+".root", "UPDATE");

  THStack* s = new THStack("stack_background_"+h_name,"");
  
  TLegend* leg = new TLegend(0.64,0.75,0.80,0.88, "","brNDC");
  leg->SetHeader("Selection: "+dir_name+", L=2.5 fb^{-1}");
  leg->SetFillStyle(0);
  leg->SetBorderSize(0);
  leg->SetTextSize(0.03);
  leg->SetFillColor(10);

  vector<TString> samples = {
    "HT100to200", 
    "HT200to300", 
    "HT300to500", 
    "HT500to700", 
    "HT700to1000", 
    "HT1000to1500", 
    "HT1500to2000", 
    "HT2000toInf",
    "M750"
  };
  
  TH1F* signal = 0;
  TH1F* background = 0;

  vector<TFile*> open_files;
  for(unsigned int ss = 0 ; ss < samples.size(); ++ss){
    TString sample = samples[ss];
    TFile* f = TFile::Open("./"+sample+".root", "READ");
    if(f==0 || f->IsZombie()){
      cout << "Cannot find file" << endl;
      continue;
    }
    open_files.push_back(f);
    float count = ((TH1F*)f->Get("Count"))->GetBinContent(1);
    TH1F* h_sample = (TH1F*)f->Get(dir_name+h_name);
    if(h_sample!=0){
      h_sample->Scale(1./count);
      if(string(sample.Data()).find("HT")==string::npos){
	signal = (TH1F*)h_sample->Clone("signal_"+h_name);
	signal->SetLineColor(kRed);
	signal->SetLineStyle(kDashed);
	signal->SetLineWidth(3);
	cout << ss << ", " << h_sample->Integral() << "==>" << signal->Integral() << endl;
	continue;
      }
      h_sample->SetFillColor(ss+30);
      h_sample->SetLineColor(ss+30);
      h_sample->SetLineWidth(0);
      h_sample->SetFillStyle(1001);
      s->Add(h_sample);
      if(background==0){
	background = (TH1F*)h_sample->Clone("background_"+h_name);
	background->SetMarkerColor(kBlack);
	background->SetMarkerSize(1.2);
	background->SetMarkerStyle(kFullCircle);
	background->SetFillColor(0);
	cout << ss << ", " << h_sample->Integral() << "==>" << background->Integral() << endl;
	leg->AddEntry(background, "Total background", "P");
      }
      else{
	background->Add(h_sample, 1.0);
	cout << ss << ", " << h_sample->Integral() << "==>" << background->Integral() << endl;
      }
    }
    else{
      cout << "Cannot find histogram" << endl;
      continue;
    }
    //f->Close();
  }

  s->Draw("HIST");
  if(signal!=0)
    s->SetMinimum(TMath::Max(signal->GetMinimum()*0.5,0.1));
  if(background!=0)
    s->SetMaximum(background->GetMaximum()*1.3);
  if(s->GetHistogram()){
    s->GetHistogram()->SetXTitle(h_name);
    s->GetHistogram()->SetTitle(dir_name);
  }

  if(signal!=0){
    if(option3=="Shape"){
      signal->Scale(background->Integral()/signal->Integral());
      leg->AddEntry(signal, "X(750) normalised to Bkg.", "L");
      signal->Draw(option1+"SAME");
    }
    else{
      leg->AddEntry(signal, "X(750), #sigma=1.0 pb", "L");
      signal->Draw(option1+"SAME");
    }
  }
  if(background!=0) background->Draw(option2+"SAME");
  out->cd();
  s->Write("", TObject::kOverwrite);
  if(signal!=0) signal->Write("", TObject::kOverwrite);
  if(background!=0) background->Write("", TObject::kOverwrite);
  out->Close();

  leg->Draw();

  if(SAVE){
    //out->Close();
    if(option3=="Shape")
      gPad->SetLogy(0);
    else
      gPad->SetLogy(1);
    gPad->SaveAs("plots/"+h_name+postfix+".png");
    for(unsigned int of = 0; of < open_files.size() ; ++of)
      open_files[of]->Close();
  }
}

void plot_all(){

  vector<TString> dirs = {
    //"Vtype",
    //"HLT",
    //"HLT_Offline_OR",
    //"HLT_Offline_AND",
    //"BTag_MT",
    "BTag_TT"
    //"Mass"
  };

  vector<TString> hists = {
    //"MinJetPt",
    //"MaxJetPt",
    //"Mass",
    "MassFSR"
    //"Pt",
    //"Eta",
    //"DeltaEta",
    //"DeltaPhi",
    //"MaxJetCSV",
    //"MinJetCSV",
    //"Vtype",
    //"njet30",
    //"njet50",
    //"njet70",
    //"njet100",
    //"MET",
    //"PtBalance",
    //"MaxJetPtoMass",
    //"MinJetPtoMass",
    //"MaxEta"
  };

  plot("All/","All_lheHT");
  plot("","CutFlow", "", "TEXT", "TEXT");

  for(unsigned int d = 0 ; d < dirs.size(); ++d){
    for(unsigned int h = 0 ; h < hists.size(); ++h){
      plot(dirs[d]+"/", dirs[d]+"_"+hists[h]);
      plot(dirs[d]+"/", dirs[d]+"_"+hists[h], "_shape", "HIST", "PE", "Shape");
    }
  }
}
