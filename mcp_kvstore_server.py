from typing import Any, Dict
import os
import logging
from mcp.server import FastMCP
# Stdio is typically the default transport and may not need explicit import/setting
# from mcp.transport import Stdio 
from smkv import create, put as _put, get as _get, load

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database file location
DBFILE = "/tmp/smkvsys_py"

# Initialize MCP server (Stdio is likely the default)
mcp = FastMCP("kvstore")

# Initialize database connection
def ensure_db_initialized():
    """Ensure the database is initialized before operations"""
    try:
        if not os.path.exists(DBFILE + ".shard0"):
            logger.info("Creating new database")
            create(DBFILE, num_buckets=16, keys_per_bucket=32,
                  num_values=1000, value_size=32, n_shards=2)
        else:
            logger.info("Loading existing database")
            load(DBFILE, n_shards=2)
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise RuntimeError("Database initialization failed")

@mcp.tool()
def kvstore_put(key: str, value: str) -> Dict[str, Any]:
    """Store a value with the given key in the key-value store.

    Args:
        key (str): The key under which to store the value.
        value (str): The value to store.
    """
    try:
        ensure_db_initialized()
        _put(key, value)
        logger.info(f"Successfully stored value for key: {key}")
        return {
            "success": True,
            "message": f"Successfully stored value for key: {key}"
        }
    except Exception as e:
        logger.error(f"Error storing value: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def kvstore_get(key: str) -> Dict[str, Any]:
    """Retrieve a value for the given key from the key-value store.

    Args:
        key (str): The key whose value needs to be retrieved.
    """
    try:
        ensure_db_initialized()
        value = _get(key)
        logger.info(f"Retrieved value for key {key}: {value}")
        return {
            "success": True,
            "value": value,
            "found": value is not None
        }
    except Exception as e:
        logger.error(f"Error retrieving value: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Start the MCP server
    logger.info("Starting KVStore MCP server...")
    try:
        # Correct run call for FastMCP with Stdio transport
        mcp.run(transport='stdio')
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise 