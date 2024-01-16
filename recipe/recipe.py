

import discord
import asyncio
import re
import os
import pathlib
import json

from redbot.core import commands


class Recipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        recipe_path = pathlib.Path(pathlib.Path(__file__).resolve())
        recipe_path = recipe_path.parent /"recipes.json"
        print('Recipe Cog Loaded')
        try: 
            if os.path.exists(recipe_path) == False:
                print("no file found, making a new one")
                init_text = {'entry_count': 0}
                file = open(recipe_path, 'x')
                json.dump(init_text, file, indent=1)
        except:
            print("Recipe file found...")
        self.textpath = recipe_path
        self.blank_entry = {'author': '', 'title': '', 'tags': [], 'body': ''}


    @commands.group()
    async def recipe(self, ctx):
        """Remember that you are responsible for formatting your recipes."""
     

    @recipe.group(name="new", autohelp=False)
    async def new_recipe(self, ctx, *, args):
        """Add recipe to collection.
        
        Recipes have to be longer than 40 characters long. The title is grabbed by the bot by using everything before the first return or the first forty characters. Remember that you are responsible for formatting your recipes. If it sucks. delete it and use the new command to reupload."""

        #open file and load buffer
        try:
            file = open(self.textpath, "r")
            buffer = json.loads(file.read())
            buffer['entry_count'] += 1
            file.close
        except:
            await ctx.send("There was an error in opening file. Check directory.")
            return
        
        try:
            if len(args) < 40:
                await  ctx.send("I don't think this is long enough to be here...")
                return
            linebreak_pos = args.find('\n')
            title = ''
            body = ''
            #grab title
            if linebreak_pos == -1 or linebreak_pos > 39:
                title = args[0:39]
                body = args[39: len(args) - 1]
            else:
                title = args[0:linebreak_pos]
                body = args[linebreak_pos: len(args) - 1]
            #make new entry
            new_entry = self.blank_entry
            new_entry['title'] = title
            new_entry['body'] = body
            new_entry['author'] = ctx.author.id
            buffer.update({buffer['entry_count']: {}})
            buffer[buffer['entry_count']].update(new_entry)
            #edit file for changes
            try:
                file = open(self.textpath, 'w')
                json.dump(buffer, file, indent=1)
                file.close()
                await ctx.send("Recipe was successfully added!")
                await ctx.send(":blessed:")
            except:
                await ctx.send("Error in updating recipe file...")
        except:
            await ctx.send("There's been an error or user input is mangled.")



    @recipe.group(name="open", autohelp=False)
    async def open_recipe(self, ctx, *, args):
        """Type in the index number after the open command."""
        #open file and load buffer
        try:
            file = open(self.textpath, "r")
            buffer = json.loads(file.read())
            file.close
        except:
            await ctx.send("There was an error in opening file. Check directory.")
            return
        try:
            output = buffer[args]
            user_obj = ctx.bot.get_user(output['author'])
            user_name = user_obj.display_name

            #add tag function later
            await ctx.send(f"Index: {args}\nAuthor: {user_name}\nTitle: {output['title']}{output['body']}")
        except:
            await ctx.send("Could not find entry for recipe.")

    @recipe.group(name="delete", autohelp=False)
    async def delete_recipe(self, ctx, *, args):
        """Type in the index number after the delete command.
         
           You can only delete the recipes that you create."""
        #open file and load buffer
        try:
            file = open(self.textpath, "r")
            buffer = json.loads(file.read())
            file.close
        except:
            await ctx.send("There was an error in opening file. Check directory.")
            return
        try:
            output = buffer[args[0]]
            user_obj = ctx.bot.get_user(output['author'])
        except:
            await ctx.send("Recipe could not be found.")
            return
        if user_obj == ctx.author:
            del buffer[args[0]]
        else:
            await ctx.send("You cannot delete someone else's recipe.")
            return
        try:
            file = open(self.textpath, 'w')
            json.dump(buffer, file, indent=1)
            file.close()
            await ctx.send("Your recipe has been deleted.")
        except:
            await ctx.send("Some error occurred saving changes to file.")
            return
        
    @recipe.group(name="all", autohelp=False)
    async def all_recipes(self, ctx):
        """Load all recipes into a menu."""

        #open file and load buffer
        try:
            file = open(self.textpath, "r")
            buffer = json.loads(file.read())
            file.close
        except:
            await ctx.send("There was an error in opening file. Check directory.")
            return
        
        del buffer['entry_count']


        await self.create_menu(ctx, buffer, "All recipes")

        
    @recipe.group(name="search", autohelp=False)
    async def search_recipe(self, ctx, *, args):
        """Enter a @user or key word to search
        
        If the search is successful, it will make a menu."""

        #open file and load buffer
        try:
            file = open(self.textpath, "r")
            buffer = json.loads(file.read())
            file.close
        except:
            await ctx.send("There was an error in opening file. Check directory.")
            return

        found_entries = None
        menu_title = ""

        #if searching for a user, check discord's id format
        if args[0] == '<':
            if args[1] == '@':
                if args[-1] == '>':
                    search_key = re.findall('[0-9]+', args)
                    found_entries = self.find_user(buffer, search_key[0])

                    if search_key[0] != '':
                        user = ctx.bot.get_user(int(search_key[0]))
                        menu_title = f"{user.display_name}'s recipes"
        else:   #if not a discord id, just look for the word
            found_entries = self.find_keyword(buffer, args)
            menu_title = f"Recipes containing {args}"

        if found_entries == {}:
            await ctx.send(f"Couldn't find any entries for that...")
            return

        await self.create_menu(ctx, found_entries, menu_title)
  

    def find_user(self, buffer, key):
        found = {}

        for entry in buffer:
            if entry != 'entry_count':
                if str(buffer[entry]['author']) == key:
                    found.update({entry: {}})
                    found[entry].update(buffer[entry])
        
        return found


    def find_keyword(self, buffer, key):
        found = {}

        for entry in buffer:
            if entry != 'entry_count':
                #find_in_title = buffer[entry]['title'].find(key)
                #find_in_body = buffer[entry]['body'].find(key)

                find_in_title = re.search(key, buffer[entry]['title'], re.IGNORECASE)
                find_in_body = re.search(key, buffer[entry]['body'], re.IGNORECASE)

                if find_in_body != None or find_in_title != None:
                    found.update({entry: {}})
                    found[entry].update(buffer[entry])

        return found


    async def create_menu(self, ctx, buffer, menu_title):
        try:
            text = ""
            counter = 0
            page_list = []
            for entry in buffer:
                if entry != 'entry_count':
                    text += f"{entry}: {buffer[entry]['title']}\n"
                    counter += 1

                    if counter > 10:
                        page_list.append(discord.Embed(title=menu_title, description=text, colour=discord.Colour.orange()))
                        counter = 0
                        text = ""

                pass
            #anything left over will go into the last page
            page_list.append(discord.Embed(title=menu_title, description=text, colour=discord.Colour.orange()))

            ctx.bot.help_pages = page_list
            current = 0
            msg = await ctx.send(embed=ctx.bot.help_pages[current])
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

        except:
            pass

