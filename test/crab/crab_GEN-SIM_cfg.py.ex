from WMCore.Configuration import Configuration
from CRABClient.UserUtilities import getUsernameFromSiteDB

config = Configuration()
config.section_("General")
config.General.requestName =
config.General.transferLogs = True

config.section_("JobType")
config.JobType.pluginName  = 'PrivateMC'
config.JobType.psetName =

config.section_("Data")
config.Data.splitting = 'EventBased'
config.Data.unitsPerJob = 
config.Data.totalUnits  =
config.Data.publication = True

config.Data.outputDatasetTag  = 'GEN-SIM'
config.Data.outLFNDirBase = '/store/user/%s/' % (getUsernameFromSiteDB())
config.Data.outputPrimaryDataset  = 

config.section_("Site")
config.Site.storageSite = 'T2_CH_CSCS'
