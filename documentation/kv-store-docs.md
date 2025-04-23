Directory structure:
└── ksunnysingh-kvstore/
    ├── README.md
    ├── keyvalue.py
    ├── main.py
    ├── pyproject.toml
    ├── smkv.py
    ├── uv.lock
    └── .python-version


Files Content:

================================================
FILE: README.md
================================================
# Key-Value Store

A simple key-value store implementation with basic put and get operations.

## Functions

### keyValPut(key: str, value: str)

Initialize or load the Key Value Store, then write a single key,value pair. In other words add a "value" associated with a given "key".

### keyValGet(key: str)

Load the Key Value Store and return the "value" or None if missing for a given "key".

Note: The database must be initialized by using keyValPut before attempting to use keyValGet. 


================================================
FILE: keyvalue.py
================================================
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



================================================
FILE: main.py
================================================
from smkv import create, put, get
import os

dbfile = "/tmp/smkvsys_py"
if not os.path.exists(dbfile + ".shard0"):
    create(dbfile, num_buckets=16, keys_per_bucket=32, num_values=1000, value_size=32, n_shards=2)

put("foo", "bar")
print("GET foo =", get("foo"))



================================================
FILE: pyproject.toml
================================================
[project]
name = "kv-file-store"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []



================================================
FILE: smkv.py
================================================
import mmap
import os
import struct
import hashlib

KEY_MAX = 16
VALUE_MAX = 32
PAGE_SIZE = 4096
MAX_SHARDS = 16

SHARDS = [None] * MAX_SHARDS
shard_count = 0

class KeyEntry:
    STRUCT_FMT = f"{KEY_MAX}s Q I I"
    SIZE = struct.calcsize(STRUCT_FMT)

    def __init__(self, key=b"", hashcode=0, voff=0, vlen=0):
        self.key = key.ljust(KEY_MAX, b'\x00')
        self.hashcode = hashcode
        self.value_offset = voff
        self.value_length = vlen

    def pack(self):
        return struct.pack(self.STRUCT_FMT, self.key, self.hashcode, self.value_offset, self.value_length)

    @classmethod
    def unpack(cls, data):
        key, h, voff, vlen = struct.unpack(cls.STRUCT_FMT, data)
        return cls(key, h, voff, vlen)

    def key_str(self):
        return self.key.rstrip(b'\x00').decode()

class Shard:
    def __init__(self, keyfile, valfile, num_buckets, keys_per_bucket):
        self.key_fd = open(keyfile, "r+b")
        self.key_mmap = mmap.mmap(self.key_fd.fileno(), 0)
        self.val_fd = open(valfile, "r+b")
        self.val_mmap = mmap.mmap(self.val_fd.fileno(), 0)

        self.num_buckets = num_buckets
        self.keys_per_bucket = keys_per_bucket
        self.bucket_size = 8 + keys_per_bucket * KeyEntry.SIZE

    def get_bucket_offset(self, h):
        bucket_idx = (h >> 8) % self.num_buckets
        return 16 + bucket_idx * self.bucket_size

def hash_key(key: str) -> int:
    return int(hashlib.sha256(key.encode()).hexdigest()[:16], 16)

def create(basefile, num_buckets, keys_per_bucket, num_values, value_size, n_shards):
    global shard_count
    shard_count = n_shards

    for i in range(n_shards):
        keyfile = f"{basefile}.shard{i}"
        valfile = f"{keyfile}.val"

        hdr = struct.pack("iiii", num_buckets, keys_per_bucket, KEY_MAX, n_shards)
        total = len(hdr) + num_buckets * (8 + keys_per_bucket * KeyEntry.SIZE)
        padded = ((total + PAGE_SIZE - 1) // PAGE_SIZE) * PAGE_SIZE
        with open(keyfile, "wb") as f:
            f.write(hdr)
            f.write(b"\x00" * (padded - len(hdr)))

        total_val = num_values * value_size + 8
        padded_val = ((total_val + PAGE_SIZE - 1) // PAGE_SIZE) * PAGE_SIZE
        with open(valfile, "wb") as f:
            f.write(struct.pack("I", 0))  # free offset
            f.write(b"\x00" * (padded_val - 4))

        SHARDS[i] = Shard(keyfile, valfile, num_buckets, keys_per_bucket)

def put(key: str, value: str):
    global SHARDS, shard_count
    k_bytes = key.encode().ljust(KEY_MAX, b'\x00')
    v_bytes = value.encode()
    h = hash_key(key)
    shard_idx = h % shard_count
    shard = SHARDS[shard_idx]

    b_offset = shard.get_bucket_offset(h)
    shard.key_mmap.seek(b_offset)
    num_keys = struct.unpack("i", shard.key_mmap.read(4))[0]
    free_slot = struct.unpack("i", shard.key_mmap.read(4))[0]

    if num_keys >= shard.keys_per_bucket:
        raise Exception("Bucket full")

    keys = []
    for i in range(num_keys):
        data = shard.key_mmap.read(KeyEntry.SIZE)
        keys.append(KeyEntry.unpack(data))

    shard.val_mmap.seek(0)
    val_offset = struct.unpack("I", shard.val_mmap.read(4))[0]

    data_offset = 8 + val_offset
    shard.val_mmap.seek(data_offset)
    shard.val_mmap.write(v_bytes)

    shard.val_mmap.seek(0)
    shard.val_mmap.write(struct.pack("I", val_offset + len(v_bytes)))

    new_key = KeyEntry(k_bytes, h, val_offset, len(v_bytes))
    keys.append(new_key)
    keys.sort(key=lambda k: (k.hashcode, k.key_str()))

    shard.key_mmap.seek(b_offset)
    shard.key_mmap.write(struct.pack("i", num_keys + 1))
    shard.key_mmap.write(struct.pack("i", free_slot + 1))

    for k in keys:
        shard.key_mmap.write(k.pack())

def get(key: str):
    h = hash_key(key)
    shard_idx = h % shard_count
    shard = SHARDS[shard_idx]

    b_offset = shard.get_bucket_offset(h)
    shard.key_mmap.seek(b_offset)
    num_keys = struct.unpack("i", shard.key_mmap.read(4))[0]
    shard.key_mmap.read(4)

    keys = []
    for _ in range(num_keys):
        data = shard.key_mmap.read(KeyEntry.SIZE)
        keys.append(KeyEntry.unpack(data))

    lo, hi = 0, len(keys) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        k = keys[mid]
        cmp_hash = (h > k.hashcode) - (h < k.hashcode)
        cmp_key = (key > k.key_str()) - (key < k.key_str())

        if cmp_hash == 0 and cmp_key == 0:
            val_offset = 8 + k.value_offset
            shard.val_mmap.seek(val_offset)
            return shard.val_mmap.read(k.value_length).decode()
        elif cmp_hash < 0 or (cmp_hash == 0 and cmp_key < 0):
            hi = mid - 1
        else:
            lo = mid + 1
    return None

def load(basefile, n_shards):
    global shard_count, SHARDS
    shard_count = n_shards
    for i in range(n_shards):
        keyfile = f"{basefile}.shard{i}"
        valfile = f"{keyfile}.val"
        SHARDS[i] = Shard(keyfile, valfile, 16, 32)  # defaults for buckets and slots



================================================
FILE: uv.lock
================================================
version = 1
revision = 1
requires-python = ">=3.12"

[[package]]
name = "kv-file-store"
version = "0.1.0"
source = { virtual = "." }



================================================
FILE: .python-version
================================================
3.12


