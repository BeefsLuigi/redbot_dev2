import discord
import asyncio
import random

from redbot.core import bank, commands

class chohan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_list = []
        print('Cho-Han Cog Loaded')

    @commands.group(invoke_without_command=True, require_var_positional=True)
    async def chohan(self, ctx):
        await ctx.send("To play, type ?chohan go, then when the cup comes down, say (odd/even) (bet amount)")

    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @chohan.command(name='go')
    async def new_game(self, ctx, *args, member: discord.Member = None):
        self.user_list = []

        #file_path = self.database + '/' + str(ctx.guild.id) + '/' + 'economy.json'

        #data = file_manager.get_all(file_path)

        await ctx.send("(rolls dice around in a cup and slams it on the mat.) ODD OR EVEN!")

        gather_task = asyncio.create_task(self.gather_players(ctx))
        timer_task = asyncio.create_task(self.timer(ctx, gather_task))
        
        await asyncio.gather(gather_task, timer_task)

        if (len(self.user_list) > 0):
            dice_result = await self.roll_dice(ctx)

            await self.handle_winnings(ctx, dice_result)

        else:
            await ctx.send("No one?!")

        pass
   
    async def gather_players(self, ctx):

        try:
            while True:
                msg = await ctx.bot.wait_for('message', check= None, timeout= 20.0)

                l_player = await self.check_msg(ctx, msg)

                if l_player != None:
                    self.user_list.append(l_player)
                else:
                    pass
        except:
            if (len(self.user_list) == 0):
                print ("None valid users in list...")



    async def check_msg(self, ctx, msg):


        try:
            bet = 0

            if(ctx.channel != msg.channel):
                return None
            if (msg.author == self.bot.user):
                return None
            if self.user_list:
                for i in self.user_list:
                    if (msg.author.id == i["id"]):
                        return None

            msg_list = msg.content.split()
            odd_or_even = 0
            if(msg_list[0].lower() == 'odd'):
                odd_or_even = 1
            elif (msg_list[0].lower() == 'even'):
                odd_or_even = 0
            else:
                return None

            if(msg_list[1].isnumeric() == False):
                return None
            else:
                bet = int(msg_list[1])

            user_money = await bank.get_balance(msg.author)

            if (user_money == 0):
                await ctx.send(f"{msg.author.display_name} is a deadbeat trying to play without money! SCRAM!!!")
                return None

            result = {"id": msg.author, "nick": msg.author.display_name, "choice": odd_or_even, "bet": bet, "balance": user_money}        

            return result
        except:
            return None


    async def timer(self,ctx, sister_task):
        secondint = int(7)
        message = await ctx.send(f"Timer: {secondint}")

        while secondint > -1:

            await message.edit(content=f"Timer: {secondint}")
            await asyncio.sleep(1)
            secondint -= 1
        
        await message.edit(content="Timer: finished!")
        sister_task.cancel()

    async def roll_dice(self, ctx):
        dice1 = random.randint(1,6)
        dice2 = random.randint(1,6)

        result = (dice1 + dice2) % 2

        if (result == 0):
            await ctx.send(f"{dice1} and a {dice2}! EVEN!")
        else:
            await ctx.send(f"{dice1} and a {dice2}! ODD!")
        
        return result

    async def handle_winnings(self, ctx, dice_result):

        for k in self.user_list:

            user_money = await bank.get_balance(k["id"])

            # lose
            if(k["choice"] != dice_result):
                if(k["balance"] <= k["bet"]):
                    await ctx.send(f"{k['nick']} lost their shirt.")
                    await bank.set_balance(k["id"], 0)
                else:
                    await ctx.send(f"{k['nick']} lost ${k['bet']}")
                    k["balance"] -= k["bet"]
                    await bank.set_balance(k["id"], k["balance"])
                break
            # win
            if (k["choice"] == dice_result):
                if (k["balance"] <= k["bet"]):
                    await ctx.send(f"{k['nick']} wins ${k['balance']} back.")
                    k["balance"] += k["balance"]
                    await bank.set_balance(k["id"], k["balance"])

                else:
                    await ctx.send(f"{k['nick']} wins ${k['bet']}.")
                    k["balance"] += k["bet"]
                    await bank.set_balance(k["id"], k["balance"])
            break



