#!/bin/sh 

echo "Copy pattern $1.$3 to directory $2"
#scp $2/$1*$3 bianchi@cms.hep.kbfi.ee:~/web/Xbb_$2
scp /scratch/bianchi/$2/$1*$3 bianchi@cms.hep.kbfi.ee:~/web/Xbb_$2