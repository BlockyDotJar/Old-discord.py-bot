import random
import asyncio
import discord

from discord import Member, Guild, User

client = discord.Client(intents=discord.Intents.all())

antworten = ["Ja", "Nein", "Vielleicht", "Wahrscheinlich", "Sieht so aus", "Sehr wahrscheinlich",
             "Sehr unwahrscheinlich"]

autoroles = {
    819142076469215272: {"memberroles": [819476414779752501], "botroles": [819281006028652574, 819263750540230736]}
}


@client.event
async def on_ready():
    print("Wir sind als eingeloggt als User {}".format(client.user.name))
    client.loop.create_task(status_task())


async def status_task():
    colors = [discord.Colour.red(), discord.Colour.orange(), discord.Colour.gold(), discord.Colour.green(),
              discord.Colour.blue(), discord.Colour.purple()]
    while True:
        await client.change_presence(activity=discord.Game("MK!help"), status=discord.Status.online)
        await asyncio.sleep(5)
        await client.change_presence(activity=discord.Game("Leute aus Spaß warnen 😈"),
                                     status=discord.Status.online)
        await asyncio.sleep(5)
        await client.change_presence(activity=discord.Game("Melonen Mail - DM für Support"),
                                     status=discord.Status.online)
        await asyncio.sleep(5)
        guild: Guild = client.get_guild(748897417390456873)
        if guild:
            role = guild.get_role(827910708142145536)
            if role:
                if role.position < guild.get_member(client.user.id).top_role.position:
                    await role.edit(colour=random.choice(colors))


def is_not_pined(mess):
    return not mess.pinned


@client.event
async def on_member_join(member):
    guild: Guild = member.guild
    if not member.bot:
        embed = discord.Embed(title="<a:ArrowRightGlow:815668040771436555> Willkommen auf unserem super coolen Discord!"
                              .format(member.name),
                              description="Ich hoffe du hast viel Spaß <a:acongablob:815668257633599489>",
                              color=0x47ff78)
        try:
            if not member.dm_channel:
                await member.create_dm()
            await member.dm_channel.send(embed=embed)
        except discord.errors.Forbidden:
            print("Es konnte keine Willkommensnachricht an {} gesendet werden".format(member.name))
        autoguild = autoroles.get(guild.id)
        if autoguild and autoguild["memberroles"]:
            for roleid in autoguild["memberroles"]:
                role = guild.get_role(roleid)
                if role:
                    await member.add_roles(role, reason="AutoRoles", atomic=True)
    else:
        autoguild = autoroles.get(guild.id)
        if autoguild and autoguild["botroles"]:
            for roleid in autoguild["botroles"]:
                role = guild.get_role(roleid)
                if role:
                    await member.add_roles(role, reason="AutoRoles", atomic=True)


