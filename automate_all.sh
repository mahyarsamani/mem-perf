#!/usr/bin/bash

# General Instructions to use this Bash Script
# ./automate_all.sh <output_directory>
#
# No special notes

if [[ $# -ne 1 ]]; then
    printf "Error! No output directory provided. The program will exit now.\n"
    exit
fi

EXPERIMENTS=("DDR3" "DDR4" "LPDDR3" "HBM")
CHANNELS=("1" "2" "4" "8" "16")


mkdir $1
echo "Starting simulation!"

for dram in ${EXPERIMENTS[*]}; do
    for chan in ${CHANNELS[*]}; do
        printf "\nExperiment running for $dram with $chan channels.\n"
        ./automate_memory_factory.sh "LinearGenerator" "NoCache" "$dram" "$chan" \
        $1 "test_memory.py"
    done
done

echo "All experiments done!"
exit
