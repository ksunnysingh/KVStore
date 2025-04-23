# keyvalue.py

import os
import sys

from smkv import create, put as _put, load
from smkv import get as _get, load

DBFILE = "/tmp/smkvsys_py"

def keyValPut(key: str, value: str):
    """ 
    Initialize or load the Key Value Store, then write a single key,value pair. In other words add a "value" associated with a given "key" 
    """

    if not os.path.exists(DBFILE + ".shard0"):
        create(DBFILE, num_buckets=16, keys_per_bucket=32,
               num_values=1000, value_size=32, n_shards=2)
    else:
        load(DBFILE, n_shards=2)
    _put(key, value)

def keyValGet(key: str):
    """
    Load the Key Value Store and return the "value" or None if missing fora given "key" 
    """

    if not os.path.exists(DBFILE + ".shard0"):
        raise RuntimeError("Database not initialized. Please run keyput.py first.")
    load(DBFILE, n_shards=2)
    return _get(key)
