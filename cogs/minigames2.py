import discord
from discord.ext import commands
import random

player1 = ""
player2 = ""
turn = ""
gameOver = True
p1=None
p2=None

#incase a game started while a game is running

board = []

"""
this is how the gaming board looks like

              [  0  ][  1  ][  2  ]
              [  3  ][  4  ][  5  ]
              [  6  ][  7  ][  8  ]
                                      p.s. the numbers are for programing but not in game

"""

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

class Minigames2(commands.Cog, name='Minigames2'):

    def __init__(self, client: commands.Bot) -> None:
        super().__init__()
        self.client = client
    
    @commands.hybrid_command(name="tictactoe", description="start playing tictactoe")
    async def tictactoe(self, ctx, p1:discord.Member, p2:discord.Member):
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
                    #the board is printed with emojis
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
                    await ctx.send(line)#change line's for tictactoe's format
                    line = ""
                else:
                    line += " " + board[x]

            # randomly determine who goes first
            num = random.randint(1, 2)
            if num == 1:
                turn = player1
                await ctx.send(f"It is {player1.mention}'s turn.")
            elif num == 2:
                turn = player2
                await ctx.send(f"It is {player2.mention}'s turn.")
        else: # avoinding the situation that two games happen at the same time
            await ctx.send("A game is already in progress! Finish it before starting a new one.")

    @commands.hybrid_command(name="place", description="place an 'x' or a 'o' on the gaming board")
    async def place(self, ctx, pos: int):
        global turn
        global player1
        global player2
        global board
        global count
        global gameOver

        """ 
        position in game:

            [  1  ][  2  ][  3  ]
            [  4  ][  5  ][  6  ]
            [  7  ][  8  ][  9  ]    

        """
        if gameOver:
            await ctx.send("Please start a new game using the $tictactoe command.")
            return

        if turn != ctx.message.author:
            await ctx.send("It is not your turn.")
            return

        if not (0 < pos < 10 and board[pos - 1] == ":white_large_square:"):
            await ctx.send("Be sure to choose an integer between 1 and 9 (inclusive) and an unmarked tile.")
            return

        mark = ":regional_indicator_x:" if turn == player1 else ":o2:"
        board[pos - 1] = mark
        count += 1

        # print the board
        line = ""
        for x in range(len(board)):
            if x == 2 or x == 5 or x == 8: # x % 3 == 2
                line += " " + board[x]
                await ctx.send(line)
                line = ""
            else:
                line += " " + board[x]

        checkWinner(winningConditions, mark)
        print(count)
        if gameOver:
            await ctx.send(mark + " wins!")
        elif count >= 9:
            gameOver = True
            await ctx.send("It's a tie!")

        # switch turns
        if turn == player1:
            turn = player2
        elif turn == player2:
            turn = player1

def checkWinner(winningConditions, mark):
    print('checking')
    global gameOver
    for condition in winningConditions:
        if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
            gameOver = True


async def tictactoe_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please mention 2 players for this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to mention/ping players.")

async def place_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter a position you would like to mark.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to enter an integer.")

async def setup(client: commands.Bot) -> None:
    """
    Loads the cog Minigames into the bot.

    This is automatically called by commands.Bot.load_extension() and **is not meant to be called directly**.

    Args:
        client (commands.Bot): The bot to load the cog into.
    """
    await client.add_cog(Minigames2(client))

#you may start a game by using the command $tictactoe @someone @someone
#using the command !place 1-9 to place a cross or a circle
#only one game can be running at the same time
