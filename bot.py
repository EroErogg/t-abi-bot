import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

# Deine ID und dein Bot-Token direkt integriert
OWNER_ID = 952555406381703218
TOKEN = "MTU0NDAzODU4MzQ4NzQzNDkxMw.GgfD16.GeyTvx5b0jfwonttGSrcWm75qzlMF8RffmdwTc"

# Intents aktivieren
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

class LiamCore(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ T ABI BOT Slash-Commands erfolgreich synchronisiert!")

bot = LiamCore()

@bot.event
async def on_ready():
    print(f"🚀 Bot ist online als {bot.user} (ID: {bot.user.id})")
    print("--------------------------------------------------")

# ==========================================
# 1. AUTOMATISCHES SERVER-SETUP (EXAKT WIE AUF DEN SCREENSHOTS)
# ==========================================
@bot.tree.command(name="setup_server", description="Erstellt exakt alle Kanäle und Emojis aus den Screenshots")
async def setup_server(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Du hast keine Berechtigung, diesen Befehl auszuführen!", ephemeral=True)
        return

    await interaction.response.send_message("⚙️ Server-Setup läuft... Erstelle Kanäle im exakten Design.", ephemeral=True)
    guild = interaction.guild

    try:
        # Standard-Berechtigungen für Info-Kanäle (Nur Lesen für Mitglieder)
        info_overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        # Streng geschützte Berechtigungen für Moderation
        mod_overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        # 1. Kategorie: Streams & Updates
        cat_streams = await guild.create_category("🔥 • UPDATES & STREAMS")
        await guild.create_text_channel("🔴 >live", category=cat_streams, overwrites=info_overwrites)
        await guild.create_text_channel("❤️ >strada-updates", category=cat_streams, overwrites=info_overwrites)
        await guild.create_text_channel("🗣️ >rollenvergabe", category=cat_streams, overwrites=info_overwrites)
        await guild.create_text_channel("💻 >server-invites", category=cat_streams, overwrites=info_overwrites)

        # 2. Kategorie: Willkommen
        cat_welcome = await guild.create_category("✨ • WILLKOMMEN")
        await guild.create_text_channel("💛 >willkommen", category=cat_welcome, overwrites=info_overwrites)
        await guild.create_text_channel("🚀 >boosts", category=cat_welcome, overwrites=info_overwrites)

        # 3. Kategorie: Informationen & Regeln
        cat_info = await guild.create_category("📌 • INFORMATIONEN")
        await guild.create_text_channel("🔊 >informationen", category=cat_info, overwrites=info_overwrites)
        await guild.create_text_channel("rules", category=cat_info, overwrites=info_overwrites)
        await guild.create_text_channel("moderator-only", category=cat_info, overwrites=mod_overwrites)

        # 4. Kategorie: Community
        cat_comm = await guild.create_category("💬 • COMMUNITY")
        await guild.create_text_channel("💬 >chat", category=cat_comm)
        await guild.create_text_channel("📷 >montagen", category=cat_comm)
        await guild.create_voice_channel("Talk 1", category=cat_comm)
        await guild.create_voice_channel("Talk 2", category=cat_comm)
        await guild.create_voice_channel("Talk 3", category=cat_comm)

        # 5. Kategorie: Support
        cat_support = await guild.create_category("🎧 • SUPPORT")
        await guild.create_text_channel("🎫 >ticket", category=cat_support)
        await guild.create_voice_channel("⏰ >Warteraum", category=cat_support)
        await guild.create_voice_channel("🔴 >Live", category=cat_support)
        await guild.create_voice_channel("🔴 >Warteschlange", category=cat_support)

        await interaction.followup.send("✅ Server-Setup erfolgreich abgeschlossen! Alle Kanäle sehen exakt aus wie auf deinen Screenshots.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Fehler beim Setup: {e}", ephemeral=True)

# ==========================================
# 2. WELCOME & AUTO-ROLLE ("abi's")
# ==========================================
@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="abi's")
    if role:
        try:
            await member.add_roles(role)
        except Exception as e:
            print(f"Fehler beim Auto-Rollen: {e}")
    
    channel = discord.utils.get(member.guild.text_channels, name="💛 >willkommen")
    if channel:
        embed = discord.Embed(
            title="✨ Willkommen auf LiamAbi!",
            description=f"Ey {member.mention}, willkommen in der Community! Schau dich in den Kanälen um und hab eine gute Zeit.",
            color=0x9b59b6
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="T ABI BOT Automation")
        await channel.send(embed=embed)

# ==========================================
# 3. BOOSTER SYSTEM
# ==========================================
@bot.event
async def on_member_update(before, after):
    if before.premium_since is None and after.premium_since is not None:
        channel = discord.utils.get(after.guild.text_channels, name="🚀 >boosts")
        if channel:
            embed = discord.Embed(
                title="🚀 Neuer Server-Boost!",
                description=f"Vielen Dank {after.mention} für den Boost! Du bist eine absolute Legende.",
                color=0xf47fff
            )
            embed.set_thumbnail(url=after.display_avatar.url)
            await channel.send(embed=embed)

# ==========================================
# 4. TICKET SYSTEM (MIT DROPDOWN)
# ==========================================
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Support", description="Allgemeine Hilfe und Fragen", emoji="🛟"),
            discord.SelectOption(label="Live-Frage", description="Fragen zu Streams oder Live-Inhalten", emoji="🔴"),
            discord.SelectOption(label="Strada-Frage", description="Fragen rund um Strada", emoji="🔥"),
        ]
        super().__init__(placeholder="Wähle dein Anliegen für das Ticket...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="🎧 • SUPPORT")
        if not category:
            category = await guild.create_category("🎧 • SUPPORT")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        channel_name = f"ticket-{interaction.user.name}-{self.values[0].lower().replace(' ', '-')}"
        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

        embed = discord.Embed(
            title=f"Ticket: {self.values[0]}",
            description=f"Willkommen {interaction.user.mention}!\nDas Team wird sich gleich um dein Anliegen kümmern. Klicke unten auf den Button, um das Ticket zu schließen.",
            color=0x2ecc71
        )
        
        await ticket_channel.send(embed=embed, view=TicketCloseView())
        await interaction.response.send_message(f"Dein Ticket wurde erstellt: {ticket_channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket schließen", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket wird in 5 Sekunden gelöscht...", ephemeral=True)
        await asyncio.sleep(5)
        await interaction.channel.delete()

@bot.tree.command(name="setup_ticket", description="Sendet das Ticket-Panel in den aktuellen Kanal")
@app_commands.checks.has_permissions(administrator=True)
async def setup_ticket(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 Support & Tickets",
        description="Wähle unten im Menü dein Anliegen aus, um einen privaten Support-Kanal zu öffnen.",
        color=0x3498db
    )
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("Ticket-Panel erfolgreich erstellt!", ephemeral=True)

# ==========================================
# 5. MODERATION & BAN SYSTEM
# ==========================================
@bot.tree.command(name="ban", description="Bannt einen User vom Server")
@app_commands.checks.has_permissions(ban_members=TypeError if False else bool) # Standard check
async def ban(interaction: discord.Interaction, member: discord.Member, grund: str = "Kein Grund angegeben"):
    await member.ban(reason=grund)
    embed = discord.Embed(title="🔨 Benutzer gebannt", description=f"{member.mention} wurde erfolgreich gebannt.\nGrund: {grund}", color=0xe74c3c)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="clear", description="Löscht eine bestimmte Anzahl an Nachrichten")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, anzahl: int):
    await interaction.channel.purge(limit=anzahl)
    await interaction.response.send_message(f"Es wurden {anzahl} Nachrichten gelöscht.", ephemeral=True)

# ==========================================
# 6. EXTRA FEATURE: SERVER STATS
# ==========================================
@bot.tree.command(name="stats", description="Zeigt die aktuellen Server-Statistiken")
async def stats(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"📊 Statistiken für {guild.name}", color=0xf1c40f)
    embed.add_field(name="Mitglieder", value=str(guild.member_count), inline=True)
    embed.add_field(name="Boosts", value=str(guild.premium_subscription_count), inline=True)
    embed.add_field(name="Server Owner", value=str(guild.owner), inline=False)
    embed.set_footer(text="T ABI BOT System")
    await interaction.response.send_message(embed=embed)

# Bot starten
bot.run(TOKEN)