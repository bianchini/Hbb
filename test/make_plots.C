#include "THStack.h"
#include "TH1F.h"
#include "TMath.h"
#include "TFile.h"
#include <vector>
#include <iostream>
#include "TCanvas.h"
#include "TLegend.h"
#include "TPad.h"
#include "TGaxis.h"

#include <map>

#define SAVE true

#define BLIND false

using namespace std;

const double KFACTOR = 1.45;

void plot(TString dir_name, TString h_name, TString postfix="", 
	  TString option_signal="HIST",  TString option_bkg="PE", TString option_data="PE", TString option_shape="", 
	  TString out_name="plot", TString version="V2"){
  
  TFile* out = TFile::Open("plots/"+version+"/"+out_name+".root", "UPDATE");

  THStack* s = new THStack("stack_background_"+h_name,"");
  
  TLegend* leg = new TLegend(0.55,0.65,0.80,0.88, "","brNDC");
  leg->SetHeader("Selection: "+dir_name+", L=2.54 fb^{-1}");
  leg->SetFillStyle(0);
  leg->SetBorderSize(0);
  leg->SetTextSize(0.03);
  leg->SetFillColor(10);

  vector<TString> samples = {
    "Run2015D",
    "HT100to200", 
    "HT200to300", 
    "HT300to500", 
    "HT500to700", 
    "HT700to1000", 
    "HT1000to1500", 
    "HT1500to2000", 
    "HT2000toInf",
    "M750",
    "TT_ext3"
    //"Spin0_M650",
    //"Spin0_M800",
    //"Spin0_M950",
    //"Spin0_M1400"
  };
  
  TH1F* signal = 0;
  map<TString, TH1F*> signals;
  for(unsigned int ss = 0 ; ss < samples.size(); ++ss){   
    if( string(samples[ss].Data()).find("Spin")!=string::npos || samples[ss]=="M750") 
      signals[samples[ss]] = 0;
  }

  TH1F* data = 0;
  TH1F* background = 0;
  TH1F* top = 0;
  TH1F* qcd = 0;

  vector<TFile*> open_files;
  for(unsigned int ss = 0 ; ss < samples.size(); ++ss){
    TString sample = samples[ss];
    TFile* f = TFile::Open("./plots/"+version+"/"+sample+".root", "READ");
    if(f==0 || f->IsZombie()){
      cout << "Cannot find file" << endl;
      continue;
    }
    open_files.push_back(f);
    float count = ((TH1F*)f->Get("Count"))->GetBinContent(1);
    TH1F* h_sample = (TH1F*)f->Get(dir_name+h_name);
    if(h_sample!=0){

      // rebin mass plots in CR...
      if( string(dir_name.Data()).find("Lep")!=string::npos && 
	  string(h_name.Data()).find("_Mass")!=string::npos )
	h_sample->Rebin(10);

      // first deal with data
      if(sample=="Run2015D"){
	data = (TH1F*)h_sample->Clone("data_"+h_name);
	data->SetMarkerColor(kBlack);
	data->SetLineColor(kBlack);
	data->SetMarkerSize(1.2);
	data->SetMarkerStyle(kFullCircle);
	data->SetFillColor(0);
	cout << ss << ", " << h_sample->Integral() << "==>" << data->Integral() << endl;
	continue;
      }

      h_sample->Scale(1./count);

      // then with signal
      if(string(sample.Data()).find("Spin")!=string::npos || sample=="M750"){
	signal = (TH1F*)h_sample->Clone("signal_"+h_name+"_"+sample+option_shape);
	signal->SetLineColor(kRed);
	signal->SetLineStyle(kDashed);
	signal->SetLineWidth(3);
	signals[sample] = signal;
	cout << ss << ", " << h_sample->Integral() << "==>" << signal->Integral() << endl;
	continue;
      }

      // this is background
      if(string(sample.Data()).find("HT")!=string::npos){
	h_sample->Scale(KFACTOR);
	h_sample->SetFillColor(ss+30);
	h_sample->SetLineColor(ss+30);
      }
      if(string(sample.Data()).find("TT_")!=string::npos){
	h_sample->SetFillColor(kMagenta);
	h_sample->SetLineColor(kMagenta);
      }
	

      h_sample->SetLineWidth(0);
      h_sample->SetFillStyle(1001);
      s->Add(h_sample);

      if(string(sample.Data()).find("HT")!=string::npos){
	if(qcd==0){
	  qcd = (TH1F*)h_sample->Clone("qcd_"+h_name);
	  qcd->SetLineColor(kBlack);
	  qcd->SetLineWidth(2);
	  qcd->SetFillColor(0);
	  cout << ss << ", " << h_sample->Integral() << "==>" << qcd->Integral() << endl;
	  leg->AddEntry(qcd, Form("Multi-jet, K-factor=%.1f", KFACTOR), "F");
	}
	else{
	  qcd->Add(h_sample, 1.0);
	  cout << ss << ", " << h_sample->Integral() << "==>" << qcd->Integral() << endl;
	}
      }

      if(string(sample.Data()).find("TT_")!=string::npos){
	if(top==0){
          top = (TH1F*)h_sample->Clone("top_"+h_name);
          top->SetLineColor(kMagenta);
          top->SetLineWidth(2);
          top->SetFillColor(kMagenta);
	  top->SetFillColor(0);
          cout << ss << ", " << h_sample->Integral() << "==>" << top->Integral() << endl;
          leg->AddEntry(top, "Top", "F");
        }
        else{
          top->Add(h_sample, 1.0);
          cout << ss << ", " << h_sample->Integral() << "==>" << top->Integral() << endl;
        }
      }

      if(background==0){
	background = (TH1F*)h_sample->Clone("background_"+h_name);
	background->SetLineColor(kBlue);
	background->SetLineWidth(2);
	if( option_bkg!="TEXT" ){
	  background->SetMarkerStyle(kFullCircle);
	  background->SetMarkerSize(0.);
	  background->SetFillColor(kBlue);
	  background->SetFillStyle(3004);
	}
	else{
	  background->SetFillStyle(0); 
	}
	cout << ss << ", " << h_sample->Integral() << "==>" << background->Integral() << endl;
	leg->AddEntry(background, "Total background", "F");
      }
      else{
	background->Add(h_sample, 1.0);
      }

    }
    else{
      cout << "Cannot find histogram" << endl;
      continue;
    }
    //f->Close();
  }

  TCanvas* c = new TCanvas("c", "canvas", 800, 800);
  TPad* pad1 = new TPad("pad1", "pad1", 0, 0.3, 1, 1.0);
  pad1->SetBottomMargin(0); 
  pad1->SetGridx();  
  pad1->Draw();      
  pad1->cd();    

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

    for(std::map<TString,TH1F*>::iterator it = signals.begin(); it != signals.end(); ++it){
      if(option_shape=="Shape"){	
	it->second->Scale(background->Integral()/signal->Integral());
	leg->AddEntry(it->second, (it->first)+" normalised to Bkg.", "L");
	it->second->Draw(option_signal+"SAME");
      }
      else{
	leg->AddEntry(it->second,  (it->first)+", #sigma=1.0 pb", "L");
	it->second->Draw(option_signal+"SAME");
      }
    }
  }

  if(background!=0){
    if( option_bkg=="TEXT") 
      background->Draw("TEXTSAME");
    else
      background->Draw(option_bkg+"E2SAME");
  }
  if(data!=0){
    if(  BLIND && string(dir_name.Data()).find("Lep")==string::npos && 
	 (string(dir_name.Data()).find("Mass")!=string::npos || 
	  (string(dir_name.Data()).find("BTag")!=string::npos &&
	   string(h_name.Data()).find("Mass")!=string::npos)) ){
      data->Reset();
      data->Add(background, 1.0);
      leg->AddEntry(data, "Data = MC (blinded)", "P");
      data->Draw(option_data+"SAME");
    }
    else{
      data->Draw(option_data+"SAME");
      leg->AddEntry(data, "Data", "P");
    }
  }
  if(s->GetHistogram()){
    s->GetHistogram()->GetYaxis()->SetTitleSize(20);
    s->GetHistogram()->GetYaxis()->SetTitleFont(43);
    s->GetHistogram()->GetYaxis()->SetTitleOffset(1.55);
  }
  TGaxis *axis = new TGaxis( -5, 20, -5, 220, 20,220,510,"");
  axis->SetLabelFont(43); 
  axis->SetLabelSize(15);
  axis->Draw();
  leg->Draw();

  c->cd(); 
  TPad *pad2 = new TPad("pad2", "pad2", 0, 0.05, 1, 0.3);
  pad2->SetTopMargin(0);
  pad2->SetBottomMargin(0.2);
  pad2->SetGridx();   
  pad2->SetGridy(); 
  pad2->Draw();
  pad2->cd();       

  // Define the ratio plot
  if(data!=0 || background!=0){
    TH1F *hratio = 0;
    if(data!=0)
      hratio = (TH1F*)data->Clone("data_clone");
    else
      hratio = (TH1F*)background->Clone("data_clone");
    hratio->SetLineColor(kBlack);
    hratio->SetMinimum(0.);  // Define Y ..
    hratio->SetMaximum(2); // .. range
    hratio->Sumw2();
    hratio->SetStats(0);      // No statistics on lower plot
    if(background!=0)
      hratio->Divide(background);
    hratio->SetMarkerStyle(21);
    hratio->Draw("ep"); 
    hratio->SetTitle(""); // Remove the ratio title

    // Y axis ratio plot settings
    hratio->GetYaxis()->SetTitle("data/MC");
    hratio->GetYaxis()->SetNdivisions(505);
    hratio->GetYaxis()->SetTitleSize(20);
    hratio->GetYaxis()->SetTitleFont(43);
    hratio->GetYaxis()->SetTitleOffset(1.55);
    hratio->GetYaxis()->SetLabelFont(43); // Absolute font size in pixel (precision 3)
    hratio->GetYaxis()->SetLabelSize(15);
    // X axis ratio plot settings
    hratio->GetXaxis()->SetTitle(h_name);
    hratio->GetXaxis()->SetTitleSize(20);
    hratio->GetXaxis()->SetTitleFont(43);
    hratio->GetXaxis()->SetTitleOffset(4.);
    hratio->GetXaxis()->SetLabelFont(43); // Absolute font size in pixel (precision 3)
    hratio->GetXaxis()->SetLabelSize(15);
  }


  out->cd();
  s->Write("", TObject::kOverwrite);
  if(signal!=0){
    for(std::map<TString,TH1F*>::iterator it = signals.begin(); it != signals.end(); ++it)
      it->second->Write("", TObject::kOverwrite);
  }
  if(background!=0) background->Write("", TObject::kOverwrite);
  if(data!=0) data->Write("", TObject::kOverwrite);
  out->Close();

  if(SAVE){
    //out->Close();
    if(option_shape=="Shape")
      pad1->SetLogy(0);
    else
      pad1->SetLogy(1);
    c->SaveAs("plots/"+version+"/"+h_name+postfix+".png");
    for(unsigned int of = 0; of < open_files.size() ; ++of)
      open_files[of]->Close();
    delete pad1;
    delete pad2;
    delete axis;
    delete c;
  }
}

