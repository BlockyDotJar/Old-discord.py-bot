import discord
from discord.ext import commands
import random

client = commands.Bot(command_prefix="MK!")

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

        # print the board
        line = ""
        for x in range(len(board)):
            if x == 2 or x == 5 or x == 8:
                line += " " + board[x]
                await ctx.send(line)
                line = ""
            else:
                line += " " + board[x]

        # determine who goes first
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

                # print the board
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

                # switch turns
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


client.run("ODEyMzM1MDEyNzI4NDA2MDQ2.YC_P7w.nT9CO_Nt5jcZz5wblVicWOOSf_w")
