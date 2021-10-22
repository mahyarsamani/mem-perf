#!/bin/bash
generators=(Linear Random)
intensities=(Loaded Unloaded)
memories=(DDR3 DDR4 LPDDR5 HBM)
num_channels=(1 2)

for generator in "${generators[@]}"
    do for intensity in "${intensities[@]}"
        do for memory in "${memories[@]}"
            do for num_chnls in "${num_channels[@]}"
                do
                gem5/build/NULL_MESI_Two_Level/gem5.opt -re --outdir=results/memory_studies/$generator/$intensity/$memory/$num_chnls test_memory.py $generator $intensity $memory $num_chnls &
            done
        done
    done
done

caches=(NoCache PrivateL1 PrivateL1PrivateL2 MESITwoLevel)

for cache in "${caches[@]}"
    do
    gem5/build/NULL_MESI_Two_Level/gem5.opt -re --outdir=results/cache_studies/$cache test_cache.py $cache &
done
