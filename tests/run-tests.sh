#!/bin/bash
# quick and dirty test script
cd $(realpath $(dirname $0))
python3 ../singularity_defparser.py data/test1.def
python3 ../singularity_defparser.py data/test2.def
