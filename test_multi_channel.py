import m5

from m5.objects import Root, DDR4_2400_8x8
from gem5.components.boards.test_board import TestBoard
from gem5.components.memory.multi_channel import MultiChannelMemory
from gem5.components.cachehierarchies.ruby.mesi_two_level_cache_hierarchy import (
    MESITwoLevelCacheHierarchy,
)
from gem5.components.processors.linear_generator import LinearGenerator

generator = LinearGenerator(duration="100us", rate="1000GB/s")

cache_hierarchy = MESITwoLevelCacheHierarchy(
    l1i_size="32kB",
    l1i_assoc="8",
    l1d_size="32kB",
    l1d_assoc="8",
    l2_size="256kB",
    l2_assoc = "4",
    num_l2_banks=2,
)

memory = MultiChannelMemory(
    dram_interface_class=DDR4_2400_8x8,
    num_channels=2,
    addr_mapping="RoRaBaCoCh",
    interleaving_size=64,
    size="32GiB",
)

motherboard = TestBoard(
    clk_freq="4GHz",
    processor=generator,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

motherboard.connect_things()

root = Root(full_system=False, system=motherboard)

m5.instantiate()

generator.start_traffic()
print("Beginning simulation!")
exit_event = m5.simulate()
print(
    "Exiting @ tick {} because {}.".format(m5.curTick(), exit_event.getCause())
)
