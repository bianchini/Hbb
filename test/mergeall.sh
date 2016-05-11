#!/bin/sh

declare -a arr=(
    #Spin0_M650
    #Spin0_M750
    #Spin0_M850
    #Spin0_M1000
    #Spin0_M1200
    #Spin2_M650
    #Spin2_M750
    #Spin2_M850
    #Spin2_M1000
    #Spin2_M1200
    #Run2015D
    Run2015C
    #HT100to200
    #HT200to300
    #HT300to500
    #HT500to700
    #HT700to1000
    #HT1000to1500
    #HT1500to2000
    #HT2000toInf
    #M750
    #TT_ext3
)

for i in ${arr[@]}
do
  ./merge.sh tree ${i}
done