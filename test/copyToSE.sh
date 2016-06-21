#!/bin/sh

name=tree.root

# create link
#mkdir -p /scratch/$USER/gfalFS/T3_CH_PSI

# mount T3
#gfalFS -s /scratch/$USER/gfalFS/T3_CH_PSI srm://t3se01.psi.ch

#version=V4
version=JetHT

declare -a arr=(
    Run2015D_JetHT
    #Run2015D
    #Run2015C
    HT100to200
    HT200to300
    HT300to500
    HT500to700
    HT700to1000
    HT1000to1500
    HT1500to2000
    HT2000toInf
    #M750
    #Spin0_M550
    #Spin0_M600
    #Spin0_M650
    #Spin0_M700
    #Spin0_M750
    #Spin0_M800
    #Spin0_M850
    #Spin0_M900
    #Spin0_M1000
    #Spin0_M1100
    #Spin0_M1200
    #Spin2_M550
    #Spin2_M600
    #Spin2_M650
    #Spin2_M700
    #Spin2_M750
    #Spin2_M800
    #Spin2_M850
    #Spin2_M900
    #Spin2_M1000
    #Spin2_M1100
    #Spin2_M1200
    #TT_ext3
    #ST_t_top
    #ST_t_atop
    #ST_tW_top
    #ST_tW_atop
)

for i in ${arr[@]}
do
    echo "Copy file $i to ${version}"
    gfal-mkdir srm://t3se01.psi.ch/pnfs/psi.ch/cms/trivcat/store/user/bianchi/Hbb_Heppy/${version}
    gfal-mkdir srm://t3se01.psi.ch/pnfs/psi.ch/cms/trivcat/store/user/bianchi/Hbb_Heppy/${version}/$i
    gfal-copy file://`pwd`/$i/${name} srm://t3se01.psi.ch/pnfs/psi.ch/cms/trivcat/store/user/bianchi/Hbb_Heppy/${version}/$i/${name}
    #cp $i/${name} /scratch/bianchi/gfalFS/T3_CH_PSI/pnfs/psi.ch/cms/trivcat/store/user/bianchi/Hbb_Heppy/$i/${name}
done

# unmonut
#gfalFS_umount /scratch/$USER/gfalFS/T3_CH_PSI