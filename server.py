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

# # --- 2. Health Check (Corrected Decorator) ---
# # This replaces @mcp.external_app.get("/")
# @mcp.custom_route("/", methods=["GET"])
# async def health_check(request):
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

# # --- 4. Main Entry Point ---
# async def main():
#     await init_db()
    
#     # Render provides the PORT environment variable
#     port = int(os.environ.get("PORT", 10000))
    
#     print(f"Starting MCP server on port {port}...")
#     # Use mcp.run() with sse transport - it's compatible with Render
#     mcp.run(transport="sse", host="0.0.0.0", port=port)

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

# --- 2. Health Check ---
@mcp.custom_route("/", methods=["GET"])
async def health_check(request):
    """Wake-up endpoint for Render."""
    return JSONResponse({
        "status": "healthy",
        "mcp_endpoints": ["/sse", "/sse/mcp"],
        "message": "Note Taker Pro MCP is active!"
    })

# --- 3. MCP Tools (Standardized JSON Outputs) ---

@mcp.tool()
async def create_note(title: str, content: str) -> dict:
    """Create a new persistent note."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
            await db.commit()
        return {"status": f"Note '{title}' saved successfully."}
    except Exception as e:
        return {"status": f"Error: {str(e)}"}

@mcp.tool()
async def get_note(title: str) -> dict:
    """Retrieve a note by its title."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT content FROM notes WHERE title = ?", (title,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"content": row[0]}
            return {"content": "Note not found."}

@mcp.tool()
async def list_notes(filter_text: str = "") -> dict:
    """
    List all saved note titles. 
    Input 'filter_text' (optional) to search for specific notes.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        if filter_text:
            query = "SELECT title FROM notes WHERE title LIKE ?"
            params = (f"%{filter_text}%",)
        else:
            query = "SELECT title FROM notes"
            params = ()
            
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return {"notes": [row[0] for row in rows]}

# --- 4. Main Entry Point (Workflow Alignment) ---
async def main():
    await init_db()
    
    # Port provided by Render
    port = int(os.environ.get("PORT", 10000))
    
    print(f"Starting MCP server on port {port}...")
    
    # message_path="/sse/mcp" matches the path your workflow is hitting (fixing the 404)
    mcp.run(transport="sse", host="0.0.0.0", port=port, message_path="/sse/mcp")

if __name__ == "__main__":
    asyncio.run(main())