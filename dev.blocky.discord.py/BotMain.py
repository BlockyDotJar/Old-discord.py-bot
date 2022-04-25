import json
import random
import asyncio
import os
from datetime import datetime

import pytz
import aiofiles
from discord import Guild

import discord
from discord.ext import commands

client = commands.Bot(command_prefix=commands.when_mentioned_or(':'), help_command=None,
                      intents=discord.Intents.all())

client.ticket_configs = {}

antworten = ["Ja", "Nein", "Vielleicht", "Wahrscheinlich", "Sieht so aus", "Sehr wahrscheinlich",
             "Sehr unwahrscheinlich"]

autoroles = {
    819142076469215272: {"memberroles": [819476414779752501], "botroles": [819281006028652574, 819263750540230736]}
}

client.warnings = {}


###########################################################

@client.event
async def on_ready():
    print("Wir sind als eingeloggt als User {}".format(client.user.name))


@client.event
async def on_member_join(member):
    guild: Guild = member.guild
    if not member.bot:
        embed = discord.Embed(title="<a:ArrowRightGlow:815668040771436555> Herzlich Willkommen!"
                              .format(member.name),
                              description=f"Herzlich willkommen auf `{guild.name}'s` Discord ^^\n"
                                          f"Wir wünschen dir **{member.name}** ganz viel Spaß, aber immer "
                                          f"schön an die Regeln halten :D",
                              color=0x47ff78, timestamp=datetime.utcnow())
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
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Du kannst dies nicht tun ;-;\n"
                       "Grund: **Fehlendes erfoderliches Argument**")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("Du kannst diesen Command nicht benutzen ;-;\n"
                       "Grund: **Fehlende Berechtigung/en**")
    elif isinstance(error, commands.MissingRole):
        await ctx.send("Du kannst diesen Command nicht benutzen ;-;\n"
                       "Grund: **Fehlende Rolle/n**")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("Ich kann dies nicht tun ;-;\n"
                       "Grund: **Ich habe keine Rechte dies zu machen**")
    elif isinstance(error, commands.BotMissingAnyRole):
        await ctx.send("Ich kann dies nicht tun ;-;\n"
                       "Grund: **Ich habe keine einzige Rolle und daher auch keine Berechtigung diesen Befehl "
                       "auszuführen**")


