#!/bin/bash
export E=/Users/collinsr/work/ppaml/2015-06-mcauley-code/flickr_bmrm/bmrm-2.1/groups-bmrm/../linear-bmrm/linear-bmrm-train
export SRCDIR=./run_bmrm_fixed

for i in $SRCDIR/*.conf; do
    tag=`basename $i .conf`
    label=`echo ${tag} | awk -F - '{print $2}'`
    echo $i
    ${E} $i &> $SRCDIR/train_${tag}.log
    /bin/mv $SRCDIR/labels_${tag}.txt $SRCDIR/labels_${tag}.train.txt
done
