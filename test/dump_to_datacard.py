#!/usr/bin/env python

from sys import argv
import commands
import time
import re
import os
import string
from os import listdir
import ROOT

def make_datacard( version, ws_name, cat, mass, x_range, pdf_sgn, pdf_bkg, data_obs ):

    outname = ws_name+'_'+cat+'_'+mass+'_'+x_range
    postfix = '_'+pdf_sgn+'_'+pdf_bkg
    ws_file = ROOT.TFile.Open('plots/'+version+'/'+outname+'.root')
    ws = ws_file.Get(ws_name)
    obs = ws.data(data_obs).sumEntries()

    f = open( 'plots/'+version+'/'+outname+postfix+'.txt','w')
    f.write('imax 1 number of bins\n')
    f.write('jmax 1 number of processes minus 1\n')
    f.write('kmax * number of nuisance parameters\n')
    f.write('--------------------------------------------------------------\n')
    f.write('shapes bkg       '+cat+'      '+outname+'.root '+ws_name+':'+pdf_bkg+'\n')
    f.write('shapes sgn       '+cat+'      '+outname+'.root '+ws_name+':'+pdf_sgn+'\n')
    f.write('shapes data_obs  '+cat+'      '+outname+'.root '+ws_name+':'+data_obs+'\n')
    f.write('--------------------------------------------------------------\n')
    f.write('bin  '+cat+'\n')
    f.write(('observation  %.0f' % obs)+'\n')
    f.write('--------------------------------------------------------------\n')
    f.write('bin               '+cat+'               '+cat+'\n')
    f.write('process           sgn                bkg\n')
    f.write('process            -1                  1\n')
    f.write('rate              1.0               1.0\n')
    f.write('--------------------------------------------------------------\n')
    f.write('sgn_unc    lnN    1.10           -\n')

    if ws.var('CSV_shift_sgn') != None:
        f.write('CMS_btag   lnN   '+("%.2f" % (1+ws.var('CSV_shift_sgn').getVal()))+'        -\n')  
        
    if pdf_bkg=='mass_pdf_bkg':
        for param in ["p1_bkg","p2_bkg","p3_bkg"]:
            val =  ws.var(param).getVal()
            f.write(param+'  param  '+( "%.2E" % val) + '  10.0\n')
    elif pdf_bkg=='pol_pdf_bkg':
        for param in ["a0_bkg","a1_bkg","a2_bkg", "a3_bkg", "a4_bkg", "a5_bkg"]:
            val =  ws.var(param).getVal()
            f.write(param+'  param  '+( "%.2E" % val) + '  1.0\n')
    elif pdf_bkg=='exp_pdf_bkg':
        for param in ["c_bkg"]:
            val =  ws.var(param).getVal()
            f.write(param+'  param  '+( "%.2E" % val) + '  1.0\n')

    if pdf_sgn=='buk_pdf_sgn':
        if not ws.var('Xp_sgn').getAttribute("Constant"):
            f.write('Xp_sgn  param  '+( "%.1E" % ws.var('Xp_sgn').getVal()) + ("  %.1f" % ws.var('Xp_shift_sgn').getVal()) + '\n')
        if not ws.var('sP_sgn').getAttribute("Constant"):
            f.write('sP_sgn  param  '+( "%.1E" % ws.var('sP_sgn').getVal()) + ("  %.1f" % ws.var('sP_shift_sgn').getVal()) + '\n')
        
    f.close()
    ws_file.Close()
    print 'Created datacard '+'plots/'+version+'/'+outname+postfix+'.txt'

########################################

for cat in [    
    'Had_MT_MinPt150_DH2p0', 
    'Had_MT_MinPt150_DH1p6',
    'Had_MT_MinPt150_DH1p1',
    'Had_MT_MinPt200_DH2p0', 
    'Had_MT_MinPt200_DH1p6',
    'Had_MT_MinPt200_DH1p1',
    'Had_LT_MinPt150_DH2p0', 
    'Had_LT_MinPt150_DH1p6',
    'Had_LT_MinPt150_DH1p1',
    'Had_LT_MinPt200_DH2p0', 
    'Had_LT_MinPt200_DH1p6',
    'Had_LT_MinPt200_DH1p1'
    ]:
    for pdf in [
        'mass_pdf_bkg'
        ]:
        for x_range in [
            '550to1200'
            ]:
            for mass in [
                'MassFSR', 
                ]:
                #make_datacard('V2', 'Xbb_workspace', cat, mass, x_range, 'buk_pdf_sgn', pdf, 'data_bkg')
                make_datacard('V2', 'Xbb_workspace', cat, mass, x_range, 'buk_pdf_sgn', pdf, 'data_obs')

