#!/bin/bash

ABSOLUTE_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)

if [ "$#" -ne 3 ]; then
    echo "usage: $(basename $0) <run_out> <eval_in> <eval_output_dir>"
    exit 1
fi

export PYTHONPATH=$ABSOLUTE_PATH

run_out=$1
eval_in=$2
eval_output_dir=$3

[ -d $eval_output_dir ] || mkdir $eval_output_dir

python $ABSOLUTE_PATH/tools/cp6_eval.py --lt $eval_in/etc/label_table.txt --tt $eval_in/testing/image_table.txt --ct $run_out/label_vectors_results.txt --tht $run_out/threshold_table.txt &> $eval_output_dir/eval.log
