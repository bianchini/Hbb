#!/bin/sh

# $1 = file name pattern
# $2 = directory

if [ -z $ROOTSYS ]; then
    echo "ROOTSYS is not defined: source ROOT, or hadd won't work!"
    exit
fi

if ls $2/$1_* &> /dev/null ; then
    ls $2/$1_* 
    hadd -f $2/$1.root $2/$1_*.root
    if ls $2/$1.root  &> /dev/null ; then
	rm $2/$1_*.root
    fi
else
    echo "Pattern $1 not found in directory $2"
fi
