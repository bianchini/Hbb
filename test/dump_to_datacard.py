#!/usr/bin/env python

from sys import argv
import commands
import time
import re
import os
import string
from os import listdir
import ROOT

import sys
sys.path.append('./')
sys.path.append('../python/')

from parameters_cfi import *
from utilities import get_bias, get_sliding_edges

def make_datacard( ws_name='Xbb_workspace', 
                   cat='Had_LT_MinPt150_DH1p6', mass='MassFSR', x_range='550to1200', sgn='Spin0_M650',
                   pdf_sgn='buk', pdf_bkg='dijet', data_obs='data_obs', save_dir='./plots/V4/', is_data=True ):

    FTestCfg = {}
    if is_data:
        FTestCfg = FTestCfg_data
    else:
        FTestCfg = FTestCfg_mc  

    outname = ws_name+'_'+cat+'_'+mass+'_'+x_range
    postfix = '_'+pdf_sgn+'_'+pdf_bkg+'_'+sgn
    ws_file = ROOT.TFile.Open(save_dir+'/'+outname+'.root')

    if ws_file==None or ws_file.IsZombie():
        return

    ws = ws_file.Get(ws_name)
    obs = ws.data(data_obs).sumEntries()
    #bias = ws.var('bias_sgn_'+sgn).getVal()
    bias = ("%.2f" % get_bias(mass=sgn[7:], pdf_name=pdf_bkg, deg=FTestCfg[pdf_bkg]['MaxOrder'][x_range], is_data=is_data) )

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
    f.write('rate              1.0                       1.0                              1.0\n')
    f.write('--------------------------------------------------------------\n')
    #f.write('CMS_Xbb_trigger_kin     lnN    1.01                       1.01                        -\n')
    f.write('CMS_Xbb_trigger_btag    lnN    1.05                       1.05                        -\n')
    f.write('lumi_13TeV              lnN    1.027                      1.027                       -\n')
    f.write('pdf_gg_13TeV            lnN    1.06                       1.06                        -\n')

    sgn_norm = ws.var(pdf_sgn+'_pdf_sgn_'+sgn+'_norm').getVal()    

    if ws.var('CSV_shift_'+sgn) != None:
        shift = 1 + ws.var('CSV_shift_'+sgn).getVal()/sgn_norm
        print "\tadding CMS_btag....lnN", shift
        if (shift-1)>=0.01:
            f.write('CMS_btag                lnN    '+("%.2f" % shift)+'                       '+("%.2f" % shift)+'                      -\n')      
    if ws.var('HLTKin_shift_'+sgn) != None:
        shift = 1 + ws.var('HLTKin_shift_'+sgn).getVal()/sgn_norm
        print "\tadding CMS_Xbb_trigger_kin....lnN", shift
        if (shift-1)>=0.01:
            f.write('CMS_Xbb_trigger_kin     lnN    '+("%.2f" % shift)+'                       '+("%.2f" % shift)+'                      -\n')      
    if ws.var('jec_norm_shift_'+sgn) != None:
        shift = 1 + ws.var('jec_norm_shift_'+sgn).getVal()/sgn_norm
        print "\tadding CMS_scale_j....lnN", shift
        if (shift-1)>=0.01:
            f.write('CMS_scale_j                 lnN    '+("%.3f" % shift)+'                  '+("%.3f" % shift)+'                      -\n')      
    f.write('\n')

    for p in xrange(FTestCfg[pdf_bkg]['ndof'][x_range]):        
        param = ("a%d_%s_deg%d_0" % (p,pdf_bkg,FTestCfg[pdf_bkg]['MaxOrder'][x_range]))
        val =  ws.var(param).getVal()
        print "\tsetting parameter... ", param, " as flatParam with initial value ", val
        f.write(param+'  flatParam \n')
    
    f.write('bias_sgn_'+sgn+'   param  0.0 '+bias+'\n')
    f.write('\n')

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

use_fixed_ranges = False
use_sliding_edges = True

signal_to_range = {
    'Spin0_M550' : '400to800',
    'Spin0_M600' : '400to800',
    'Spin0_M650' : '400to800',
    'Spin0_M700' : '500to900',
    'Spin0_M750' : '500to900',
    'Spin0_M800' : '500to900',
    'Spin0_M850' : '600to1000',
    'Spin0_M900' : '600to1000',
    'Spin0_M1000' : '700to1400',
    'Spin0_M1100' : '700to1400',
    'Spin0_M1200' : '700to1400',
    'Spin2_M550' : '400to800',
    'Spin2_M600' : '400to800',
    'Spin2_M650' : '400to800',
    'Spin2_M700' : '500to900',
    'Spin2_M750' : '500to900',
    'Spin2_M800' : '500to900',
    'Spin2_M850' : '600to1000',
    'Spin2_M900' : '600to1000',
    'Spin2_M1000' : '700to1400',
    'Spin2_M1100' : '700to1400',
    'Spin2_M1200' : '700to1400',
}

for cat_btag in [
    #'Had_LT', 
    #'Had_TT',
    'Had_MT', 
    ]:
    for cat_kin in [
        #'MinPt150_DH1p6', 'MinPt150_DH2p0', 'MinPt150_DH1p1', 
        #'MinPt175_DH1p6', 'MinPt175_DH2p0', 'MinPt175_DH1p1',
        #'MinPt200_DH1p6', 'MinPt200_DH2p0', 'MinPt200_DH1p1',
        'MinPt100_DH1p6'
        ]:        
        for pdf in [
            #'pow',
            #'exp',
            #'polyexp',
            #'pol'
            'dijet',
            'polydijet',
            ]:
            for sgn in [
                'Spin0_M550',
                'Spin0_M600',
                'Spin0_M650',
                'Spin0_M700',
                'Spin0_M750',
                'Spin0_M800',
                'Spin0_M850',
                'Spin0_M900',
                'Spin0_M1000',
                'Spin0_M1100',
                'Spin0_M1200',
                'Spin2_M550',
                'Spin2_M600',
                'Spin2_M650',
                'Spin2_M700',
                'Spin2_M750',
                'Spin2_M800',
                'Spin2_M850',
                'Spin2_M900',
                'Spin2_M1000',
                'Spin2_M1100',
                'Spin2_M1200',
                ]:
                for mass in ['MassFSR']:
                    range_name = ""
                    if use_fixed_ranges:
                        range_name = signal_to_range[sgn]
                    elif use_sliding_edges:
                        mX = float(sgn.split('_')[-1][1:])
                        edges = get_sliding_edges(mass=mX)
                        range_name = ("%.0fto%.0f" % (edges[0],edges[1]))
                    make_datacard('Xbb_workspace', cat_btag+"_"+cat_kin, mass, range_name, sgn, 'buk', pdf, 'data_obs', './plots/V7/', is_data=True)
                        
                    
                        
