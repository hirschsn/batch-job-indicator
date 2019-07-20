# See LICENSE for license details.

from hazelhen import MachineHazelhen

_MACH_REGISTRY = {
    "hazelhen": MachineHazelhen
}

def parser_maker(name):
    """Returns the constructor to a parser class for machine "name"."""
    try:
        return _MACH_REGISTRY[name]
    except:
        raise RuntimeError("Unknown machine: {}".format(name))
