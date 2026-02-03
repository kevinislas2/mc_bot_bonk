import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import discord
from dotenv import load_dotenv

load_dotenv()

# Configuration
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

# Discord Client Setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# State Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # Broadcast a message to all connected Minecraft computers
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

# Lifecycle: Manages the Discord Bot loop alongside the Web Server
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Run Discord bot in the background
    asyncio.create_task(client.start(TOKEN))
    yield
    # Shutdown
    await client.close()

app = FastAPI(lifespan=lifespan)

# --- Discord Events ---
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.id != CHANNEL_ID:
        return

    # Format: [DiscordUser] Message Content
    payload = f"[{message.author.display_name}] {message.content}"
    print(f"Forwarding to Minecraft: {payload}")
    await manager.broadcast(payload)

# --- WebSocket Endpoint ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive data FROM Minecraft
            data = await websocket.receive_text()
            
            # Send to Discord
            channel = client.get_channel(CHANNEL_ID)
            if channel:
                # You might want to sanitize 'data' here to prevent ping spam
                await channel.send(f"**[Minecraft]** {data}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)