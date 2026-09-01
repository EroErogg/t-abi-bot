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

# --- 3. Ticket-System (Erstellt jetzt echte Kanäle!) ---
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
        # Zeigt dem User sofort an, dass im Hintergrund gearbeitet wird (verhindert Timeout)
        await interaction.response.defer(ephemeral=True)
        
        guild = interaction.guild
        member = interaction.user
        category_name = self.values[0]

        # Berechtigungen: Nur der User, der Admin/Bot und Rollen mit Admin-Rechten sehen das Ticket
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
        }

        # Kanalname generieren (z.B. ticket-tesak-support)
        safe_name = f"ticket-{member.name}-{category_name}".lower().replace(" ", "-").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")

        try:
            # Erstelle den echten Textkanal auf dem Server
            ticket_channel = await guild.create_text_channel(name=safe_name, overwrites=overwrites)

            # Begrüßungsnachricht in den neuen Ticket-Kanal schicken
            embed = discord.Embed(
                title=f"🎫 Ticket: {category_name}",
                description=f"Hallo {member.mention}!\nDanke für dein Anliegen. Ein Teammitglied wird sich gleich hier melden.",
                color=discord.Color.blue()
            )
            await ticket_channel.send(embed=embed)

            # Dem User als Antwort (nur für ihn sichtbar) den Link zum neuen Kanal geben
            await interaction.followup.send(f"Dein Ticket wurde erfolgreich erstellt: {ticket_channel.mention}", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"Fehler beim Erstellen des Kanals: {e}", ephemeral=True)

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
