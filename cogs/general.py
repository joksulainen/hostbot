import random
import os
import time
import json
from asyncio import sleep

import discord
from discord.ext import commands

# Define automatic command deletion
# Credits to DJ#4806
def delete():
    async def predicate(ctx):
        await ctx.message.delete()
        return True
    return commands.check(predicate)

class General(commands.Cog):
    def __init__(self, bot, appInfo, logChannel, statuses, logTime):
        self.bot = bot
        self.appInfo = appInfo
        self.logChannel = logChannel
        self.statuses = statuses
        self.logTime = logTime

        self.helpdescription = "List of all the commands this bot has to offer\n(required) [optional]"
        self.helpcategories = ["general (Default)", "game"]
        self.COLOR = 0x0099ff
        # Loads idlist.json into idlist variable so the bot can work with it
        self.idlistFile = open("idlist.json", "r")
        self.idlist = json.load(self.idlistFile)
        self.idlistFile.close()


    @commands.command()
    async def help(self, ctx, category="general"):
        if category == "general":
            e = discord.Embed(title="General commands", description=self.helpdescription, colour=self.COLOR)
            e.set_footer(text=f"Created by {self.appInfo.owner.display_name}#{self.appInfo.owner.discriminator}", icon_url=self.appInfo.owner.avatar_url)
            e.add_field(name="help [category]", value="The help embed for the specified category. Defaults to this category", inline=False)
            e.add_field(name="info", value="Info about the bot and its creator", inline=False)
            e.add_field(name="changelog", value="Changelog for the bot", inline=False)
            e.add_field(name="ping", value="Test for latency between the bot and discord", inline=False)
            e.add_field(name="flipcoin", value="Flips a coin", inline=False)
            e.add_field(name="rng (maximum) [minimum]", value="Picks a random integer between minimum and maximum", inline=False)
            e.add_field(name="customstatus (string)", value="Changes the status to your own string", inline=False)
            e.add_field(name="randomstatus [count: y]", value="Changes the status to a random status from the list", inline=False)
            e.add_field(name="id (mode: add/modify/remove/current) (add/modify mode: id)", value="Manipulate your Arcaea ID entry in the bot database", inline=False)
            e.add_field(name="pit", value="Pit", inline=False)
            e.add_field(name="praise (character) [count: y]", value="Sends a random praise for the specified character", inline=False)
            await ctx.send(embed=e)
        elif category == "game":
            e = discord.Embed(title="Game management commands (Host only)", description=self.helpdescription, colour=self.COLOR)
            e.set_footer(text=f"Created by {self.appInfo.owner.display_name}#{self.appInfo.owner.discriminator}", icon_url=self.appInfo.owner.avatar_url)
            e.add_field(name="game", value="Base command", inline=False)
            e.add_field(name="-createinvite \"difficulty\" [minutes]", value="Creates an invite with custom difficulty string", inline=False)
            e.add_field(name="-cancelinvite", value="Cancels the ongoing invite", inline=False)
            e.add_field(name="-songcheck \"(name)\" \"(pack)\" \"(difficulty)\"", value="Sends a check message for song owned", inline=False)
            e.add_field(name="-startround (time in sec)", value="Starts a round", inline=False)
            e.add_field(name="-cancelround", value="Cancels the ongoing round", inline=False)
            e.add_field(name="-removeplayers", value="Removes Player 2 role from those who still have it", inline=False)
            await ctx.send(embed=e)
        else:
            await ctx.send(f"Invalid category\nValid categories:\n`{', '.join(self.helpcategories)}`")


    @delete()
    @commands.command()
    async def info(self, ctx):
        e = discord.Embed(title=f"{self.appInfo.name} | A bot that is made for hosting games", description=f"{self.appInfo.owner.display_name} uses this bot to host games", colour=self.COLOR)
        e.set_footer(text=f"Created by {self.appInfo.owner.display_name}#{self.appInfo.owner.discriminator}", icon_url=self.appInfo.owner.avatar_url)
        await ctx.send(embed=e)


    @commands.command()
    async def changelog(self, ctx):
        changelogFile = open("changelog.txt", "r")
        changelogContent = changelogFile.read()
        changelogFile.close()
        e = discord.Embed(title="Changelog", description="Most recent changes at top", colour=self.COLOR)
        e.set_footer(text=f"Created by {self.appInfo.owner.display_name}#{self.appInfo.owner.discriminator}", icon_url=self.appInfo.owner.avatar_url)
        e.add_field(name="\u200B", value=changelogContent, inline=False)
        await ctx.send(embed=e)


    @commands.command()
    async def ping(self, ctx):
        t1 = time.perf_counter()
        await ctx.channel.trigger_typing()
        t2 = time.perf_counter()
        await ctx.send(f"\U0001f3d3 **Pong!** `{str(round((t2 - t1) * 100))}ms`")


    coin = ["Heads", "Tails"]
    @commands.command()
    async def flipcoin(self, ctx):
        await ctx.send(f"The coin landed on: {random.choice(self.coin)}")


    @commands.command()
    async def rng(self, ctx, maximum=1, minimum=0):
        result = random.randint(minimum, maximum)
        await ctx.send(f"Result: {result}")


    @commands.command()
    async def customstatus(self, ctx, *, string: str):
        await self.bot.change_presence(activity=discord.Game(name=string))
        await ctx.send(f"Changed status to \"{string}\"")
        await self.logChannel.send(f"[Bot @ {self.logTime}] {ctx.author} has changed this bot's status to \"{string}\"")


    @commands.command()
    async def randomstatus(self, ctx, showCount=""):
        if showCount.lower() == "y":
            await ctx.send(f"There are {len(self.statuses)} statuses to pick from")
        else:
            await self.bot.change_presence(activity=discord.Game(name=random.choice(self.statuses)))
            await ctx.send("Changed status to a random one from the list")
            await self.logChannel.send(f"[Bot @ {self.logTime}] {ctx.author} has randomized this bot's status")


    @delete()
    @commands.group()
    async def id(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Specify a valid mode")

    @id.command()
    async def add(self, ctx, id=""):
        user = str(ctx.author.id)
        if len(id) == 9 and id.isdigit():
            if user not in self.idlist:
                self.idlist[user] = id
                idlistFile = open("idlist.json", "w")
                json.dump(self.idlist, idlistFile, indent=4, sort_keys=True)
                idlistFile.close()
                await ctx.send(f"<@!{ctx.author.id}> > Added your Arcaea ID to the database")
            else:
                await ctx.send(f"<@!{ctx.author.id}> > You already have an Arcaea ID in the database for this account")
        else:
            await ctx.send(f"<@!{ctx.author.id}> > Invalid Arcaea ID. Check that your Arcaea ID is 9 digits long")
        
    @id.command()
    async def modify(self, ctx, id=""):
        user = str(ctx.author.id)
        if len(id) == 9 and id.isdigit():
            if user in self.idlist:
                self.idlist[user] = id
                idlistFile = open("idlist.json", "w")
                json.dump(self.idlist, idlistFile, indent=4, sort_keys=True)
                idlistFile.close()
                await ctx.send(f"<@!{ctx.author.id}> > Modified your Arcaea ID entry in the database")
            else:
                await ctx.send(f"<@!{ctx.author.id}> > You do not have an Arcaea ID in the database for this account")
        else:
            await ctx.send(f"<@!{ctx.author.id}> > Invalid Arcaea ID. Check that your Arcaea ID is 9 digits long")

    @id.command()
    async def remove(self, ctx):
        user = str(ctx.author.id)
        del self.idlist[user]
        idlistFile = open("idlist.json", "w")
        json.dump(self.idlist, idlistFile, indent=4, sort_keys=True)
        idlistFile.close()
        await ctx.send(f"<@!{ctx.author.id}> > Removed your Arcaea ID from the database")

    @id.command()
    async def current(self, ctx):
        user = str(ctx.author.id)
        if user in self.idlist:
            await ctx.author.send(f"The current Arcaea ID for your account is `{self.idlist[user]}`")
        else:
            await ctx.author.send(f"You do not have an Arcaea ID for this account yet. Use `{self.bot.command_prefix}id add (Arcaea ID)` to add your ID")


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pit(self, ctx):
        pitImageList = os.listdir("images/pit/")
        chance = random.randint(1, 50)
        if chance == 1:
            await ctx.send("StooPit", file=discord.File("images/pit/"+random.choice(pitImageList)))
        else:
            await ctx.send("Pit", file=discord.File("images/pit/"+random.choice(pitImageList)))


    # Praise stuff
    characters = ["hikari", "tairitsu", "ayu"]
    hikaripraises = ["Hikari best girl", "Tairitsu is Hikari but dark mode", "Hikari cutest girl", "Hikari's beauty is indescribable with words"]
    tairitsupraises = ["Tairitsu best girl", "Hikari is Tairitsu but light mode", "Tairitsu cutest girl", "Tairitsu's beauty is indescribable with words"]
    ayupraises = ["Ayu best tr4p", "Roses are red\nViolets are blue\nTr4ps are the best\nAnd Ayu too!"]


    @commands.command()
    async def praise(self, ctx, character="", showCount=""):
        if character.lower() == "hikari":
            if showCount.lower() == "y":
                await ctx.send(f"There are {len(self.hikaripraises)} praises for Hikari")
            else:
                await ctx.send(random.choice(self.hikaripraises))
        elif character.lower() == "tairitsu":
            if showCount.lower() == "y":
                await ctx.send(f"There are {len(self.tairitsupraises)} praises for Tairitsu")
            else:
                await ctx.send(random.choice(self.tairitsupraises))
        elif character.lower() == "ayu":
            if showCount.lower() == "y":
                await ctx.send(f"There are {len(self.ayupraises)} praises for Ayu")
            else:
                await ctx.send(random.choice(self.ayupraises))
        else:
            await ctx.send(f"Specify a valid character\nValid characters:\n`{', '.join(self.characters)}`")
