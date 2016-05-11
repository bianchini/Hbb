#!/bin/sh 

echo "Copy pattern $1 to $2"
#scp plots/$2/$1*png bianchi@cms.hep.kbfi.ee:~/web/Xbb_$2
scp /scratch/bianchi/$2/$1*png bianchi@cms.hep.kbfi.ee:~/web/Xbb_$2