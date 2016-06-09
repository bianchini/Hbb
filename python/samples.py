
version = "V4"

pisa_lfn = "root://stormgf1.pi.infn.it:1094//store/user/arizzi/VHBBHeppyV21/"
cern_lfn = "root://188.184.38.46:1094//store/group/phys_higgs/hbb/ntuples/V21/user/arizzi/VHBBHeppyV21/"
xbb_lfn = "root://188.184.38.46:1094//store/group/phys_higgs/hbb/Xbb/"
#psi_lfn = "dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/bianchi/Hbb_Heppy/"
psi_lfn = "droot://t3dcachedb.psi.ch:1094//pnfs/psi.ch/cms/trivcat/store/user/bianchi/Hbb_Heppy/"

samples_V21 = {
  "Run2015D" : [cern_lfn+"/BTagCSV//VHBB_HEPPY_V21_BTagCSV__Run2015D-16Dec2015-v1/160317_132347/0000/", -1],
  "Run2015C" : [cern_lfn+"BTagCSV/VHBB_HEPPY_V21_BTagCSV__Run2015C_25ns-16Dec2015-v1/160318_133752/0000/", -1],
  "HT100to200" : [cern_lfn+"QCD_HT100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/VHBB_HEPPY_V21_QCD_HT100to200_TuneCUETP8M1_13TeV-madgraphMLM-Py8__fall15MAv2-pu25ns15v1_76r2as_v12-v1/160316_144616/0000/", 27990000],
  "HT200to300" : [cern_lfn+"/QCD_HT200to300_TuneCUETP8M1_13TeV-madgraphMLM-pythia8//VHBB_HEPPY_V21_QCD_HT200to300_TuneCUETP8M1_13TeV-madgraphMLM-Py8__fall15MAv2-pu25ns15v1_76r2as_v12-v1/160316_151338/0000/", 1712000.],
  "HT300to500" :   [cern_lfn+"QCD_HT300to500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/VHBB_HEPPY_V21_QCD_HT300to500_TuneCUETP8M1_13TeV-madgraphMLM-Py8__fall15MAv2-pu25ns15v1_76r2as_v12-v1/160321_090315/0000/",347700.],
  "HT500to700" :   [cern_lfn+"QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/VHBB_HEPPY_V21_QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-Py8__fall15MAv2-pu25ns15v1_76r2as_v12-v1/160316_144548/0000/", 32100.],
  "HT700to1000" :  [cern_lfn+"QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8//VHBB_HEPPY_V21_QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-Py8__fall15MAv2-pu25ns15v1_76r2as_v12-v1//160321_090740/0000/", 6831.],
  "HT1000to1500" : [cern_lfn+"QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/VHBB_HEPPY_V21_QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-Py8__fall15MAv2-pu25ns15v1_76r2as_v12-v1//160316_151306/0000/", 1207.],
  "HT1500to2000" : [cern_lfn+"QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/VHBB_HEPPY_V21_QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-Py8__fall15MAv2-pu25ns15v1_76r2as_v12-v1//160316_144454//0000/",119.9],
  "HT2000toInf" :  [cern_lfn+"QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8//VHBB_HEPPY_V21_QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-Py8__fall15MAv2-pu25ns15v1_76r2as_v12-v1//160316_144521/0000/", 25.24], 
  "TT_ext3" : [pisa_lfn+"TT_TuneCUETP8M1_13TeV-powheg-pythia8/VHBB_HEPPY_V21a_TT_TuneCUETP8M1_13TeV-powheg-Py8__fall15MAv2-pu25ns15v1_76r2as_v12_ext3-v1/160324_170631/0000/", 832.],
  "ST_t_top" : [cern_lfn+"ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1/VHBB_HEPPY_V21_ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-Py8_TuneCUETP8M1__fall15MAv2-pu25ns15v1_76r2as_v12-v1/160316_151136/0000/", 45.34],
  "ST_t_atop" : [cern_lfn+"ST_t-channel_top_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1/VHBB_HEPPY_V21_ST_t-channel_top_4f_leptonDecays_13TeV-powheg-Py8_TuneCUETP8M1__fall15MAv2-pu25ns15v1_76r2as_v12-v1/160316_145139/0000/", 26.98 ],
   "ST_tW_top" : [cern_lfn+"ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/VHBB_HEPPY_V21_ST_tW_top_5f_inclusiveDecays_13TeV-powheg-Py8_TuneCUETP8M1__fall15MAv2-pu25ns15v1_76r2as_v12-v1/160316_145310/0000/",  35.6],
  "ST_tW_atop" : [cern_lfn+"ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/VHBB_HEPPY_V21_ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-Py8_TuneCUETP8M1__fall15MAv2-pu25ns15v1_76r2as_v12-v1/160316_145243/0000/",  35.6],
  "Spin0_M650" : [xbb_lfn+"GluGluSpin0ToBBbar_W_1p0_M_650_TuneCUEP8M1_13TeV_pythia8/VHBB_HEPPY_F21_add_GluGluSpin0ToBBbar_W_1p0_M_650_TuneCUEP8M1_13TeV_Py8__bianchi-MiniAODv2-17d438ff51ec6b3cada9e499a5a978e0/160430_172522/0000/", 1.0],
  "Spin0_M750" : [xbb_lfn+"/GluGluSpin0ToBBbar_W_1p0_M_750_TuneCUEP8M1_13TeV_pythia8/VHBB_HEPPY_F21_add_GluGluSpin0ToBBbar_W_1p0_M_750_TuneCUEP8M1_13TeV_Py8__bianchi-MiniAODv2-17d438ff51ec6b3cada9e499a5a978e0/160430_172549/0000/", 1.0],
  "Spin0_M850" : [xbb_lfn+"GluGluSpin0ToBBbar_W_1p0_M_850_TuneCUEP8M1_13TeV_pythia8/VHBB_HEPPY_F21_add_GluGluSpin0ToBBbar_W_1p0_M_850_TuneCUEP8M1_13TeV_Py8__bianchi-MiniAODv2-17d438ff51ec6b3cada9e499a5a978e0/160430_172620/0000/", 1.0],
  "Spin0_M1000" : [xbb_lfn+"/GluGluSpin0ToBBbar_W_1p0_M_1000_TuneCUEP8M1_13TeV_pythia8/VHBB_HEPPY_F21_add_GluGluSpin0ToBBbar_W_1p0_M_1000_TuneCUEP8M1_13TeV_Py8__bianchi-MiniAODv2-17d438ff51ec6b3cada9e499a5a978e0/160430_172426/0000/", 1.0],
  "Spin0_M1200" : [xbb_lfn+"GluGluSpin0ToBBbar_W_1p0_M_1200_TuneCUEP8M1_13TeV_pythia8/VHBB_HEPPY_F21_add_GluGluSpin0ToBBbar_W_1p0_M_1200_TuneCUEP8M1_13TeV_Py8__bianchi-MiniAODv2-17d438ff51ec6b3cada9e499a5a978e0/160430_172456/0000/", 1.0],
  "Spin2_M650" : [xbb_lfn+"/RSGravitonToBBbar_kMpl01_M_650_TuneCUEP8M1_13TeV_pythia8/VHBB_HEPPY_F21_add_RSGravitonToBBbar_kMpl01_M_650_TuneCUEP8M1_13TeV_Py8__bianchi-MiniAODv2-17d438ff51ec6b3cada9e499a5a978e0/160430_173251/0000/", 1.0],
  "Spin2_M750" : [xbb_lfn+"RSGravitonToBBbar_kMpl01_M_750_TuneCUEP8M1_13TeV_pythia8/VHBB_HEPPY_F21_add_RSGravitonToBBbar_kMpl01_M_750_TuneCUEP8M1_13TeV_Py8__bianchi-MiniAODv2-17d438ff51ec6b3cada9e499a5a978e0/160430_173316/0000/", 1.0],
  "Spin2_M850" : [xbb_lfn+"RSGravitonToBBbar_kMpl01_M_850_TuneCUEP8M1_13TeV_pythia8/VHBB_HEPPY_F21_add_RSGravitonToBBbar_kMpl01_M_850_TuneCUEP8M1_13TeV_Py8__bianchi-MiniAODv2_v3-17d438ff51ec6b3cada9e499a5a978e0/160430_173345/0000/", 1.0],
  "Spin2_M1000" : [xbb_lfn+"RSGravitonToBBbar_kMpl01_M_1000_TuneCUEP8M1_13TeV_pythia8/VHBB_HEPPY_F21_add_RSGravitonToBBbar_kMpl01_M_1000_TuneCUEP8M1_13TeV_Py8__bianchi-MiniAODv2-17d438ff51ec6b3cada9e499a5a978e0/160501_082958/0000/", 1.0],
  "Spin2_M1200" : [xbb_lfn+"/RSGravitonToBBbar_kMpl01_M_1200_TuneCUEP8M1_13TeV_pythia8/VHBB_HEPPY_F21_add_RSGravitonToBBbar_kMpl01_M_1200_TuneCUEP8M1_13TeV_Py8__bianchi-MiniAODv2-17d438ff51ec6b3cada9e499a5a978e0/160501_082815/0000/", 1.0],
  #"M750" : ["root://eoscms.cern.ch//eos/cms/store/group/cmst3/user/degrutto/VHBBHeppyV21_add/RSGravitonTobb_kMpl001_M_750_Tune4C_13TeV_pythia8/VHBB_HEPPY_F21_add_RSGravitonTobb_kMpl001_M_750_Tune4C_13TeV_Py8__khurana-MINIAODSIM-17d438ff51ec6b3cada9e499a5a978e0/160405_155957/0000/", 1.0],
}

samples_pruned = {
 "HT100to200" : [psi_lfn+version+"/HT100to200/", 27990000],
 "HT200to300" : [psi_lfn+version+"/HT200to300/", 1712000.],
 "HT300to500" :   [psi_lfn+version+"/HT300to500/",347700.],
 "HT500to700" :   [psi_lfn+version+"/HT500to700/", 32100.],
 "HT700to1000" :  [psi_lfn+version+"/HT700to1000/", 6831.],
 "HT1000to1500" : [psi_lfn+version+"/HT1000to1500/", 1207.],
 "HT1500to2000" : [psi_lfn+version+"/HT1500to2000/",119.9],
 "HT2000toInf" :  [psi_lfn+version+"/HT2000toInf/", 25.24], 
 "M750" : [psi_lfn+version+"/M750/", 1.0],
 "Run2015D" : [psi_lfn+version+"/Run2015D/", -1],
 "Run2015C" : [psi_lfn+version+"/Run2015C/", -1],
 "Spin0_M650" : [psi_lfn+version+"/Spin0_M650/",1.0],
 "Spin0_M750" : [psi_lfn+version+"/Spin0_M750/",1.0],
 "Spin0_M850" : [psi_lfn+version+"/Spin0_M850/",1.0],
 "Spin0_M1000" : [psi_lfn+version+"/Spin0_M1000/",1.0],
 "Spin0_M1200" : [psi_lfn+version+"/Spin0_M1200/",1.0],
 "Spin2_M650" : [psi_lfn+version+"/Spin2_M650/",1.0],
 "Spin2_M750" : [psi_lfn+version+"/Spin2_M750/",1.0],
 "Spin2_M850" : [psi_lfn+version+"/Spin2_M850/",1.0],
 "Spin2_M1000" : [psi_lfn+version+"/Spin2_M1000/",1.0],
 "Spin2_M1200" : [psi_lfn+version+"/Spin2_M1200/",1.0],
 "TT_ext3" : [psi_lfn+version+"/TT_ext3/",832.],
 "ST_t_top" : [psi_lfn+version+"/ST_t_top/", 45.34],
 "ST_t_atop" : [psi_lfn+version+"/ST_t_atop/", 26.98],
 "ST_tW_top" : [psi_lfn+version+"/ST_tW_top/", 35.6],
 "ST_tW_atop" : [psi_lfn+version+"/ST_tW_atop/", 35.6],
}

