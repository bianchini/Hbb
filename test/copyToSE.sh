#!/bin/sh

name=tree.root

# create link
#mkdir -p /scratch/$USER/gfalFS/T3_CH_PSI

# mount T3
#gfalFS -s /scratch/$USER/gfalFS/T3_CH_PSI srm://t3se01.psi.ch

version=V2

declare -a arr=(
    Run2015D
    HT100to200
    HT200to300
    HT300to500
    HT500to700
    #HT700to1000
    HT1000to1500
    HT1500to2000
    HT2000toInf
    #M750
    #Spin0_M650
    #Spin0_M950
    #Spin0_M800
    #Spin0_M1400
    TT_ext3
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