@client.command()
async def help_me(ctx):
    embed = discord.Embed(title="Hilfe", description="⬆️ _ _ 》 **Allgemeine Commands**\n"
                                                     "⬅️ _ _ 》 **Team Commands**\n"
                                                     "➡️ _ _ 》 **Admin Commands**\n"
                                                     "⬇️ _ _ 》 **Fun Commands**\n"
                                                     "😯    _ _ 》 **Sonstiges**", color=0x7289DA)
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction(u"\u2B06")
    await msg.add_reaction(u"\u2B05")
    await msg.add_reaction(u"\u27A1")
    await msg.add_reaction(u"\u2B07")
    await msg.add_reaction(u"\U0001F62F")

    try:
        reaction, user = await client.wait_for("reaction_add",
                                               check=lambda reaction, user: user == ctx.author and reaction.emoji in [
                                                   u"\u27A1", u"\u2B05", u"\u2B06", u"\u2B07", u"\U0001F62F"],
                                               timeout=30.0)
    except asyncio.TimeoutError:
        await ctx.channel.send("Die Zeit ist Abgelaufen.")

    else:
        if reaction.emoji == u"\u27A1":
            embed = discord.Embed(title="Admin Commands",
                                  description="`MK!info` - *Zeigt allgemeine Statistiken zum Bot*\n"
                                              "`MK!addGlobal` - *Fügt den Globalchat zu diesem Channel hinzu.(Soon)*\n"
                                              "`MK!removeGlobal` - *Entfernt den Globalchat von diesem Channel.("
                                              "Soon)*\n "
                                              "`MK!addtempchannel (Voicechannel ID)` - *Fügt den Channel als "
                                              "Tempchannel hinzu*\n"
                                              "`MK!removetempchannel (Voicechannel ID)` - *Entfernt den Tempchannel "
                                              "wieder*\n"
                                              "`MK!warn @User (Grund)` - *Warnt den angegebenen User*\n"
                                              "`MK!warnings @User`- *Zeigt dir alle Verwarnungen des Users an*\n"
                                              "`MK!config_ticket [Nachrichten ID] {Kategorie ID}` - *Fügt zu der "
                                              "angegebenen Nachricht den  Emoji hinzu und wenn man mit diesem Emoji "
                                              "interagiert, öffnet sich ein Ticket, in welches nur die Person, "
                                              "die das Ticket erstellt hat und das Team reinschauen kann.*",
                                  color=0x00fff7, timestamp=datetime.utcnow())
            await ctx.channel.send(embed=embed)

        if reaction.emoji == u"\u2B05":
            embed = discord.Embed(title="Team Commands",
                                  description="`MK!gstart` - *Veranstaltet ein Giveaway (Um den Command verwenden zu "
                                              "können muss man **Rollen verwalten** Berechtigungen haben)*\n"
                                              "`MK!greroll (Channel ID) (Giveawaynachrichten ID)` - *Das Giveaway "
                                              "bekommt andere/neue Gewinner (Um den Command verwenden zu können muss "
                                              "man **Rollen verwalten** Berechtigungen haben)*\n"
                                              "`MK!kick (User)` - *Kickt einen Member von dem Server*\n"
                                              "`MK!ban (User ID)` - *Bannt einen Member auf unbestimmte Zeit*\n"
                                              "`MK!unban (User ID)` - *Entbannt einen gabannten Member*\n"
                                              "`MK!clear (Nachrichtenanzahl)` - *Cleart die nächsten x Nachrichten*\n"
                                              "`MK!mute @User (Grund)` - *Mutet einen User so das er nichts mehr "
                                              "schreiben "
                                              "kann (Um den Command verwenden zu können muss man **Nachrichten "
                                              "verwalten** "
                                              "Berechtigungen haben)*\n"
                                              "`MK!unmute @User` - *Entmutet einen User so das er wieder schreiben "
                                              "kann "
                                              "(Um den Command verwenden zu können muss man "
                                              "**Nachrichten verwalten** Berechtigungen haben)*",
                                  color=0x00fff7, timestamp=datetime.utcnow())
            await ctx.channel.send(embed=embed)

        if reaction.emoji == u"\u2B06":
            embed = discord.Embed(title="Allgemeine Commands",
                                  description="`MK!help_me` - *Zeigt dir alle Hilfs Kategorien an*\n"
                                              "`MK!userinfo (User)` - *Zeigt dir Informationen über einen User an*\n"
                                              "`MK!ping` - *Zeigt dir den aktuellen Ping des Bots an*\n",
                                  color=0x00fff7, timestamp=datetime.utcnow())
            await ctx.send(embed=embed)

        if reaction.emoji == u"\u2B07":
            embed = discord.Embed(title="Fun Commands",
                                  description="`MK!bal/MK!balance` - *Zeigt dir deinen Konto Stand an und wie viel "
                                              "Geld du in "
                                              "deiner Brieftasche hast*\n"
                                              "`MK!beg` - *Du bekommst Geld, indem zu darum bettelst*\n"
                                              "`MK!with/MK!withdraw (Geldbetrag)` - *Du buchst Geld von deinem "
                                              "Bankkonto ab*\n"
                                              "`MK!dep/MK!deposit (Geldbetrag)` - *Du deponierst Geld in deiner Bank*\n"
                                              "`MK!send/give @User (Geldbetrag)` - *Du gibst einem User Geld*\n"
                                              "`MK!rob @User` - *Du raubst einen User aus*\n"
                                              "`MK!slot (Geldbetrag)` - *Du spielst ein Slotmaschinen Spiel, wenn man "
                                              "gewinnt bekommt man 3 mal so viel Geld zurück, wie man geboten hat*\n "
                                              "`MK!shop` - *Zeigt dir den Shop an*\n"
                                              "`MK!buy (item) [Anzahl]` - *Du kaufst ein Item aus dem Shop*\n"
                                              "`MK!sell (item) [Anzahl]` - *Du verkaufst ein Item das du bereits "
                                              "besitzt und bekommst denn vollen Betrag wieder*\n "
                                              "`MK!collectincome/collect` - *Gibt dir ein bisschen Geld*\n"
                                              "`MK!daily` - *Gibt dir einen täglichen Betrag an Geld*\n"
                                              "`MK!bag` - *Zeigt dir alle gekauften Items an*\n"
                                              "`MK!leaderboard/lb (Zahl wie viele Top Person angezeigt werden sollen)` "
                                              "- *Zeigt die Top x der besten Blockonomy Spieler an*\n"
                                              "`MK!aktiennews/aktien-news/aktien_news` - *Man erhält Informationen "
                                              "über Sachen wie einen steigende Aktienkurs und/oder einen "
                                              "fallende Aktienkurse.*\n"
                                              "`MK!tictactoe @Du @User` - *Du startest eine TicTacToe Runde*\n"
                                              "`MK!place (Zahl von 1-9)` - *Makiert eine Stelle für dich*\n"
                                              "`MK!forecast/8ball (Frage)` - *Stelle dem Bot eine Frage und er"
                                              " beantwortet sie (100% Wahrheitsgehalt)*",
                                  color=0x00fff7, timestamp=datetime.utcnow())
            await ctx.send(embed=embed)

        if reaction.emoji == u"\U0001F62F":
            embed = discord.Embed(title="Sonstiges",
                                  description="`Prefix` - *Wenn man den Bot Pingt und dahinter prefix schreibt zeigt "
                                              "dir der "
                                              "Bot an welchen Prefix er aktuell hat*\n"
                                              "`Willkommensnachricht` - *Sendet eine Private Nachricht an einen User, "
                                              "der gerade gejoint ist*\n", color=0x00fff7, timestamp=datetime.utcnow())
            await ctx.send(embed=embed)


@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.User):
    guild = ctx.guild
    await guild.ban(user=user)
    await ctx.send(f"{user.mention} wurde erfolgreich **gebannt** <:ban_hammer:843745190664470538>")
    await ctx.send("https://tenor.com/view/samdreamsmaker-samuel-guizani-pokemon-mmo3d-admin-banned-gif-14845624")


@client.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user: discord.User):
    guild = ctx.guild
    await guild.unban(user=user)
    await ctx.send(f"{user.mention} wurde erfolgreich **entbannt** <:unban_hammer:843746164805599245>")


@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member):
    await member.kick()
    await ctx.send(f"{member.mention} wurde erfolgreich **gekickt** <:Kick:843746993650401310>")


@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=5):
    await ctx.message.delete()
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"{amount} Nachrichten wurden gelöscht 🗑️", delete_after=3)


