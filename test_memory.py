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
import argparse

from os.path import join
from m5.stats import gem5stats
from gem5.components.boards.test_board import TestBoard
from gem5.components.memory.multi_channel import MultiChannelMemory
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.processors.linear_generator import LinearGenerator
from gem5.components.processors.random_generator import RandomGenerator
from m5.objects import (
    Root,
    DDR3_1600_8x8,
    DDR4_2400_8x8,
    HBM_1000_4H_1x128,
    LPDDR5_5500_1x16_8B_BL32,
)


def translate_intensity(intensity, num_channels):
    if intensity == "Loaded":
        return str(24 * num_channels) + "GB/s"
    elif intensity == "Unloaded":
        return "1GB/s"
    else:
        raise ValueError


def generator_factory(generator_class, rate, mem_size):
    if generator_class == "Linear":
        return LinearGenerator(
            duration="250us", rate=rate, min_addr=0, max_addr=mem_size
        )
    elif generator_class == "Random":
        return RandomGenerator(
            duration="250us", rate=rate, min_addr=0, max_addr=mem_size
        )
    else:
        raise ValueError


def memory_factory(memory_class, num_channels):
    if memory_class == "DDR3":
        return MultiChannelMemory(
            dram_interface_class=DDR3_1600_8x8,
            num_channels=num_channels,
            addr_mapping="RoCoRaBaCh",
        )
    elif memory_class == "DDR4":
        return MultiChannelMemory(
            dram_interface_class=DDR4_2400_8x8,
            num_channels=num_channels,
            addr_mapping="RoCoRaBaCh",
        )
    elif memory_class == "LPDDR5":
        return MultiChannelMemory(
            dram_interface_class=LPDDR5_5500_1x16_8B_BL32,
            num_channels=num_channels,
            addr_mapping="RoCoRaBaCh",
        )
    elif memory_class == "HBM":
        return MultiChannelMemory(
            dram_interface_class=HBM_1000_4H_1x128,
            num_channels=num_channels,
            addr_mapping="RoCoRaBaCh",
        )
    else:
        raise ValueError


parser = argparse.ArgumentParser(
    description="A traffic generator that can be sed to test a gem5 "
    "memory component."
)

parser.add_argument(
    "generator_class",
    type=str,
    help="Type of traffic to be generated",
    choices=["Linear", "Random"],
)

parser.add_argument(
    "traffic_intensity",
    type=str,
    help="The intensity of injected traffic",
    choices=["Loaded", "Unloaded"],
)

parser.add_argument(
    "memory_class",
    type=str,
    help="The type of memory to be used in the system",
    choices=["DDR3", "DDR4", "LPDDR5", "HBM"],
)

parser.add_argument(
    "num_channels",
    type=int,
    help="The number of channels that we want to simulate",
)

args = parser.parse_args()

memory = memory_factory(args.memory_class, args.num_channels)

generator = generator_factory(
    args.generator_class,
    translate_intensity(args.traffic_intensity, args.num_channels),
    memory.get_size(),
)

cache_hierarchy = NoCache()


motherboard = TestBoard(
    clk_freq="4GHz",
    processor=generator,
    cache_hierarchy=cache_hierarchy,
    memory=memory,
)

motherboard.connect_things()

root = Root(full_system=False, system=motherboard)

m5.instantiate()

generator.start_traffic()
print("Beginning simulatrion")
exit_event = m5.simulate()
print(
    "exiting @ tick {} because {}.".format(m5.curTick(), exit_event.getCause())
)
stats = gem5stats.get_simstat(root)
json_out = join(m5.options.outdir, "processor_stats.json")
with open(json_out, "w") as json_stats:
    stats.system.processor.dump(json_stats, indent=2)

print("Simulation finished")
