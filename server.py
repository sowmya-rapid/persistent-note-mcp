# import os
# import aiosqlite
# from fastmcp import FastMCP

# # Initialize FastMCP
# mcp = FastMCP("Note Taker Pro")
# DB_PATH = "notes.db"

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

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(init_db())
#     mcp.run()






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

# --- 2. Health Check (Fixes Render Shutdowns) ---
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
if __name__ == "__main__":
    # Create DB then start server
    asyncio.run(init_db())
    # Use 'sse' transport for Render/Postman compatibility
    mcp.run(transport="sse")