@client.command()
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True)

    await member.add_roles(mutedRole, reason=reason)
    await ctx.send(f"{member.mention} wurde erfolgreich gemuted. 🤫 Grund: {reason}")
    await member.send(f"Du wurdest auf dem {guild.name} Discord Server gemuted. Grund: {reason}")


@client.command()
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
    muteRole = discord.utils.get(ctx.guild.roles, name="Muted")

    await member.remove_roles(muteRole)
    await ctx.send(f"{member.mention} wurde erfolgreich entmuted. 🔊")
    await member.send(f"Du wurdest auf dem {ctx.guild.name} Discord Server entmuted.")


@client.command(aliases=["8ball"])
async def forecast(ctx, *, frage):
    mess = await ctx.send(f"Ich versuche deine Frage `{frage}` zu beantworten.")
    await asyncio.sleep(2)
    await mess.edit(content="Ich kontaktiere das Orakel...")
    await asyncio.sleep(2)
    await mess.edit(content=f"Deine Antwort zur Frage `{frage}` lautet: `{random.choice(antworten)}`")


###########################################################

mainshop = [{"Name": "Schokolade", "Preis": 10, "Beschreibung": "Essen"},
            {"Name": "Taschenuhr", "Preis": 100, "Beschreibung": "Zeit"},
            {"Name": "Handy", "Preis": 500, "Beschreibung": "Kommunikation"},
            {"Name": "Laptop", "Preis": 1000, "Beschreibung": "Arbeit"},
            {"Name": "PC", "Preis": 5000, "Beschreibung": "Gaming"},
            {"Name": "Privatjet", "Preis": 10000, "Beschreibung": "Mobilität"},
            {"Name": "Villa", "Preis": 500000, "Beschreibung": "Wohnen"},
            {"Name": "Diamant", "Preis": 1000000, "Beschreibung": "Schmuck"},
            {"Name": "Bitcoin", "Preis": 10000000, "Beschreibung": "Geld"},
            {"Name": "BIONTECH SE", "Preis": 10000000000, "Beschreibung": "Aktie"},
            {"Name": "Tesla", "Preis": 10000000000, "Beschreibung": "Aktie"},
            {"Name": "Amazon", "Preis": 10000000000, "Beschreibung": "Aktie"},
            {"Name": "Microsoft", "Preis": 10000000000, "Beschreibung": "Aktie"},
            {"Name": "GAMESTOP", "Preis": 10000000000, "Beschreibung": "Aktie"},
            {"Name": "BMW", "Preis": 10000000000, "Beschreibung": "Aktie"}]

BionTechKurs = "+1,20%"
TeslaKurs = "+3,34%"
AmazonKurs = "+0,28%"
MicrosoftKurs = "+0,074%"
GAMESTOPKurs = "+0,36%"
BMWKurs = "+0,71%"


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = "**Du hast gerade einen cooldown!**, du kannst diesen Command in `{:.2f}` " \
              "Sekunden wieder nutzen! 🕐".format(error.retry_after)
        await ctx.send(msg)


@client.command(aliases=["aktiennews", "aktien-news"])
async def aktien_news(ctx):
    embed = discord.Embed(title="Tägliche Aktien-News 💸", description="Hier erhältst du Informationen über Sachen "
                                                                       "wie...\n"
                                                                       "...steigende Aktienkurse.\n"
                                                                       "...fallende Aktienkurse.\n", color=0x7df5e5,
                          timestamp=datetime.utcnow())
    embed.add_field(name="BIONTECH SE Aktie", value=f"Der BIONTECH SE Aktienkurs Prozentsatz beträgt heute: "
                                                    f"**{BionTechKurs}**")
    embed.add_field(name="Tesla Aktie", value=f"Der Tesla Aktienkurs Prozentsatz beträgt heute: **{TeslaKurs}**")
    embed.add_field(name="Amazon Aktie", value=f"Der Amazon Aktienkurs Prozentsatz beträgt heute: **{AmazonKurs}**")
    embed.add_field(name="Microsoft Aktie", value=f"Der Microsoft Aktienkurs Prozentsatz beträgt heute: "
                                                  f"**{MicrosoftKurs}**")
    embed.add_field(name="GAMESTOP Aktie", value=f"Der GAMESTOP Aktienkurs Prozentsatz beträgt heute: "
                                                 f"**{GAMESTOPKurs}**")
    embed.add_field(name="BMW Aktie", value=f"Der BMW Aktienkurs Prozentsatz beträgt heute: **{BMWKurs}**")
    embed.set_footer(text="Das waren die Live News 24")
    await ctx.send(embed=embed)


