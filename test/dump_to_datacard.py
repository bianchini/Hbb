#!/usr/bin/env python

from sys import argv
import commands
import time
import re
import os
import string
from os import listdir
import ROOT

def make_datacard( version='V3', ws_name='Xbb_workspace', 
                   cat='Had_LT_MinPt150_DH1p6', mass='MassFSR', x_range='550to1200', sgn='Spin0_M650',
                   pdf_sgn='buk', pdf_bkg='dijet', data_obs='data_obs' ):

    outname = ws_name+'_'+cat+'_'+mass+'_'+x_range
    postfix = '_'+pdf_sgn+'_'+pdf_bkg+'_'+sgn
    ws_file = ROOT.TFile.Open('plots/'+version+'/'+outname+'.root')
    ws = ws_file.Get(ws_name)
    obs = ws.data(data_obs).sumEntries()

    f = open( 'plots/'+version+'/'+outname+postfix+'.txt','w')
    f.write('imax 1 number of bins\n')
    f.write('jmax 1 number of processes minus 1\n')
    f.write('kmax * number of nuisance parameters\n')
    f.write('--------------------------------------------------------------\n')
    f.write('shapes bkg          '+cat+'     '+outname+'.root '+ws_name+':'+pdf_bkg+'_pdf_bkg\n')
    f.write('shapes '+sgn+'   '+cat+'     '+outname+'.root '+ws_name+':'+pdf_sgn+'_pdf_sgn_'+sgn+'\n')
    f.write('shapes data_obs     '+cat+'      '+outname+'.root '+ws_name+':'+data_obs+'\n')
    f.write('--------------------------------------------------------------\n')
    f.write('bin          '+cat+'\n')
    f.write(('observation  %.0f' % obs)+'\n')
    f.write('--------------------------------------------------------------\n')
    f.write('bin               '+cat+'   '+cat+'\n')
    f.write('process           '+sgn+'                bkg\n')
    f.write('process            -1                       1  \n')
    f.write('rate              1.0                       1.0\n')
    f.write('--------------------------------------------------------------\n')
    f.write('sgn_unc    lnN    1.10                        -\n')

    sgn_norm = ws.var(pdf_sgn+'_pdf_sgn_'+sgn+'_norm').getVal()    
    if ws.var('CSV_shift_sgn_'+sgn) != None:
        f.write('CMS_btag   lnN   '+("%.2f" % (1+ws.var('CSV_shift_sgn_'+sgn).getVal()/sgn_norm))+'        -\n')  
        
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
            f.write('mean_sgn_'+sgn+'  param  '+( "%.3E" % mean) + ("  %.1f" % d_mean) + '\n')
        if not ws.var('sigma_sgn_'+sgn).getAttribute("Constant"):
            f.write('sigma_sgn_'+sgn+'  param  '+( "%.2E" % sigma) + ("  %.1f" % d_sigma) + '\n')

    f.close()
    ws_file.Close()
    print 'Created datacard '+'plots/'+version+'/'+outname+postfix+'.txt'

########################################

for cat in [    
    'Had_LT_MinPt150_DH1p6',
    ]:
    for pdf in [
        'dijet',
        ]:
        for sgn in [
            'Spin0_M650',
            'Spin0_M750',
            'Spin0_M850',
            'Spin0_M1000',
            'Spin0_M1200',
            ]:
            for x_range in [
                '550to1200'
                ]:
                for mass in [
                    'MassFSR', 
                    ]:
                    make_datacard('V3', 'Xbb_workspace', cat, mass, x_range, sgn, 'buk', pdf, 'data_obs')

