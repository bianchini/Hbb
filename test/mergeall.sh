#!/bin/sh

declare -a arr=(
    #Spin0_M650
    #Spin0_M950
    #Spin0_M800
    #Spin0_M1400
    Run2015D
    #HT100to200
    #HT200to300
    #HT300to500
    #HT500to700
    #HT700to1000
    #HT1000to1500
    #HT1500to2000
    #HT2000toInf
    #M750
    TT_ext3
)

for i in ${arr[@]}
do
  ./merge.sh tree ${i}
done