void plot_all(){

  vector<TString> dirs = {
    //"Vtype",
    //"HLT",
    //"HLT_Offline_OR",
    //"HLT_Offline_AND",
    //"BTag_LT_lept",
    //"BTag_MT",
    //"BTag_nMT",
    //"BTag_LT",
    //"BTag_TT",
    //"Mass"
    "Had_MT_MinPt200_DH1p6",
    "Had_MT_MinPt150_DH1p6",
    "Had_MT_MinPt175_DH1p6",
    "Lep_LT_MinPt200_DH2p0",
    "Lep_LT_MinPt150_DH2p0",
    "Lep_LT_MinPt175_DH2p0",
    "Had_MT_MinPt200_DH2p0",
    "Had_MT_MinPt150_DH2p0",
    "Had_MT_MinPt175_DH2p0"
  };

  vector<TString> hists = {
    "MinJetPt",
    "MaxJetPt",
    "Mass",
    "MassFSR",
    "MassAK08",
    "Pt",
    "Eta",
    "DeltaEta",
    "DeltaPhi",
    "MaxJetCSV",
    "MinJetCSV",
    "Vtype",
    "njet30",
    "njet50",
    "njet70",
    "njet100",
    "MET",
    "PtBalance",
    //"MaxJetPtoMass",
    //"MinJetPtoMass",
    "MaxEta"
  };

  plot("All/","All_lheHT");
  plot("","CutFlow", "", "TEXT", "TEXT", "PE");

  for(unsigned int d = 0 ; d < dirs.size(); ++d){
    for(unsigned int h = 0 ; h < hists.size(); ++h){
      plot(dirs[d]+"/", dirs[d]+"_"+hists[h]);
      plot(dirs[d]+"/", dirs[d]+"_"+hists[h], "_shape", "HIST", "PE", "PE", "Shape");
    }
  }
}
