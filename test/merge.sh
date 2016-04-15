#!/bin/sh

if [ -z $ROOTSYS ]; then
    echo "ROOTSYS is not defined: source ROOT, or hadd won't work!"
    exit
fi

if ls ./$1_* &> /dev/null ; then
    ls ./$1_* 
    hadd -f $1.root $1_*.root
    if ls $1.root  &> /dev/null ; then
	rm $1_*.root
    fi
else
    echo "Pattern $1 not found"
fi
