# Copyright (c) 2021 The Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
This script creates a simple traffic generator. The simulator starts with a
linear traffic generator, and ends with a random traffic generator. It is used
for testing purposes.
"""
import m5
import re
import argparse
import pandas as pd
import seaborn as sns

from os import listdir
from os.path import join
from m5.stats import gem5stats
from gem5.components.boards.test_board import TestBoard
from gem5.components.processors.gups_generator import GUPSGenerator
from gem5.components.memory.multi_channel import MultiChannelMemory
from gem5.components.cachehierarchies.classic.no_cache import NoCache
#from gem5.components.processors.linear_generator import LinearGenerator
from gem5.components.processors.gups_generator_ep import GUPSGeneratorEP
from gem5.components.processors.complex_generator import ComplexGenerator
from gem5.components.processors.gups_generator_par import GUPSGeneratorPAR
from m5.objects import Root, DDR3_1600_8x8, DDR4_2400_8x8, LPDDR3_1600_1x32,\
    HBM_1000_4H_1x128

translate_limit = {"32KiB": 0x8000, "256KiB": 0x40000, "1MiB": 0x100000}
limit_num = ["32KiB", "256KiB", "1MiB"]


# TODO: Update this to return generators with sound parameters
def generator_factory(traffic_mode):
    if traffic_mode == "Linear":
        generator = ComplexGenerator()
        generator.add_linear(rate="20GB/s",
            data_limit=translate_limit["32KiB"])
        generator.add_linear(rate="20GB/s",
            data_limit=translate_limit["256KiB"])
        generator.add_linear(rate="20GB/s",
            data_limit=translate_limit["1MiB"])
    elif traffic_mode == "Random":
        generator = ComplexGenerator()
        generator.add_random(rate="20GB/s",
            data_limit=translate_limit["32KiB"])
        generator.add_random(rate="20GB/s",
            data_limit=translate_limit["256KiB"])
        generator.add_random(rate="20GB/s",
            data_limit=translate_limit["1MiB"])
    elif traffic_mode == "GUPS":
        generator = GUPSGenerator(update_limit = 1000)
    elif traffic_mode == "GUPSEP":
        generator = GUPSGeneratorEP(num_cores = 2, update_limit = 1000)
    elif traffic_mode == "GUPSPAR":
        generator = GUPSGeneratorPAR(num_cores = 2, update_limit = 1000)
    else:
        raise ValueError
    return generator

def cache_factory (cache_class):
    if cache_class == "NoCache":
        return NoCache ()
    elif cache_class == "PrivateL1":
        from gem5.components.cachehierarchies.classic\
            .private_l1_cache_hierarchy import (
            PrivateL1CacheHierarchy,
        )

        return PrivateL1CacheHierarchy (l1i_size = "32KiB", l1d_size="32KiB")
    elif cache_class == "PrivateL1PrivateL2":
        from gem5.components.cachehierarchies.classic\
            .private_l1_private_l2_cache_hierarchy import (
            PrivateL1PrivateL2CacheHierarchy,
        )

        return PrivateL1PrivateL2CacheHierarchy (
            l1i_size = "32KiB", l1d_size = "32KiB", l2_size = "256KiB"
        )
    elif cache_class == "MESITwoLevel":
        from gem5.components.cachehierarchies.ruby\
            .mesi_two_level_cache_hierarchy import (
            MESITwoLevelCacheHierarchy,
        )

        return MESITwoLevelCacheHierarchy (
            l1i_size  = "32KiB",
            l1i_assoc = "8",
            l1d_size  = "32KiB",
            l1d_assoc = "8",
            l2_size   = "256KiB",
            l2_assoc  = "4",
            num_l2_banks = 1,
        )
    else:
        raise ValueError

def memory_factory (memory_class, num_chan):
    # TODO
    if memory_class == "DDR3":
        return MultiChannelMemory (
            dram_interface_class = DDR3_1600_8x8,
            num_channels = num_chan
        )
    elif memory_class == "DDR4":
        return MultiChannelMemory (
            dram_interface_class = DDR4_2400_8x8,
            num_channels = num_chan
        )
    elif memory_class == "LPDDR3":
        return MultiChannelMemory (
            dram_interface_class = LPDDR3_1600_1x32,
            num_channels = num_chan
        )
    elif memory_class == "HBM":
        return MultiChannelMemory (
            dram_interface_class = HBM_1000_4H_1x128,
            num_channels = num_chan
        )
    else:
        raise ValueError

parser = argparse.ArgumentParser(
    description = "A traffic generator that can be sed to test a gem5 "
    "memory component."
)

parser.add_argument (
    "generator_class",
    type = str,
    help = "Type of traffic to be generated",
    choices = ["Linear", "Random", "GUPS", "GUPSEP", "GUPSPAR"],
)

parser.add_argument (
    "cache_class",
    type = str,
    help = "The type of cache to be used in the system",
    choices = ["NoCache", "PrivateL1", "PrivateL1PrivateL2", "MESITwoLevel"],
)

parser.add_argument (
    "memory_class",
    type = str,
    help = "The type of memory to be used in the system",
    choices = ["DDR3", "DDR4", "LPDDR3", "HBM"],
)

parser.add_argument (
    "num_chan",
    type = int,
    help = "The number of channels that we want to simulate",
    #choices = ["1 to N"],
)

args = parser.parse_args ()

generator = generator_factory (args.generator_class)

cache_hierarchy = cache_factory (args.cache_class)

memory = memory_factory (args.memory_class, args.num_chan)

motherboard = TestBoard (
    clk_freq = "4GHz",
    processor = generator,
    cache_hierarchy = cache_hierarchy,
    memory = memory,
)

motherboard.connect_things ()

root = Root (full_system = False, system = motherboard)

json_files = []

m5.instantiate ()

generator.start_traffic ()
print ("Beginning simulatrion with 32 KiB data limit.")
exit_event = m5.simulate ()
print ("exiting @ tick {} because {}.".format(m5.curTick (),
    exit_event.getCause ())
)
stats = gem5stats.get_simstat (root)
json_out = join (m5.options.outdir, "stats_32KiB.json")
with open (json_out, "w") as json_stats:
    stats.system.processor.dump (json_stats, indent = 2)
    json_files.append (stats.system.processor)
m5.stats.reset ()
generator.start_traffic ()
print("Resuming simulation! With 256KiB data limit")
exit_event = m5.simulate()
print(
    "Exiting @ tick {} because {}.".format(m5.curTick(), exit_event.getCause())
)
stats = gem5stats.get_simstat(root)
json_out = join(m5.options.outdir, "stats_256KiB.json")
with open(json_out, "w") as json_stats:
    stats.system.processor.dump(json_stats, indent=2)
    json_files.append(stats.system.processor)
m5.stats.reset()
generator.start_traffic()
print("Resuming simulation! With 1MiB data limit")
exit_event = m5.simulate()
print(
    "Exiting @ tick {} because {}.".format(m5.curTick(), exit_event.getCause())
)
stats = gem5stats.get_simstat(root)
json_out = join(m5.options.outdir, "stats_1MiB.json")
with open(json_out, "w") as json_stats:
    stats.system.processor.dump(json_stats, indent=2)
    json_files.append(stats.system.processor)
