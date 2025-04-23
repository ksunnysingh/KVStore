# Key-Value Store

A simple key-value store implementation with basic put and get operations.

## Functions

### keyValPut(key: str, value: str)

Initialize or load the Key Value Store, then write a single key,value pair. In other words add a "value" associated with a given "key".

### keyValGet(key: str)

Load the Key Value Store and return the "value" or None if missing for a given "key".

Note: The database must be initialized by using keyValPut before attempting to use keyValGet. 