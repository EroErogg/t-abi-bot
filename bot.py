import os
import asyncio
import discord
from discord.ext import commands
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- 1. Mini-Webserver für Render (Löst den Port-Fehler) ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def start_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

# Startet den Webserver im Hintergrund, damit Render zufrieden ist
threading.Thread(target=start_server, daemon=True).start()


# --- 2. Discord Bot Konfiguration ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 Bot ist online als {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔄 {len(synced)} Slash-Commands synchronisiert.")
    except Exception as e:
        print(e)

# Beispiel-Befehl zum Testen (/ping)
@bot.tree.command(name="ping", description="Testet, ob der Bot erreichbar ist.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! 🏓 Alles läuft einwandfrei.", ephemeral=True)


# --- 3. Bot Starten ---
async def main():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("❌ FEHLER: Kein DISCORD_TOKEN in den Environment Variables gefunden!")
        return
    
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