@client.event
async def on_message(message):
    if message.author.bot:
        return
    if "help-1" in message.content:
        await message.channel.send("***Seite 1***  von **2**\r\n"
                                   "**Admin Commands:**\r\n"
                                   "`MK!addGlobal` - *Addet den Globalchat,"
                                   " in den Channel wo dieser Command geschrieben wird*\n"
                                   "`MK!removeGlobal` - *Removet den Globalchat von dem Chat*\n"
                                   "`MK!warn @User (Grund)` - *Warnt den angegebenen User*\n"
                                   "`MK!warnings @user`- *Zeigt dir alle Verwarnungen des Users an*\n"
                                   "`MK!config_ticket [Nachrichten ID] {Kategorie ID}` - *Fügt zu der angegebenen "
                                   "Nachricht den :ticket: Emoji hinzu und wenn man mit dem Emoji interagiert öffnet "
                                   "sich ein Ticket wo nur die Perosn die mit Emoji interagiert hat und das Team "
                                   "reinschauen kann (Man muss eine Rolle die **Admin** heißt haben um das "
                                   "durchführen zu können)*\n"
                                   "**Team Commands:**\r\n"
                                   "`MK!gstart` - *Veranstaltet ein Giveaway*\n"
                                   "`MK!greroll (Giveawaynachrichten ID) [Kategorie ID]` - *Das Giveaway bekommt "
                                   "andere/neue Gewinner*\n"
                                   "`MK!kick (Username)` - *Kickt einen Member von dem Server*\n"
                                   "`MK!ban (Username)` - *Bannt einen User auf unbestimmte Zeit*\n"
                                   "`MK!unban (Username)` - *Entbannt einen gabannten User*\n"
                                   "`MK!clear (Nachrichtenanzahl)` - *Cleart die nächsten x Nachrichten*\n"
                                   "**Hilfe zum Bot:**\r\n"
                                   "`MK!help-1` - *Zeigt dir die 1. Hilfe Seite mit Commands an*\n"
                                   "`MK!help-2` - *Zeigt dir die 2. Hilfe Seite mit Commands an*\n"
                                   "`MK?help` - *Zeigt dir alle Melonen Mail Commands an*\n"
                                   "`MK!userinfo (Username)` - *Zeigt dir Informationen über einen User an*\n"
                                   "`MK!stats/MK!stats @User` - *Zeigt dir deine Stats wie **aktuelles Level**, "
                                   "**exp Stand**, **Rank** und **Level Fortschritt** an*\n"
                                   "`MK!leaderboard` - *Zeigt dir die höchst gelevelten User an*\n"
                                   "`MK=Stadt` - *Zeigt dir das aktuelle Wetter von einer angegebenen Stadt an*\n"
                                   "**Fun:**\r\n"
                                   "`MK!bal/MK!balance` - *Zeigt dir deinen Konto Stand an und wie viel Geld du in "
                                   "deiner Brieftasche hast*\n"
                                   "`MK!beg` - *Du bekommst Geld indem du darum bettelst*\n"
                                   "`MK!with/MK!withdraw` - *Du buchst Geld von deinem Bankkonto ab*\n"
                                   "`MK!dep/MK!deposit` - *Du deponierst Geld in deiner Bank*\n")
    if message.content.startswith("MK!help-2"):
        await message.channel.send("***Seite 2***  von **2**\r\n"
                                   "`MK!send @User (Geldbetrag)` - *Du gibst einen User Geld*\n"
                                   "`MK!rob @User` - *Du raubst einen User aus*\n"
                                   "`MK!slot (Geldbetrag)` - *DU spielst ein Slotmaschinen Spiel, wenn man gewinnt "
                                   "bekommt man 3 mal so viel Geld zurück wie man geboten hat*\n"
                                   "`MK!shop` - *Zeigt dir den Shop an*\n"
                                   "`MK!buy (item) [Anzahl]` - *Du kaufst ein Item aus dem Shop*\n"
                                   "`MK!sell (item) [Anzahl]` - *Du verkaufst ein Item das du bereits besitzt und "
                                   "bekommst denn vollen Betrag wieder*\n "
                                   "`MK!bag` - *Zeigt dir alle gekauften Items an*\n"
                                   "`MK!lb (Zahl wie viele Top Person angezeigt werden sollen)` - *Zeigt die Top x "
                                   "der besten Blockonomy Spieler an*\n "
                                   "`MK!tictactoe @Du @User` - *Du startest eine Tic Tac Toe Runde*\n"
                                   "`MK!place (Zahl von 1-9)` - *Makiert eine Stelle für dich*\n"
                                   "`MK!8ball (Frage)` - *Stelle dem Bot eine Frage und er beantwortet sie "
                                   "(100% Wahrheitsgehalt)*\n"
                                   "**Sonstige:**\r\n"
                                   "`Slash Commands` - *Wenn man /guess start:Zahl stop:Zahl macht antwortet dir der "
                                   "Bot mit einer zufälligen Zahl (Dies ist nur ein Test Command echte werden noch "
                                   "folgen)*\n"
                                   "`Level System` - *Man bekommt XP für Nachrichten und Levelt somit auf*\n"
                                   "`AutoRoles` - *Wenn ein User joint bekommt er die **Community** Rolle"
                                   " und wenn ein Bot joint bekommt dieser die **Bot** Rolle*\n"
                                   "`Willkommensnachricht` - *Sendet eine Private Nachricht an einen User, "
                                   "der gerade gejoint ist*\n")
    if message.content.startswith("MK!ban") and message.author.guild_permissions.ban_members:
        args = message.content.split(" ")
        if len(args) == 2:
            member: Member = discord.utils.find(lambda m: args[1] in m.name, message.guild.members)
            if member:
                await member.ban()
                await message.channel.send(f"Du hast {member.name} gebannt <a:acongablob:815668257633599489>")
            else:
                await message.channel.send(f"Kein User mit dem Namen {args[1]} gefunden. "
                                           f"Dieser User existiert entweder nicht oder du hast in falsch geschrieben.")
    if message.content.startswith("MK!unban") and message.author.guild_permissions.ban_members:
        args = message.content.split(" ")
        if len(args) == 2:
            user: User = discord.utils.find(lambda banentry: args[1] in banentry.user.name,
                                            await message.guild.bans()).user
            if user:
                await message.guild.unban(user)
                await message.channel.send(f"Du hast {user.name} entbannt <a:among_dance:801390220854820874>")
            else:
                await message.channel.send(f"Kein User mit dem Namen {args[1]} gefunden. "
                                           f"Dieser User existiert entweder nicht oder du hast in falsch geschrieben.")
    if message.content.startswith("MK!kick") and message.author.guild_permissions.kick_members:
        args = message.content.split(" ")
        if len(args) == 2:
            member: Member = discord.utils.find(lambda m: args[1] in m.name, message.guild.members)
            if member:
                await member.kick()
                await message.channel.send(f"Du hast {member.name}  gekickt <a:blob_aufgeregt:801390684497903617>")
            else:
                await message.channel.send(f"Kein User mit dem Namen {args[1]} gefunden. "
                                           f"Dieser User existiert entweder nicht oder du hast in falsch geschrieben.")
    if message.content.startswith("MK!clear"):
        if message.author.permissions_in(message.channel).manage_messages:
            args = message.content.split(" ")
            if len(args) == 2:
                if args[1].isdigit():
                    count = int(args[1]) + 1
                    deleted = await message.channel.purge(limit=count, check=is_not_pined)
                    await message.channel.send("{} Nachrichten gelöscht.".format(len(deleted) - 1))
    if message.content.startswith("MK!8ball"):
        args = message.content.split(" ")
        if len(args) >= 2:
            frage = " ".join(args[1:])
            mess = await message.channel.send("Ich versuche deine Frage `{0}` zu beantworten.".format(frage))
            await asyncio.sleep(2)
            await mess.edit(content="Ich kontaktiere das Orakel...")
            await asyncio.sleep(2)
            await mess.edit(content="Deine Antwort zur Frage `{0}` lautet: `{1}`".format(frage,
                                                                                         random.choice(antworten)))


client.run("ODEyMzM1MDEyNzI4NDA2MDQ2.YC_P7w.nT9CO_Nt5jcZz5wblVicWOOSf_w")
