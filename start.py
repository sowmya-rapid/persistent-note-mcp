import os
import uvicorn
import asyncio
from server import mcp, init_db

async def main():
    # 1. Initialize the database before starting the server
    print("Initializing database...")
    await init_db()
    
    # 2. Get the port (Render uses PORT env var, local defaults to 8000)
    port = int(os.environ.get("PORT", 8000))
    
    # 3. Use run_async to share the current event loop
    print(f"Starting server on port {port}...")
    await mcp.run_async(transport="sse", host="0.0.0.0", port=port)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped by user.")