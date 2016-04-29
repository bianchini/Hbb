from WMCore.Configuration import Configuration

config = Configuration()

config.section_("General")
config.General.requestName   = 
config.General.transferLogs = True

config.section_("JobType")
config.JobType.pluginName  = 'Analysis'
config.JobType.psetName  = 

config.section_("Data")
config.Data.inputDataset = 
config.Data.inputDBS = 'phys03'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 1
config.Data.publication = True

# This string is used to construct the output dataset name
config.Data.outputDatasetTag  = 'MiniAODv2' #something you like

config.section_("Site")
config.Site.storageSite = 'T2_CH_CSCS'