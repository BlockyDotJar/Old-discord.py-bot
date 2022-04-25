import random

import discord
from discord.ext import commands
import json

client = commands.Bot(command_prefix=commands.when_mentioned_or('PREFIX'), help_command=None,
                      intents=discord.Intents.all())

mainshop = [{"Name": "Schokolade", "Preis": 10, "Beschreibung": "Essen"},
            {"Name": "Taschenuhr", "Preis": 100, "Beschreibung": "Zeit"},
            {"Name": "Tomatensoße", "Preis": 250, "Beschreibung": "Soße"},
            {"Name": "Handy", "Preis": 500, "Beschreibung": "Kommunikation"},
            {"Name": "Laptop", "Preis": 1000, "Beschreibung": "Arbeit"},
            {"Name": "PC", "Preis": 10000, "Beschreibung": "Gaming"},
            {"Name": "Privatjet", "Preis": 100000, "Beschreibung": "Mobilität"},
            {"Name": "Diamant", "Preis": 1000000, "Beschreibung": "Schmuck"},
            {"Name": "Villa", "Preis": 10000000, "Beschreibung": "Wohnen"}]


@client.event
async def on_ready():
    print("Economy System bereit zum Start")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = "**Du hast gerade einen cooldown!**, du kannst diesen Command in `{:.2f}` " \
              "Sekunden wieder nutzen! 🕐".format(error.retry_after)
        await ctx.send(msg)


@client.command(aliases=["bal"])
async def balance(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["Bank"]

    embed = discord.Embed(title=f"{ctx.author.name}`s Kontostand 💸", color=0x00ffe5)
    embed.add_field(name="Brieftasche 👛", value=wallet_amt)
    embed.add_field(name="Bank 🏦", value=bank_amt)
    await ctx.send(embed=embed)


@client.command()
@commands.cooldown(5, 60, commands.BucketType.user)
async def beg(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()

    user = ctx.author

    earnings = random.randrange(101)

    await ctx.send(f"Jemand hat dir {earnings} :coin:`s gegeben!!! 😱")

    users[str(user.id)]["wallet"] += earnings

    with open("mainbank.json", "w") as f:
        json.dump(users, f)


@client.command(aliases=["ci", "collect"])
@commands.cooldown(1, 3600, commands.BucketType.user)
async def collectincome(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()

    user = ctx.author

    earnings = random.randrange(1000)

    embed = discord.Embed(title=f"{ctx.author.name}", color=0x325ea8,
                          description="<:check"":839098117613813771> Erfolgreich eingesammelt "
                                      "<a:coin_animated:839121965499023390>\n")
    embed.add_field(name="Einkommen", value=f"Dein Einkommen beträgt: {earnings} :coin:`s !")
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

    embed = discord.Embed(title=f"Dein täglicher Lohn {ctx.author.name}!", color=0x325ea8,
                          description="<a:verified_blue:815667711774031922> "
                                      "Tägliche Belohnung Erfolgreich "
                                      "eingesammelt "
                                      "<a:coin_animated:839121965499023390>"
                                      "\n")
    embed.add_field(name="Tägliche Belohnung:", value=f"Deine Täglich Belohnung beträgt: {earnings} :coin:`s !")
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

    await ctx.send(f"Du hast {amount} :coin:`s von deinem Bank Konto abgehoben 🏦 💵")


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

    await ctx.send(f"Du hast {amount} :coin:`s deponiert 🏦 💵")


@client.command()
async def send(ctx, member: discord.Member, amount=None):
    await open_account(ctx.author)
    await open_account(member)

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
    await update_bank(member, amount, "Bank")

    await ctx.send(f"Du hast {amount} :coin:`s vergeben <a:moneyyyy:837654704556605450>")


@client.command()
@commands.cooldown(1, 300, commands.BucketType.user)
async def rob(ctx, member: discord.Member):
    await open_account(ctx.author)
    await open_account(member)

    bal = await update_bank(member)

    if bal[0] < 100:
        await ctx.send("Dir bringt es nichts einen User der unter 100 Coins hat auszurauben!  🙅‍♂")
        return

    earnings = random.randrange(0, bal[0])

    await update_bank(ctx.author, earnings)
    await update_bank(member, -1 * earnings)

    await ctx.send(f"Du hast jemanden ausgeraubt und hast {earnings} :coin:`s gestohlen! "
                   f"<a:blob_schnell:831427448050679828>")


@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
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
    embed = discord.Embed(title="Shop", color=0xffc800)

    for item in mainshop:
        name = item["Name"]
        price = item["Preis"]
        desc = item["Beschreibung"]
        embed.add_field(name=name, value=f"{price}€ | {desc}")

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
            await ctx.send(f"Du hast nicht genug Geld in deiner Brieftasche um {amount} {item} zu kaufen 🙅‍♂ 💵")
            return

    await ctx.send(f"Du hast gerade {amount} {item} gekauft <a:tada_animated:815667511629840454>")


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

    em = discord.Embed(title=f"Top {x} Reichste Personen", description="Dies ist ein Leaderboard wo die reichsten "
                                                                       "Leute die das Economy System je benutzt haben"
                                                                       " angezeigt werden "
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
            await ctx.send(f"Du hast nicht {item} {amount} in deiner Tasche 🙅‍♂")
            return
        if res[1] == 3:
            await ctx.send(f"Du hast {item} nicht in deiner Tasche 🙅‍♂")
            return

    await ctx.send(f"Du hast gerade {item} {amount} verkauft 💵")


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


client.run("BOT_TOKEN")
