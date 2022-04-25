import discord
from discord.ext import commands
import asyncio
import random

client = commands.Bot(command_prefix="MK!")


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
@commands.has_role("Giveaway Leitung")
async def gstart(ctx):
    await ctx.send("Beginnen wir mit diesem Giveaway! Beantworte diese Fragen innerhalb von 15 Sekunden! :alarm_clock:")

    questions = ["In welchem Kanal soll das Giveaway stattfinden ?  🏴",
                 "Wie lange sollte das Giveaway gehen ? <:thonk:750400537588924417> (s|m|h|d)",
                 "Was soll der Preis sein ? :coin:"]

    answers = []

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    for i in questions:
        await ctx.send(i)

        try:
            msg = await client.wait_for('message', timeout=15.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send('Du hast nicht zeitgemäß geantwortet<a:blob_schnell:831427448050679828> Versuch es nochmal!')
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
        await ctx.send(f"Die Zeit muss einen integer enthalten. Bitte benutze das nächste mal einen!")
        return

    prize = answers[2]

    await ctx.send(f"Das giveaway findet in {channel.mention} statt und wird {answers[1]} lang gehen! "
                   f"<a:acongablob:815668257633599489>")

    embed = discord.Embed(title="Giveaway!", description=f"Es gibt `{prize}` zu gewinnen!", color=ctx.author.color)

    embed.add_field(name="Veranstaltet von:", value=ctx.author.mention)

    embed.set_footer(text=f"Endet in {answers[1]} ab jetzt!")

    my_msg = await channel.send(embed=embed)

    await my_msg.add_reaction("🎉")

    await asyncio.sleep(time)

    new_msg = await channel.fetch_message(my_msg.id)

    users = await new_msg.reactions[0].users().flatten()
    users.pop(users.index(client.user))

    winner = random.choice(users)

    await channel.send(f"<a:blob_aufgeregt:801390684497903617> Gratulation {winner.mention} du hast "
                       f"<a:ArrowRightGlow:815668040771436555> `{prize}` gewonnen! <a:among_dance:801390220854820874>")

    await my_msg.add_reaction("🥳")

    await my_msg.add_reaction("🎁")

    await my_msg.add_reaction("🥂")


@client.command()
@commands.has_role("Giveaway Leitung")
async def greroll(ctx, channel: discord.TextChannel, id_: int):
    try:
        new_msg = await channel.fetch_message(id_)
    except:
        await ctx.send("Die ID wurde falsch eingegeben. 🙅‍♂")
        return

    users = await new_msg.reactions[0].users().flatten()
    users.pop(users.index(client.user))

    winner = random.choice(users)

    await channel.send(f"<a:blob_aufgeregt:801390684497903617> Gratulation! Der neue Gewinner ist: "
                       f"<a:ArrowRightGlow:815668040771436555> {winner} <a:among_dance:801390220854820874>")


client.run("ODEyMzM1MDEyNzI4NDA2MDQ2.YC_P7w.nT9CO_Nt5jcZz5wblVicWOOSf_w")
