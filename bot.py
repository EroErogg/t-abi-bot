import os
import asyncio
import discord
from discord.ext import commands
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- 1. Mini-Webserver für Render ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def start_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

threading.Thread(target=start_server, daemon=True).start()


# --- 2. Discord Bot Konfiguration ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

# --- 3. Ticket-System mit fester ID ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Support", description="Allgemeine Hilfe und Fragen", emoji="🛟"),
            discord.SelectOption(label="Live-Frage", description="Fragen zu Streams oder Live-Inhalten", emoji="🔴"),
            discord.SelectOption(label="Strada-Frage", description="Fragen rund um Strada", emoji="🔥"),
        ]
        super().__init__(
            placeholder="Wähle dein Anliegen für das Ticket...", 
            min_values=1, 
            max_values=1, 
            options=options, 
            custom_id="abi_ticket_dropdown_v1"
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            # Prüfen ob bereits geantwortet wurde, um Fehler zu vermeiden
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"Dein Ticket für **{self.values[0]}** wurde erfolgreich erstellt!", 
                    ephemeral=True
                )
        except Exception as e:
            print(f"Fehler im Ticket-Callback: {e}")

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


# --- 4. Events ---
@bot.event
async def on_member_join(member: discord.Member):
    role_id = 1543819197706936481
    role = member.guild.get_role(role_id)
    if role:
        try:
            await member.add_roles(role)
        except Exception as e:
            print(f"Fehler bei Autorole: {e}")

is_synced = False

@bot.event
async def on_ready():
    global is_synced
    print(f"🚀 Bot ist online als {bot.user}")
    
    # Registriert das Menü dauerhaft
    bot.add_view(TicketView())
    
    if not is_synced:
        try:
            synced = await bot.tree.sync()
            print(f"🔄 {len(synced)} Slash-Commands synchronisiert.")
            is_synced = True
        except Exception as e:
            print(f"Fehler beim Syncen: {e}")


# --- 5. Slash-Befehle ---
@bot.tree.command(name="ping", description="Testet, ob der Bot erreichbar ist.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! 🏓 Alles läuft einwandfrei.", ephemeral=True)

@bot.tree.command(name="setup_ticket", description="Sendet das Ticket-Menü in den Kanal.")
async def setup_ticket(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 Support & Tickets",
        description="Wähle unten im Menü dein Anliegen aus, um einen privaten Support-Kanal zu öffnen.",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, view=TicketView())


# --- 6. Bot Starten ---
async def main():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("❌ FEHLER: Kein DISCORD_TOKEN gefunden!")
        return
    
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
