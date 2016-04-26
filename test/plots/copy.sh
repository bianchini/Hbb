#!/bin/sh 

echo "Copy to pattern $1 $2"
scp $2/$1*png bianchi@cms.hep.kbfi.ee:~/web/Xbb_$2