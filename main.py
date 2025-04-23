from smkv import create, put, get
import os

dbfile = "/tmp/smkvsys_py"
if not os.path.exists(dbfile + ".shard0"):
    create(dbfile, num_buckets=16, keys_per_bucket=32, num_values=1000, value_size=32, n_shards=2)

put("foo", "bar")
print("GET foo =", get("foo"))
