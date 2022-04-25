import asyncio

import aiofiles
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="MK!")
bot.ticket_configs = {}


@bot.event
async def on_ready():
    async with aiofiles.open("ticket_configs.txt", mode="a") as temp:
        pass

    async with aiofiles.open("ticket_configs.txt", mode="r") as file:
        lines = await file.readlines()
        for line in lines:
            data = line.split(" ")
            bot.ticket_configs[int(data[0])] = [int(data[1]), int(data[2]), int(data[3])]

    print(f"{bot.user.name} ist Bereit zum Ticket erstellen.")


@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.id != bot.user.id and str(payload.emoji) == u"\U0001F3AB":
        msg_id, channel_id, category_id = bot.ticket_configs[payload.guild_id]

        if payload.message_id == msg_id:
            guild = bot.get_guild(payload.guild_id)

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
                await bot.wait_for("message", check=lambda
                    m: m.channel == ticket_channel and m.author == payload.member and m.content == "MK!close",
                                   timeout=3600)

            except asyncio.TimeoutError:
                await ticket_channel.delete()

            else:
                await ticket_channel.delete()


@bot.command()
@commands.has_role("Admin")
async def config_ticket(ctx, msg: discord.Message = None, category: discord.CategoryChannel = None):
    if msg is None or category is None:
        await ctx.channel.send("Fehler beim Konfigurieren des Tickets das Argument wurde nicht angegeben oder war "
                               "ungültig.")
        return

    bot.ticket_configs[ctx.guild.id] = [msg.id, msg.channel.id, category.id]  # this resets the configuration

    async with aiofiles.open("ticket_configs.txt", mode="r") as file:
        data = await file.readlines()

    async with aiofiles.open("ticket_configs.txt", mode="w") as file:
        await file.write(f"{ctx.guild.id} {msg.id} {msg.channel.id} {category.id}\n")

        for line in data:
            if int(line.split(" ")[0]) != ctx.guild.id:
                await file.write(line)

    await msg.add_reaction(u"\U0001F3AB")
    await ctx.channel.send("Das Ticketsystem wurde erfolgreich konfiguriert.")


bot.run("ODEyMzM1MDEyNzI4NDA2MDQ2.YC_P7w.nT9CO_Nt5jcZz5wblVicWOOSf_w")
