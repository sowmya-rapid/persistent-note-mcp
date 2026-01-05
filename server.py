# import os
# import asyncio
# import aiosqlite
# from fastmcp import FastMCP
# from starlette.responses import JSONResponse

# # Initialize FastMCP
# mcp = FastMCP("Note Taker Pro")
# DB_PATH = "notes.db"

# # --- 1. Database Initialization ---
# async def init_db():
#     async with aiosqlite.connect(DB_PATH) as db:
#         await db.execute("""
#             CREATE TABLE IF NOT EXISTS notes (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 title TEXT UNIQUE,
#                 content TEXT
#             )
#         """)
#         await db.commit()
#     print("Database initialized successfully.")

# # --- 2. Health Check (Fixes Render Shutdowns) ---
# @mcp.external_app.get("/")
# async def health_check():
#     """Tell Render and Postman that the server is healthy."""
#     return JSONResponse({
#         "status": "healthy",
#         "mcp_endpoints": ["/sse", "/messages"],
#         "message": "Note Taker Pro MCP is running!"
#     })

# # --- 3. MCP Tools ---
# @mcp.tool()
# async def create_note(title: str, content: str) -> str:
#     """Create a new persistent note."""
#     try:
#         async with aiosqlite.connect(DB_PATH) as db:
#             await db.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
#             await db.commit()
#         return f"Note '{title}' saved successfully."
#     except Exception as e:
#         return f"Error: {str(e)}"

# @mcp.tool()
# async def get_note(title: str) -> str:
#     """Retrieve a note by its title."""
#     async with aiosqlite.connect(DB_PATH) as db:
#         async with db.execute("SELECT content FROM notes WHERE title = ?", (title,)) as cursor:
#             row = await cursor.fetchone()
#             return row[0] if row else "Note not found."

# @mcp.tool()
# async def list_notes() -> list[str]:
#     """List all saved note titles."""
#     async with aiosqlite.connect(DB_PATH) as db:
#         async with db.execute("SELECT title FROM notes") as cursor:
#             rows = await cursor.fetchall()
#             return [row[0] for row in rows]

# # --- 4. Main Entry Point (Optimized for Render) ---
# async def main():
#     # Initialize database
#     await init_db()
    
#     # Get port from environment for Render
#     port = int(os.environ.get("PORT", 10000))
    
#     # Run the server using the async method to keep the loop alive
#     print(f"Starting MCP server on port {port}...")
#     await mcp.run_async(transport="sse", host="0.0.0.0", port=port)

# if __name__ == "__main__":
#     asyncio.run(main())









import os
import asyncio
import aiosqlite
from fastmcp import FastMCP
from starlette.responses import JSONResponse

# Initialize FastMCP
mcp = FastMCP("Note Taker Pro")
DB_PATH = "notes.db"

# --- 1. Database Initialization ---
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE,
                content TEXT
            )
        """)
        await db.commit()
    print("Database initialized successfully.")

# --- 2. Health Check (Corrected Decorator) ---
# This replaces @mcp.external_app.get("/")
@mcp.custom_route("/", methods=["GET"])
async def health_check(request):
    """Tell Render and Postman that the server is healthy."""
    return JSONResponse({
        "status": "healthy",
        "mcp_endpoints": ["/sse", "/messages"],
        "message": "Note Taker Pro MCP is running!"
    })

# --- 3. MCP Tools ---
@mcp.tool()
async def create_note(title: str, content: str) -> str:
    """Create a new persistent note."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
            await db.commit()
        return f"Note '{title}' saved successfully."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def get_note(title: str) -> str:
    """Retrieve a note by its title."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT content FROM notes WHERE title = ?", (title,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else "Note not found."

@mcp.tool()
async def list_notes() -> list[str]:
    """List all saved note titles."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT title FROM notes") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

# --- 4. Main Entry Point ---
async def main():
    await init_db()
    
    # Render provides the PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    
    print(f"Starting MCP server on port {port}...")
    # Use mcp.run() with sse transport - it's compatible with Render
    mcp.run(transport="sse", host="0.0.0.0", port=port)

if __name__ == "__main__":
    asyncio.run(main())