@client.command(aliases=["bal"])
async def balance(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["Bank"]

    embed = discord.Embed(title=f"{ctx.author.name}`s Kontostand 🏦", color=0x00ffe5)
    embed.add_field(name="Brieftasche", value=f"`{wallet_amt}€`")
    embed.add_field(name="Bank", value=f"`{bank_amt}€`")
    await ctx.send(embed=embed)


@client.command()
@commands.cooldown(5, 60, commands.BucketType.user)
async def beg(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()

    user = ctx.author

    earnings = random.randrange(101)

    await ctx.send(f"Jemand hat dir **{earnings}** Coin`s gegeben!!! 😱 :coin:")

    users[str(user.id)]["wallet"] += earnings

    with open("mainbank.json", "w") as f:
        json.dump(users, f)


@client.command(aliases=["collect"])
@commands.cooldown(1, 3600, commands.BucketType.user)
async def collectincome(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()

    user = ctx.author

    earnings = random.randrange(1000)

    embed = discord.Embed(title=f"{ctx.author.name}", color=0x4d8efa,
                          description="<:check"":839098117613813771> Erfolgreich eingesammelt "
                                      "<a:coin_animated:839121965499023390>\n")
    embed.add_field(name="Einkommen", value=f"Dein Einkommen beträgt: **{earnings}** Coins`s! :coin:")
    await ctx.send(embed=embed)

    users[str(user.id)]["Bank"] += earnings

    with open("mainbank.json", "w") as f:
        json.dump(users, f)


@client.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def daily(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()

    user = ctx.author

    earnings = random.randrange(1000)

    embed = discord.Embed(title=f"{ctx.author.name}", color=0x325ea8,
                          description="<a:verified_blue:815667711774031922> "
                                      "Tägliche Belohnung Erfolgreich "
                                      "eingesammelt "
                                      "<a:coin_animated:839121965499023390>"
                                      "\n")
    embed.add_field(name="Tägliche Belohnung:", value=f"Deine Täglich Belohnung beträgt: **{earnings}** Coin`s! :coin:")
    await ctx.send(embed=embed)

    users[str(user.id)]["Bank"] += earnings

    with open("mainbank.json", "w") as f:
        json.dump(users, f)


@client.command(aliases=["with"])
async def withdraw(ctx, amount=None):
    await open_account(ctx.author)

    if amount is None:
        await ctx.send("Bitte gib den Betrag an! 🔢")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[1]:
        await ctx.send("Du hast nicht genug Geld! 🙅‍♂")
        return
    if amount < 0:
        await ctx.send("Der Geldbetrag muss im + Bereich sein! 🙃")
        return

    await update_bank(ctx.author, amount)
    await update_bank(ctx.author, -1 * amount, "Bank")

    await ctx.send(f"Du hast **{amount}** Coin`s von deinem Bank Konto abgehoben 🏦 💵")


@client.command(aliases=["dep"])
async def deposit(ctx, amount=None):
    await open_account(ctx.author)

    if amount is None:
        await ctx.send("Bitte gib den Betrag an! 🔢")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[0]:
        await ctx.send("Du hast nicht genug Geld! 🙅‍♂")
        return
    if amount < 0:
        await ctx.send("Der Geldbetrag muss im + Bereich sein! 🙃")
        return

    await update_bank(ctx.author, -1 * amount)
    await update_bank(ctx.author, amount, "Bank")

    await ctx.send(f"Du hast **{amount}** Coin`s deponiert 🏦 💵")


@client.command(aliases=["give"])
async def send(ctx, member: discord.Member, amount=None):
    await open_account(ctx.author)
    await open_account(member.id)

    if amount is None:
        await ctx.send("Bitte gib den Betrag an! 🔢")
        return

    bal = await update_bank(ctx.author)
    if amount == "all":
        amount = bal[0]

    amount = int(amount)
    if amount > bal[1]:
        await ctx.send("Du hast nicht genug Geld! 🙅‍♂")
        return
    if amount < 0:
        await ctx.send("Der Geldbetrag muss im + Bereich sein! 🙃")
        return

    await update_bank(ctx.author, -1 * amount, "Bank")
    await update_bank(member.id, amount, "Bank")

    await ctx.send(f"Du hast **{amount}** Coin`s an {member.mention} vergeben <a:moneyyyy:837654704556605450>")


@client.command()
@commands.cooldown(1, 300, commands.BucketType.user)
async def rob(ctx, member: discord.Member):
    await open_account(ctx.author)
    await open_account(member.id)

    bal = await update_bank(member.id)

    if bal[0] < 100:
        await ctx.send("Dir bringt es nichts einen User der unter 100 Coins hat auszurauben!  🙅‍♂")
        return

    earnings = random.randrange(0, bal[0])

    await update_bank(ctx.author, earnings)
    await update_bank(member.id, -1 * earnings)

    await ctx.send(f"Du hast {member.mention} ausgeraubt und hast **{earnings}** Coin`s gestohlen! "
                   f"<a:blob_schnell:831427448050679828>")


@client.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def slot(ctx, amount=None):
    await open_account(ctx.author)

    if amount is None:
        await ctx.send("Bitte gib den Betrag an! 🔢")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[0]:
        await ctx.send("Du hast nicht genug Geld! 🙅‍♂")
        return
    if amount < 0:
        await ctx.send("Der Geldbetrag muss im + Bereich sein! 🙃")
        return

    final = []
    for i in range(3):
        a = random.choice([":watermelon:", ":tada:", ":star:"])

        final.append(a)

    await ctx.send(str(final))

    if final[0] == final[1] or final[0] == final[2] or final[2] == final[1]:
        await update_bank(ctx.author, 2 * amount)
        await ctx.send("Du hast gewonnen !!! <a:tada_animated:815667511629840454>")
    else:
        await update_bank(ctx.author, -1 * amount)
        await ctx.send("Du hast leider verloren <a:blob_aufgeregt:801390684497903617> Vielleicht wird es beim "
                       "nächstem mal ja was")


@client.command()
async def shop(ctx):
    embed = discord.Embed(title=f"Willkommen im Shop! 🛒", color=0xffc800)

    for item in mainshop:
        name = item["Name"]
        price = item["Preis"]
        desc = item["Beschreibung"]
        embed.add_field(name=name, value=f"`{price}€` **|** *{desc}*")

    await ctx.send(embed=embed)


@client.command()
async def buy(ctx, item, amount=1):
    await open_account(ctx.author)

    res = await buy_this(ctx.author, item, amount)

    if not res[0]:
        if res[1] == 1:
            await ctx.send("Dieses Objekt existiert nicht! 🙅‍♂")
            return
        if res[1] == 2:
            await ctx.send(f"Du hast nicht genug Geld in deiner Brieftasche um **{amount}** `{item}` zu kaufen 🙅‍♂ 💵")
            return

    await ctx.send(f"Du hast gerade **{amount}** `{item}` gekauft <a:tada_animated:815667511629840454>")


@client.command()
async def bag(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    try:
        bag = users[str(user.id)]["Tasche"]
    except:
        bag = []

    embed = discord.Embed(title="Tasche", color=0x4f3a00)
    for item in bag:
        name = item["item"]
        amount = item["amount"]

        embed.add_field(name=name, value=amount)

    await ctx.send(embed=embed)


@client.command(aliases=["lb"])
async def leaderboard(ctx, x=1):
    users = await get_bank_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["wallet"] + users[user]["Bank"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total, reverse=True)

    em = discord.Embed(title=f"Top {x} Reichste Personen", description="Dies ist ein Leaderboard, in dem die "
                                                                       "reichsten Leute, die das Economy System je "
                                                                       "benutzt haben, angezeigt werden. "
                                                                       "<a:moneyyyy:837654704556605450>",
                       color=discord.Color(0x8d99ff))
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = client.get_user(id_)
        name = member.name
        em.add_field(name=f"{index}. {name}", value=f"{amt}", inline=False)
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed=em)


async def buy_this(user, item_name, amount):
    global price
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["Name"].lower()
        if name == item_name:
            name_ = name
            price = item["Preis"]
            break

    if name_ is None:
        return [False, 1]

    cost = price * amount

    users = await get_bank_data()

    bal = await update_bank(user)

    if bal[0] < cost:
        return [False, 2]

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["Tasche"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["Tasche"][index]["amount"] = new_amt
                t = 1
                break
            index += 1
        if t is None:
            obj = {"item": item_name, "amount": amount}
            users[str(user.id)]["Tasche"].append(obj)
    except:
        obj = {"item": item_name, "amount": amount}
        users[str(user.id)]["Tasche"] = [obj]

    with open("mainbank.json", "w") as f:
        json.dump(users, f)

    await update_bank(user, cost * -1, "wallet")

    return [True, "Worked"]


@client.command()
async def sell(ctx, item, amount=1):
    await open_account(ctx.author)

    res = await sell_this(ctx.author, item, amount)

    if not res[0]:
        if res[1] == 1:
            await ctx.send("Dieses Objekt existiert nicht! 🙅‍♂")
            return
        if res[1] == 2:
            await ctx.send(f"Du hast nicht **{amount}** `{item}` in deiner Tasche 🙅‍♂")
            return
        if res[1] == 3:
            await ctx.send(f"Du hast `{item}` nicht in deiner Tasche 🙅‍♂")
            return

    await ctx.send(f"Du hast gerade **{amount}** `{item}` verkauft 💵")


async def sell_this(user, item_name, amount, price=None):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["Name"].lower()
        if name == item_name:
            name_ = name
            if price is None:
                price = item["Preis"]
            break

    if name_ is None:
        return [False, 1]

    cost = price * amount

    users = await get_bank_data()

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["Tasche"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - amount
                if new_amt < 0:
                    return [False, 2]
                users[str(user.id)]["Tasche"][index]["amount"] = new_amt
                t = 1
                break
            index += 1
        if t is None:
            return [False, 3]
    except:
        return [False, 3]

    with open("mainbank.json", "w") as f:
        json.dump(users, f)

    await update_bank(user, cost, "wallet")

    return [True, "Worked"]


async def open_account(user):
    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["Bank"] = 0

    with open("mainbank.json", "w") as f:
        json.dump(users, f)
    return True


async def get_bank_data():
    with open("mainbank.json", "r") as f:
        users = json.load(f)

    return users


async def update_bank(user, change=0, mode="wallet"):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open("mainbank.json", "w") as f:
        json.dump(users, f)

    bal = [users[str(user.id)]["wallet"], users[str(user.id)]["Bank"]]
    return bal


if os.path.isfile("servers.json"):
    with open('servers.json', encoding='utf-8') as f:
        servers = json.load(f)
else:
    servers = {"servers": []}
    with open('servers.json', 'w') as f:
        json.dump(servers, f, indent=4)


###########################################################


def convert(time):
    pos = ["s", "m", "h", "d"]

    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}

    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]


@client.command()
@commands.has_permissions(manage_roles=True)
async def gstart(ctx):
    await ctx.send("Beginnen wir mit diesem Giveaway! Beantworte diese Fragen innerhalb von 15 Sekunden! :alarm_clock:")

    questions = ["In welchem Kanal soll das Giveaway stattfinden?  🧐",
                 "Wie lange sollte das Giveaway gehen? <:thonk:750400537588924417> (s|m|h|d)",
                 "Was soll der Preis sein? :coin:"]

    answers = []

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    for i in questions:
        await ctx.send(i)

        try:
            msg = await client.wait_for('message', timeout=15.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send('Du hast nicht zeitgemäß geantwortet ⏳ Versuch es nochmal!')
            return
        else:
            answers.append(msg.content)

    try:
        c_id = int(answers[0][2:-1])
    except:
        await ctx.send(f"Du hast keinen Kanal ausgewählt. 🙅‍♂ Mach es das nächste mal so: {ctx.channel.mention}.")
        return

    channel = client.get_channel(c_id)

    time = convert(answers[1])
    if time == -1:
        await ctx.send(f"Du hast keine Zeit angegeben. 🙅‍♂ Benutze (s|m|h|d) das nächste mal!")
        return
    elif time == -2:
        await ctx.send(f"Die Zeit muss einen Integer enthalten. 🔢 Bitte benutze das nächste mal einen!")
        return

    prize = answers[2]

    await ctx.send(f"Das Giveaway findet in {channel.mention} statt und wird {answers[1]} lang gehen! "
                   f"<a:tada_animated:815667511629840454>")

    embed = discord.Embed(title="Giveaway!", description=f"Es gibt `{prize}` zu gewinnen!", color=0xFFC312)

    embed.add_field(name="Veranstaltet von:", value=ctx.author.mention)

    embed.set_footer(text=f"Endet in {answers[1]} ab jetzt!")

    my_msg = await channel.send(embed=embed)

    await my_msg.add_reaction("🎉")

    await asyncio.sleep(time)

    new_msg = await channel.fetch_message(my_msg.id)

    users = await new_msg.reactions[0].users().flatten()
    users.pop(users.index(client.user))

    winner = random.choice(users)

    await channel.send(f"<a:tada_animated:815667511629840454> Gratulation {winner.mention} du hast "
                       f"<a:ArrowRightGlow:815668040771436555> `{prize}` gewonnen! 😮")


@client.command()
@commands.has_permissions(manage_roles=True)
async def greroll(ctx, channel: discord.TextChannel, id_: int):
    try:
        new_msg = await channel.fetch_message(id_)
    except:
        await ctx.send("Die ID wurde falsch eingegeben. 🙅‍♂")
        return

    users = await new_msg.reactions[0].users().flatten()
    users.pop(users.index(client.user))

    winner = random.choice(users)

    await channel.send(f"<a:tada_animated:815667511629840454> Gratulation! Der neue Gewinner ist: "
                       f"<a:ArrowRightGlow:815668040771436555> {winner.mention}! 😮")


###########################################################


@client.event
async def on_ready():
    async with aiofiles.open("ticket_configs.txt", mode="a"):
        pass

    async with aiofiles.open("ticket_configs.txt", mode="r") as file:
        lines = await file.readlines()
        for line in lines:
            data = line.split(" ")
            client.ticket_configs[int(data[0])] = [int(data[1]), int(data[2]), int(data[3])]


@client.event
async def on_raw_reaction_add(payload):
    global category
    if payload.member.id != client.user.id and str(payload.emoji) == u"\U0001F3AB":
        msg_id, channel_id, category_id = client.ticket_configs[payload.guild_id]

        if payload.message_id == msg_id:
            guild = client.get_guild(payload.guild_id)

            for category in guild.categories:
                if category.id == category_id:
                    break

            channel = guild.get_channel(channel_id)

            ticket_channel = await category.create_text_channel(f"ticket-{payload.member.display_name}",
                                                                topic=f"Ein Ticket für {payload.member.display_name}.",
                                                                permission_synced=True)

            await ticket_channel.set_permissions(payload.member, read_messages=True, send_messages=True,
                                                 read_message_history=True)

            message = await channel.fetch_message(msg_id)
            await message.remove_reaction(payload.emoji, payload.member)

            await ticket_channel.send(
                f"{payload.member.mention} Danke fürs erstellen eines Tickets! Benutze **MK!close** um das Ticket zu "
                f"schließen.")

            try:
                await client.wait_for("message", check=lambda
                    m: m.channel == ticket_channel and m.author == payload.member and m.content == "MK!close",
                                      timeout=3600)

            except asyncio.TimeoutError:
                await ticket_channel.delete()

            else:
                await ticket_channel.delete()


@client.command()
@commands.has_permissions(administrator=True)
async def config_ticket(ctx, msg: discord.Message = None, category: discord.CategoryChannel = None):
    if msg is None or category is None:
        await ctx.channel.send("Fehler beim Konfigurieren des Tickets das Argument wurde nicht angegeben oder war "
                               "ungültig.")
        return

    client.ticket_configs[ctx.guild.id] = [msg.id, msg.channel.id, category.id]

    async with aiofiles.open("ticket_configs.txt", mode="r") as file:
        data = await file.readlines()

    async with aiofiles.open("ticket_configs.txt", mode="w") as file:
        await file.write(f"{ctx.guild.id} {msg.id} {msg.channel.id} {category.id}\n")

        for line in data:
            if int(line.split(" ")[0]) != ctx.guild.id:
                await file.write(line)

    await msg.add_reaction(u"\U0001F3AB")
    await ctx.channel.send("Das Ticketsystem wurde erfolgreich konfiguriert.")


###########################################################

player1 = ""
player2 = ""
turn = ""
gameOver = True

board = []

winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
]


@client.command()
async def tictactoe(ctx, p1: discord.Member, p2: discord.Member):
    global count
    global player1
    global player2
    global turn
    global gameOver

    if gameOver:
        global board
        board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        turn = ""
        gameOver = False
        count = 0

        player1 = p1
        player2 = p2

        line = ""
        for x in range(len(board)):
            if x == 2 or x == 5 or x == 8:
                line += " " + board[x]
                await ctx.send(line)
                line = ""
            else:
                line += " " + board[x]

        num = random.randint(1, 2)
        if num == 1:
            turn = player1
            await ctx.send("<@" + str(player1.id) + "> ist gerade dran.")
        elif num == 2:
            turn = player2
            await ctx.send("<@" + str(player2.id) + "> ist gerade dran.")
    else:
        await ctx.send("Ein Spiel ist bereits im Gange! <:ich_beobachte_dich:826490014232739841> "
                       "Beende es, bevor du ein neues startest.")


@client.command()
async def place(ctx, pos: int):
    global turn
    global player1
    global player2
    global board
    global count
    global gameOver

    if not gameOver:
        mark = ""
        if turn == ctx.author:
            if turn == player1:
                mark = ":regional_indicator_x:"
            elif turn == player2:
                mark = ":o2:"
            if 0 < pos < 10 and board[pos - 1] == ":white_large_square:":
                board[pos - 1] = mark
                count += 1

                line = ""
                for x in range(len(board)):
                    if x == 2 or x == 5 or x == 8:
                        line += " " + board[x]
                        await ctx.send(line)
                        line = ""
                    else:
                        line += " " + board[x]

                checkWinner(winningConditions, mark)
                print(count)
                if gameOver is True:
                    await ctx.send(mark + " hat gewonnen! <a:slot:826874092649054264> <a:slot:826874092649054264> "
                                          "<a:slot:826874092649054264>")
                elif count >= 9:
                    gameOver = True
                    await ctx.send("UNENTSCHIEDEN!!! :scream: WAS EIN MATCH <a:blob_schnell:831427448050679828>")

                if turn == player1:
                    turn = player2
                elif turn == player2:
                    turn = player1
            else:
                await ctx.send("Stell sicher, dass du eine Ganze Zahl zwischen 1 und 9 (einschließlich) ein nicht "
                               "markiertes Feld auswählst. :1234:")
        else:
            await ctx.send("Es ist nicht dein Zug! <:ich_beobachte_dich:826490014232739841>")
    else:
        await ctx.send("Bitte starte mit dem **MK!tictactoe** Command ein neues Spiel. "
                       "<a:blob_aufgeregt:801390684497903617>")


def checkWinner(winningConditions, mark):
    global gameOver
    for condition in winningConditions:
        if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
            gameOver = True


@tictactoe.error
async def tictactoe_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Bitte erwähne 2 Spieler für diesen Command. <a:among_dance:801390220854820874>")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Bitte stell sicher, dass du den Spieler erwähnst/pingst (z.B. <@!731080543503908895>). :eyes:")


@place.error
async def place_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Bitte gib eine Position ein, die du markieren möchtest. :regional_indicator_x:")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Bitte gib einen Integer ein. :1234:")


###########################################################

@client.event
async def on_ready():
    for guild in client.guilds:
        client.warnings[guild.id] = {}

        async with aiofiles.open(f"{guild.id}.txt", mode="a"):
            pass

        async with aiofiles.open(f"{guild.id}.txt", mode="r") as file:
            lines = await file.readlines()

            for line in lines:
                data = line.split(" ")
                member_id = int(data[0])
                admin_id = int(data[1])
                reason = " ".join(data[2:]).strip("\n")

                try:
                    client.warnings[guild.id][member_id][0] += 1
                    client.warnings[guild.id][member_id][1].append((admin_id, reason))

                except KeyError:
                    client.warnings[guild.id][member_id] = [1, [(admin_id, reason)]]


@client.event
async def on_guild_join(guild):
    client.warnings[guild.id] = {}


@client.command()
@commands.has_permissions(administrator=True)
async def warn(ctx, member: discord.Member = None, *, reason=None):
    if member.id in [ctx.author.id]:
        return await ctx.send("Du kannst dich nicht selbst warnen 🙅")

    if member is None:
        return await ctx.send("Der angegebene Nutzer exisiert entweder nicht oder du hast vergessen einen anzugeben.")

    if reason is None:
        return await ctx.send("Bitte füge einen Grund hinzu.")

    try:
        first_warning = False
        client.warnings[ctx.guild.id][member.id][0] += 1
        client.warnings[ctx.guild.id][member.id][1].append((ctx.author.id, reason))

    except KeyError:
        first_warning = True
        client.warnings[ctx.guild.id][member.id] = [1, [(ctx.author.id, reason)]]

    count = client.warnings[ctx.guild.id][member.id][0]

    async with aiofiles.open(f"{ctx.guild.id}.txt", mode="a") as file:
        await file.write(f"{member.id} {ctx.author.id} {reason}\n")

    await ctx.send(f"{member.mention} hat {count} {'Verwarung' if first_warning else 'Verwarnungen'}.")


@client.command()
@commands.has_permissions(administrator=True)
async def warnings(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send("Der angegebene Nutzer exisiert entweder nicht oder du hast vergessen einen anzugeben.")

    embed = discord.Embed(title=f"Alle Verwarnungen von {member.name}", description="", colour=discord.Colour.red())
    try:
        i = 1
        for admin_id, reason in client.warnings[ctx.guild.id][member.id][1]:
            admin = ctx.guild.get_member(admin_id)
            embed.description += f"**Warnung {i}** wurde von: {admin.mention} vergeben. Der Grund ist: *'{reason}'*.\n"
            i += 1

        await ctx.send(embed=embed)

    except KeyError:
        await ctx.send("Diese Nutzer hat keine Verwarnungen")


###########################################################

@client.command(name='userinfo')
async def userinfo(ctx, member: discord.Member):
    de = pytz.timezone('Europe/Berlin')
    embed = discord.Embed(title=f'> Userinfo für {member.display_name}',
                          description='', color=0x4cd137, timestamp=datetime.now().astimezone(tz=de))

    embed.add_field(name='Name', value=f'```{member.name}#{member.discriminator}```', inline=True)
    embed.add_field(name='Bot', value=f'```{("Ja" if member.bot else "Nein")}```', inline=True)
    embed.add_field(name='Nickname', value=f'```{(member.nick if member.nick else "Nicht gesetzt")}```', inline=True)
    embed.add_field(name='Server beigetreten', value=f'```{member.joined_at}```', inline=True)
    embed.add_field(name='Discord beigetreten', value=f'```{member.created_at}```', inline=True)
    embed.add_field(name='Rollen', value=f'```{len(member.roles)}```', inline=True)
    embed.add_field(name='Höchste Rolle', value=f'```{member.top_role.name}```', inline=True)
    embed.add_field(name='Farbe', value=f'```{member.color}```', inline=True)
    embed.add_field(name='Booster', value=f'```{("Ja" if member.premium_since else "Nein")}```', inline=True)
    embed.set_footer(text=f'Angefordert von {ctx.author.name} • {ctx.author.id}', icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


###########################################################

@client.command()
async def prefix(ctx):
    await ctx.send("Mein Prefix ist: `MK!`\n"
                   "Du kannst `MK!help_me` machen um Hilfe zu bekommen.")


###########################################################

@client.command()
async def ping(ctx):
    msg = await ctx.channel.send(f"Pong! {client.latency * 1000:,.0f}ms  🏓")

    await msg.add_reaction("🏓")


###########################################################

if os.path.isfile("channels.json"):
    with open('channels.json', encoding='utf-8') as f:
        channels = json.load(f)
else:
    channels = {}
    with open('channels.json', 'w') as f:
        json.dump(channels, f, indent=4)

botcolor = 0x5865F2

client.remove_command("help")

tempchannels = []
admins = [731080543503908895, 764760823360913418]


@client.command(pass_context=True)
async def addtempchannel(ctx, channelid):
    if ctx.author.bot:
        return
    if ctx.author.guild_permissions.administrator:
        if channelid:
            for vc in ctx.guild.voice_channels:
                if vc.id == int(channelid):
                    if str(ctx.channel.guild.id) not in channels:
                        channels[str(ctx.channel.guild.id)] = []
                    channels[str(ctx.channel.guild.id)].append(int(channelid))
                    with open('channels.json', 'w') as f:
                        json.dump(channels, f, indent=4)
                    await ctx.send(f"{vc.name} ist nun ein JoinHub.")
                    return
            await ctx.send(f"{channelid} ist kein Voicechannel 🤦")
        else:
            await ctx.send("Bitte gib eine Channel ID an 🔢")
    else:
        await ctx.send("Du brauchst Administrator Rechte um das zu tun <:admin:836869634555641866> 🙅")


@client.command(pass_context=True)
async def removetempchannel(ctx, channelid):
    if ctx.author.bot:
        return
    if ctx.author.guild_permissions.administrator:
        if channelid:
            guildS = str(ctx.channel.guild.id)
            channelidI = int(channelid)
            for vc in ctx.guild.voice_channels:
                if vc.id == int(channelid):
                    if channels[guildS]:
                        if channelidI in channels[guildS]:
                            channels[guildS].remove(channelidI)
                            with open('channels.json', 'w') as f:
                                json.dump(channels, f, indent=4)
                                await ctx.send(f"{vc.name} ist kein JoinHub mehr.")
                                return
                        else:
                            await ctx.send("Dieser Channel existiert hier nicht 🤦")
                            return
            await ctx.send("Du besitzt noch keine JoinHubs 🙅")
        else:
            await ctx.send("Keine Channelid angegeben 🔢")
    else:
        await ctx.send("Du brauchst Administrator Rechte um das zu tun <:admin:836869634555641866> 🙅")


@client.command(pass_context=True)
async def info(ctx):
    if ctx.author.bot:
        return
    if ctx.author.id in admins:
        membercount = 0
        guildcount = 0
        for guild in client.guilds:
            membercount += guild.member_count
            guildcount += 1
        embed = discord.Embed(title='Informationen', description=f'Der Bot ist derzeit auf {guildcount - 1} anderen '
                                                                 f'Servern mit {membercount} Mitglieder.',
                              color=0x7289DA)
        await ctx.channel.send(embed=embed)


@client.event
async def on_voice_state_update(member, before, after):
    if before.channel:
        if isTempChannel(before.channel):
            bchan = before.channel
            if len(bchan.members) == 0:
                await bchan.delete(reason="Keine Mitglieder mehr im Sprachkanal")
    if after.channel:
        if isJoinHub(after.channel):
            name = f"🏡 | {member.name}`s Raum"
            output = await after.channel.clone(name=name, reason=f"{member.name} ist dem Join Hub gejoint")
            if output:
                tempchannels.append(output.id)
                await output.set_permissions(member)
                await member.move_to(output, reason="Ein Temporärer Sprachkanal wurde erstellt")


async def getChannel(guild, name):
    for channel in guild.voice_channels:
        if name in channel.name:
            return channel
    return None


def isJoinHub(channel):
    if channels[str(channel.guild.id)]:
        if channel.id in channels[str(channel.guild.id)]:
            return True
    return False


def isTempChannel(channel):
    if channel.id in tempchannels:
        return True
    else:
        return False


###########################################################

client.run("ODEyMzM1MDEyNzI4NDA2MDQ2.YC_P7w.nT9CO_Nt5jcZz5wblVicWOOSf_w")
