#!/usr/bin/bash

# General Instructions to use this Bash Script
# ./automate_memory_factory <traffic_type> <cache_type> <memory_gen/type> 
#   <num_chan> <result_dir> <input_file>
# order of the aforementioned arguments is important.
#
# Also, note that this file is OUTSIDE the gem5 directory TODO: Fix this

if [[ $# -ge 6 ]]; then
    TRAFFIC=$1
    CACHE=$2
    MEM=$3
    CHAN=$4
    RES=$5
else
    printf "Error! This script requires the following inputs:\n"
    printf "\t$ ./automate_memory_factory <traffic_type> <cache_type> "
    printf "<memory_gen/type> <num_chan> <resu_dir> <input>\n"
    printf "\t\ttraffic_type: LinearGenerator, GUPSGenerator, GUPSEPGenerator\
, GUPSPARGenerator\n"
    printf "\t\tcache_type: NoCache, PrivateL1, PrivateL1PrivateL2, \
MESITwoLevel\n"
    printf "\t\tmemory_gen/type: DDR3, DDR4, LPDDR3, HBM\n"
    printf "\t\tnum_chan: n (int), where n in {1..N}\n"
    printf "\t\tres_dir: results directory\n"
    printf "\t\tinput: location of the input file\n\n"
    exit
fi

# Get the date and time (in unix epoch time) so that there are no conflicts.
#DAT=`date +%s`


if [ ! -d "$RES" ]; then
    mkdir "$RES"
fi

if [ ! -d "$RES/$CACHE" ]; then
    mkdir "$RES/$CACHE"
fi

if [ ! -d "$RES/$CACHE/$TRAFFIC" ]; then
    mkdir "$RES/$CACHE/$TRAFFIC"
fi

if [ ! -d "$RES/$CACHE/$TRAFFIC/$MEM" ]; then
    mkdir "$RES/$CACHE/$TRAFFIC/$MEM"
fi

if [ ! -d "$RES/$CACHE/$TRAFFIC/$MEM/$CHAN" ]; then
    mkdir "$RES/$CACHE/$TRAFFIC/$MEM/$CHAN"
fi
 
# Using next number in the folder to avoid conflicts
WC=`ls $RES/$CACHE/$TRAFFIC/$MEM/$CHAN|wc -l`
DAT=$(($WC + 1))   

if [ -d "$RES/$CACHE/$TRAFFIC/$MEM/$CHAN/$DAT" ]; then
    echo "Directory `echo "$RES/$CACHE/$TRAFFIC/$MEM/$CHAN/$DAT"` \
already exists. Aborting!"
    exit
else
    mkdir "$RES/$CACHE/$TRAFFIC/$MEM/$CHAN/$DAT"
fi

# Start gem5!
echo "Staring gem5!"
gem5/build/NULL/gem5.opt -re --outdir=$RES/$CACHE/$TRAFFIC/$MEM/$CHAN/$DAT $6 \
$TRAFFIC $CACHE $MEM $CHAN
exit
