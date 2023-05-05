import discord
import asyncio
import re
import os
import pathlib

from redbot.core import commands


class madlib(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print('Mad Lib Cog Loaded')
        self.final_text = tuple()


    @commands.group(invoke_without_command=True, require_var_positional=True)
    async def madlib(self, ctx):

        names_list = dump_dir()
        page_list = []
        index = 1
        
        while (len(names_list) != 0):

            text = f"{index}. {names_list[0]['title']}"
            names_list.pop(0)
            index += 1

            for i in range(0, 10):
                if(len(names_list) == 0):
                    break
                text += f"\n{index}. {names_list[0]['title']}"
                names_list.pop(0)
                index += 1

            page_list.append(discord.Embed(title="Madlib menu", description=text, colour=discord.Colour.orange()))

        self.bot.help_pages = page_list
        current = 0
        msg = await ctx.send(embed=self.bot.help_pages[current])
        buttons = [u"\u23EA", u"\u2B05", u"\u27A1", u"\u23E9"] # skip to start, left, right, skip to end

        for button in buttons:
            await msg.add_reaction(button)      

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=60.0)

            except asyncio.TimeoutError:
                return print("test")

            else:
                previous_page = current
                if reaction.emoji == u"\u23EA":
                    current = 0
                    
                elif reaction.emoji == u"\u2B05":
                    if current > 0:
                        current -= 1
                        
                elif reaction.emoji == u"\u27A1":
                    if current < len(self.bot.help_pages)-1:
                        current += 1

                elif reaction.emoji == u"\u23E9":
                    current = len(self.bot.help_pages)-1


                for button in buttons:
                    await msg.remove_reaction(button, ctx.author)

                if current != previous_page:
                    await msg.edit(embed=self.bot.help_pages[current])

            pass
    
 
    @madlib.command(name = "prompt")
    async def use_prompt(self, ctx, *args):

        try:
            prompt_list = dump_dir()

            file = open(prompt_list[int(args[0]) - 1]['src'], 'r')
            buffer = file.read()
            buffer = buffer.split(']', 1)
            buffer = buffer[1]
            user_keys = re.findall('\[(.*?)\]', buffer)
            revert_string = re.sub('\[(.*?)\]', '{}', buffer)
            prompt = "#"
            i = 0

            while i < (len(user_keys) - 1):
                prompt += user_keys[i] + ", "
                i += 1

            prompt += user_keys[-1]

            await ctx.send("To play, copy/paste all of the text below, replace ONLY the words, then hit enter")
            await ctx.send(prompt)

            main_task = asyncio.create_task(self.get_user_input(ctx, prompt, revert_string))
            #timer_task = asyncio.create_task(self.timer(ctx, main_task))

            await asyncio.gather(main_task)

            print('?')

            await ctx.send(revert_string.format(*self.final_text))
        except:
            await ctx.send("There's been an error or user input is mangled.")

    @madlib.command(name = "new")
    async def new_prompt(self, ctx, *, args):

        try:
            user_text = re.findall('\[(.*?)\]', args)
            grab_title = user_text[0].replace(' ', '_')
            prompt_path = pathlib.Path(pathlib.Path(__file__).resolve())
            prompt_path = prompt_path.parent / 'prompts' / f"{grab_title}.txt"

            pathlib.Path(prompt_path).write_text(args)

            #new_file.write(args)



            await ctx.send(f"New user prompt saved: {user_text[0]}")
        except:
            await ctx.send("There's been an error or user input is mangled.")


    @madlib.command(name = "delete")
    async def delete_prompt(self, ctx, *args):
        try:
            protected_files = pathlib.Path(pathlib.Path(__file__).resolve())
            protected_files = protected_files.parent / "protected.txt"

            #protected_files = open(pathlib.Path("madlib/protected.txt"), "r")
            #protected_titles = protected_files.read()

            protected_titles = pathlib.Path(protected_files).read_text()

            protected_titles = re.findall('\[(.*?)\]', protected_titles)
            all_titles = dump_dir()
            del_choice = all_titles[int(args[0]) - 1]['title']
            for i in protected_titles:
                if(del_choice == i):
                    
                    print(len(del_choice))
                    print(len(i))
                    await ctx.send("This file is protected. Cannot delete.")
                    return
            delete_file = f"{all_titles[int(args[0]) - 1]['src']}"
            if os.path.exists(delete_file):
                os.remove(delete_file)
                await ctx.send("Prompt and file removed.")
            else:
                await ctx.send("File could not be found.")
        except:
            await ctx.send("There's been an error or user input is mangled.")

    async def get_user_input(self, ctx, prompt, text):
        try:
            while True:
                msg = await ctx.bot.wait_for('message', check= None, timeout= 240.0)

                final_text = await self.check_msg(ctx, msg)

                if final_text != None:
                    self.final_text = final_text
                    break

        except:
            pass


    async def timer(self, ctx, sister_task):
        secondint = int(60)
        message = await ctx.send(f"Timer: {secondint}")

        while secondint > -1:

            await message.edit(content=f"Timer: {secondint}")
            await asyncio.sleep(1)
            secondint -= 1
        
        await message.edit(content="Timer: finished!")
        sister_task.cancel()


    async def check_msg(self, ctx, msg):

        try:
            if(ctx.channel.id != msg.channel.id):
                return None
            if (msg.author == self.bot.user):
                return None
            if (msg.author != ctx.author):
                return None
        
            if msg.content[0] != '#':
                return None

            rtn_string = msg.content
            rtn_string = rtn_string.replace('#', '', 1)
            rtn_string = tuple(rtn_string.split(', '))

            return rtn_string


        except:
            pass
        pass



    async def create_menu():
        pass



# takes all files, makes list full of their data, sends it back
def dump_dir():

    prompt_path = pathlib.Path(pathlib.Path(__file__).resolve())
    prompt_path = str(prompt_path.parent / 'prompts')

    file_names = os.listdir(prompt_path)
    files = []

    for i in file_names:
        src = os.path.join(prompt_path, i)
        buffer = ''
        title = ''
        try:
            file = open(src, 'r')
            buffer = file.read()
            title = re.findall('\[(.*?)\]', buffer)
            file.close
        except:
            print ("bad file name")
        entry = {
            'title': title[0],
            'src': src,
            'text': ''
            }
        files.append(entry)

    return files