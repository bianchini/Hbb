#!/usr/bin/env python

from sys import argv
import commands
import time
import re
import os
import string
from os import listdir
import ROOT

def make_datacard( ws_name='Xbb_workspace', 
                   cat='Had_LT_MinPt150_DH1p6', mass='MassFSR', x_range='550to1200', sgn='Spin0_M650',
                   pdf_sgn='buk', pdf_bkg='dijet', data_obs='data_obs', save_dir='./plots/V4/' ):

    outname = ws_name+'_'+cat+'_'+mass+'_'+x_range
    postfix = '_'+pdf_sgn+'_'+pdf_bkg+'_'+sgn
    ws_file = ROOT.TFile.Open(save_dir+'/'+outname+'.root')
    ws = ws_file.Get(ws_name)
    obs = ws.data(data_obs).sumEntries()
    bias = ws.var('bias_sgn_'+sgn).getVal()

    f = open( save_dir+'/'+outname+postfix+'.txt','w')
    f.write('imax 1 number of bins\n')
    f.write('jmax 2 number of processes minus 1\n')
    f.write('kmax * number of nuisance parameters\n')
    f.write('--------------------------------------------------------------\n')
    f.write('shapes bkg          '+cat+'          '+outname+'.root '+ws_name+':'+pdf_bkg+'_pdf_bkg\n')
    f.write('shapes '+sgn+'   '+cat+'          '+outname+'.root '+ws_name+':'+pdf_sgn+'_pdf_sgn_'+sgn+'\n')
    f.write('shapes '+sgn+'_bias   '+cat+'     '+outname+'.root '+ws_name+':'+pdf_sgn+'_pdf_sgn_bias_'+sgn+'\n')
    f.write('shapes data_obs     '+cat+'          '+outname+'.root '+ws_name+':'+data_obs+'\n')
    f.write('--------------------------------------------------------------\n')
    f.write('bin          '+cat+'\n')
    f.write(('observation  %.0f' % obs)+'\n')
    f.write('--------------------------------------------------------------\n')
    f.write('bin               '+cat+'   '+cat+'   '+cat+'\n')
    f.write('process           '+sgn+'                '+sgn+'_bias                  bkg\n')
    f.write('process             0                       1                                2  \n')
    f.write('rate              1.0                       1e-06                            1.0\n')
    f.write('--------------------------------------------------------------\n')
    f.write('CMS_Xbb_trigger    lnN    1.10                       1.10                        -\n')
    f.write('signal_bias        lnN     -                         '+('%.2f' % (1.+bias))+'                        -\n')
    f.write('lumi_13TeV         lnN    1.027                      1.027                       -\n')

    sgn_norm = ws.var(pdf_sgn+'_pdf_sgn_'+sgn+'_norm').getVal()    
    if ws.var('CSV_shift_'+sgn) != None:
        f.write('CMS_btag           lnN    '+("%.2f" % (1+ws.var('CSV_shift_'+sgn).getVal()/sgn_norm))+'                       '+("%.2f" % (1+ws.var('CSV_shift_'+sgn).getVal()/sgn_norm))+'                      -\n')  
        
    if pdf_bkg=='dijet':
        for param in ['p1_bkg_'+pdf_bkg,'p2_bkg_'+pdf_bkg]:
            val =  ws.var(param).getVal()
            f.write(param+'  flatParam \n')

    mean = ws.var('mean_sgn_'+sgn).getVal()
    d_mean = ws.var('mean_shift_'+sgn).getVal()
    sigma = ws.var('sigma_sgn_'+sgn).getVal()
    d_sigma = ws.var('sigma_shift_'+sgn).getVal()

    if pdf_sgn=='buk':
        if not ws.var('mean_sgn_'+sgn).getAttribute("Constant"):
            f.write('mean_sgn_'+sgn+'   param  '+( "%.3E" % mean) + ("  %.1f" % d_mean) + '\n')
        if not ws.var('sigma_sgn_'+sgn).getAttribute("Constant"):
            f.write('sigma_sgn_'+sgn+'  param  '+( "%.2E" % sigma) + ("  %.1f" % d_sigma) + '\n')

    f.close()
    ws_file.Close()
    print 'Created datacard '+save_dir+'/'+outname+postfix+'.txt'

########################################

for cat_btag in [
    'Had_LT', 'Had_MT'
    ]:
    for cat_kin in [
        'MinPt150_DH1p6', 'MinPt150_DH2p0', 
        'MinPt180_DH1p6', 'MinPt180_DH2p0',
        ]:        
        for pdf in [
            'dijet',
            ]:
            for sgn in [
                #'Spin0_M650',
                'Spin0_M750',
                #'Spin0_M850',
                #'Spin0_M1000',
                #'Spin0_M1200',
                ]:
                for x_range in [
                    '550to1200'
                    ]:
                    for mass in [
                        'MassFSR', 
                        ]:
                        make_datacard('Xbb_workspace', cat_btag+"_"+cat_kin, mass, x_range, sgn, 'buk', pdf, 'data_bkg', './plots/V4/')
                        
