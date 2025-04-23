# Key-Value Store

A simple key-value store implementation with basic put and get operations, exposed through an MCP server interface.

## Key-Value Store Functions

### keyValPut(key: str, value: str)

Initialize or load the Key Value Store, then write a single key,value pair. In other words add a "value" associated with a given "key".

### keyValGet(key: str)

Load the Key Value Store and return the "value" or None if missing for a given "key".

Note: The database must be initialized by using keyValPut before attempting to use keyValGet.

## MCP Server Tools

The key-value store is accessible through an MCP server that provides the following tools:

### kvstore_put

Store a value with the given key in the key-value store.

Parameters:
- key (str): The key to store the value under
- value (str): The value to store

Returns:
- success (bool): Whether the operation was successful
- message (str): Success message (on success)
- error (str): Error message (on failure)

### kvstore_get

Retrieve a value for the given key from the key-value store.

Parameters:
- key (str): The key to look up

Returns:
- success (bool): Whether the operation was successful
- value (str): The stored value (if found)
- found (bool): Whether the key exists
- error (str): Error message (on failure)

## Running the Server

To start the MCP server:

```bash
python mcp_kvstore_server.py
``` 