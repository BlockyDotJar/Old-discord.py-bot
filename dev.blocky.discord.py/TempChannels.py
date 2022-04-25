import asyncio
import discord
from discord.ext import commands
import os
import json

if os.path.isfile("channels.json"):
    with open('channels.json', encoding='utf-8') as f:
        channels = json.load(f)
else:
    channels = {}
    with open('channels.json', 'w') as f:
        json.dump(channels, f, indent=4)

bot = commands.Bot(command_prefix="t!")
botcolor = 0x5865F2

bot.remove_command("help")

# ---------------------------------------------------------------------


tempchannels = []
admins = [731080543503908895, 764760823360913418]


# ---------------------------------------------------------------------

@bot.command(pass_context=True)
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
                    await ctx.send("{} ist nun ein JoinHub.".format(vc.name))
                    return
            await ctx.send("{} ist kein Voicechannel 🤦".format(channelid))
        else:
            await ctx.send("Bitte gib eine Channel ID an 🔢")
    else:
        await ctx.send("Du brauchst Administrator Rechte um das zu tun <:admin:836869634555641866> 🙅")


@bot.command(pass_context=True)
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
                                await ctx.send("{} ist kein JoinHub mehr.".format(vc.name))
                                return
                        else:
                            await ctx.send("Dieser Channel existiert hier nicht 🤦")
                            return
            await ctx.send("Du besitzt noch keine JoinHubs 🙅")
        else:
            await ctx.send("Keine Channelid angegeben 🔢")
    else:
        await ctx.send("Du brauchst Administrator Rechte um das zu tun <:admin:836869634555641866> 🙅")


@bot.command(pass_context=True)
async def info(ctx):
    if ctx.author.bot:
        return
    if ctx.author.id in admins:
        membercount = 0
        guildcount = 0
        for guild in bot.guilds:
            membercount += guild.member_count
            guildcount += 1
        embed = discord.Embed(title='Informationen', description=f'Der Bot ist derzeit auf {guildcount - 1} anderen '
                                                                 f'Servern mit {membercount} Members.',
                              color=0xfefefe)
        await ctx.channel.send(embed=embed)


@bot.command(pass_context=True)
async def help(ctx):
    if ctx.author.bot:
        return
    embed = discord.Embed(title='Befehle für die Tempchannel', description=f'.addtempchannel <channelid> - '
                                                                           f'Fügt den Channel als Tempchannel hinzu.\n'
                                                                           f'.removetempchannel <channelid> - '
                                                                           f'Entfernt den Tempchannel.',
                          color=0xfefefe)
    if ctx.author.id in admins:
        embed.add_field(name='Adminbefehle', value='.info - Zeigt allgemeine Statistiken.', inline=False)
    await ctx.channel.send(embed=embed)


# ---------------------------------------------------------------------

@bot.event
async def on_ready():
    print('--------------------------------------')
    print('Bot is ready.')
    print('Eingeloggt als')
    print(bot.user.name)
    print(bot.user.id)
    print('--------------------------------------')
    bot.loop.create_task(status_task())


async def status_task():
    while True:
        await bot.change_presence(activity=discord.Game('Discord » discord.gg/mqwc7wNk'), status=discord.Status.online)
        await asyncio.sleep(10)
        await bot.change_presence(activity=discord.Game('Hilfe » t!help'),
                                  status=discord.Status.online)
        await asyncio.sleep(10)


@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel:
        if isTempChannel(before.channel):
            bchan = before.channel
            if len(bchan.members) == 0:
                await bchan.delete(reason="No member in tempchannel")
    if after.channel:
        if isJoinHub(after.channel):
            overwrite = discord.PermissionOverwrite()
            overwrite.manage_channels = True
            overwrite.move_members = True
            name = "│⏳ {}".format(member.name)
            output = await after.channel.clone(name=name, reason="Joined in joinhub")
            if output:
                tempchannels.append(output.id)
                await output.set_permissions(member, overwrite=overwrite)
                await member.move_to(output, reason="Created tempvoice")


# ---------------------------------------------------------------------

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


# ---------------------------------------------------------------------

bot.run("BOT_TOKEN")
