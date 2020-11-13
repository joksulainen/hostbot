import time
from asyncio import sleep
import random
import json
import os

import discord
from discord.ext import commands

tokenFile = open("token.txt", "r")
token = tokenFile.read()
tokenFile.close()

COLOR = 0x0099ff
bot = commands.Bot(command_prefix="j.", help_command=None)


# Define automatic command deletion
# Credits to DJ#4806
def delete():
    async def predicate(ctx):
        await ctx.message.delete()
        return True
    return commands.check(predicate)


# A list of statuses for the bot to pick as playing status
statuses = ["with hosting stuff", "with chemicals", "with joksulainen", "with the boys", "with itself", "with nothing", "joksuBOT.exe",
            "joksuBOT - Playing joksuBOT - Playing joksuBOT"]

logTime = time.strftime("%D %H:%M:%S UTC", time.gmtime())

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=random.choice(statuses)))
    # Define important things
    global appInfo, logChannel, joinChannel, lobbyChannel, scoreChannel, joinReaction, discordServer, playerRole
    appInfo = await bot.application_info()
    logChannel = bot.get_channel(631136267366694913)
    joinChannel = bot.get_channel(614731761875943434)
    lobbyChannel = bot.get_channel(614731837587324929)
    scoreChannel = bot.get_channel(614770687521062928)
    joinReaction = bot.get_emoji(567204134441320451)
    discordServer = bot.get_guild(566111034063192085)
    playerRole = discordServer.get_role(614770824867479556)
    # Just incase, have the variables print out their types
    print(f"logChannel: {type(logChannel)}")
    print(f"joinChannel: {type(joinChannel)}")
    print(f"lobbyChannel: {type(lobbyChannel)}")
    print(f"scoreChannel: {type(scoreChannel)}")
    print(f"joinReaction: {type(joinReaction)}")
    print(f"discordServer: {type(discordServer)}")
    print(f"playerRole: {type(playerRole)}")


# Error handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send(f"I don't recognise this command. Use `{bot.command_prefix}help` for all the commands")
    elif isinstance(error, commands.errors.NotOwner):
        await ctx.send("This command is owner only")
    elif isinstance(error, commands.errors.BotMissingPermissions):
        await ctx.send(f"I'm missing the following permission(s) to execute this command: {', '.join(error.missing_perms)}")
    elif isinstance(error, commands.errors.MissingPermissions):
        await ctx.send(f"You are missing the following permission(s) to execute this command: {','.join(error.missing_perms)}")
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("You are missing required arguments for this command")
    elif isinstance(error, commands.errors.CommandInvokeError):
        await ctx.send("Something went wrong while invoking this command")
    elif isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.send(f"You are on cooldown for this command. Try again in {round(error.retry_after, 1)} seconds")
    elif isinstance(error, commands.errors.NoPrivateMessage):
        await ctx.author.send("This command can't be used in private messages")
    elif isinstance(error, commands.errors.MissingAnyRole):
        await ctx.send(f"You are missing the following role(s): {error.missing_roles}")
    elif isinstance(error, commands.errors.NSFWChannelRequired):
        await ctx.send("This command requires to be executed in a NSFW channel")
    else:
        await ctx.send("An unknown error has occurred. Get that lazy boi to fix it")

# Blacklisted channels
blacklistedChannels = [566111034063192087, 635031521040007198]

# Mention sender when sender mentions bot
@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        if "@everyone" not in message.content and "@here" not in message.content:
            await message.channel.send(f"<@!{message.author.id}>")
            await logChannel.send(f"[Bot @ {logTime}] Bot pinged by {message.author}")
            return
    elif message.channel.id in blacklistedChannels:
        if message.content.startswith(bot.command_prefix):
            await message.delete()
            warning = await message.channel.send(f"<@!{message.author.id}> > This channel is blacklisted from using commands")
            await logChannel.send(f"[Bot @ {logTime}] {message.author} attempted to use a command in <#{message.channel.id}>")
            await sleep(3)
            await warning.delete()
            return
    else:
        await bot.process_commands(message)


# Loads idlist.json into idlist variable so the bot can work with it
idlistFile = open("idlist.json", "r")
idlist = json.load(idlistFile)
idlistFile.close()


# Commands for general public
@bot.command()
async def help(ctx, category="general"):
    helpdescription = "List of all the commands this bot has to offer\n(required) [optional]"
    helpcategories = ["general (Default)", "game"]
    if category == "general":
        e = discord.Embed(title="General commands", description=helpdescription, colour=COLOR)
        e.set_footer(text=f"Created by {appInfo.owner.display_name}#{appInfo.owner.discriminator}", icon_url=appInfo.owner.avatar_url)
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
        e = discord.Embed(title="Game management commands (Host only)", description=helpdescription, colour=COLOR)
        e.set_footer(text=f"Created by {appInfo.owner.display_name}#{appInfo.owner.discriminator}", icon_url=appInfo.owner.avatar_url)
        e.add_field(name="game", value="Base command", inline=False)
        e.add_field(name="-createinvite \"difficulty\" [minutes]", value="Creates an invite with custom difficulty string", inline=False)
        e.add_field(name="-cancelinvite", value="Cancels the ongoing invite", inline=False)
        e.add_field(name="-songcheck \"(name)\" \"(pack)\" \"(difficulty)\"", value="Sends a check message for song owned", inline=False)
        e.add_field(name="-startround (time in sec)", value="Starts a round", inline=False)
        e.add_field(name="-cancelround", value="Cancels the ongoing round", inline=False)
        e.add_field(name="-removeplayers", value="Removes Player 3 role from those who still have it", inline=False)
        await ctx.send(embed=e)
    else:
        await ctx.send(f"Invalid category\nValid categories:\n`{', '.join(helpcategories)}`")


@bot.command()
async def info(ctx):
    e = discord.Embed(title=f"{appInfo.name} | A bot that is made for hosting games", description=f"{appInfo.owner.display_name} uses this bot to host games", colour=COLOR)
    e.set_footer(text=f"Created by {appInfo.owner.display_name}#{appInfo.owner.discriminator}", icon_url=appInfo.owner.avatar_url)
    await ctx.send(embed=e)


@bot.command()
async def changelog(ctx):
    changelogFile = open("changelog.txt", "r")
    changelogContent = changelogFile.read()
    changelogFile.close()
    e = discord.Embed(title="Changelog", description="Most recent changes at top", colour=COLOR)
    e.set_footer(text=f"Created by {appInfo.owner.display_name}#{appInfo.owner.discriminator}", icon_url=appInfo.owner.avatar_url)
    e.add_field(name="\u200B", value=changelogContent, inline=False)
    await ctx.send(embed=e)


@bot.command()
async def ping(ctx):
    t1 = time.perf_counter()
    await ctx.channel.trigger_typing()
    t2 = time.perf_counter()
    await ctx.send(f"\U0001f3d3 **Pong!** `{str(round((t2 - t1) * 100))}ms`")


coin = ["Heads", "Tails"]
@bot.command()
async def flipcoin(ctx):
    await ctx.send(f"The coin landed on: {random.choice(coin)}")


@bot.command()
async def rng(ctx, maximum=1, minimum=0):
    result = random.randint(minimum, maximum)
    result = result.replace("69", "nice")
    result = result.replace("420", "weed")
    await ctx.send(f"Result: {result}")


@bot.command()
async def customstatus(ctx, *, string: str):
    await bot.change_presence(activity=discord.Game(name=string))
    await ctx.send(f"Changed status to \"{string}\"")
    await logChannel.send(f"[Bot @ {logTime}] {ctx.user} has changed this bot's status to \"{string}\"")


@bot.command()
async def randomstatus(ctx, showCount=""):
    if showCount.lower() == "y":
        await ctx.send(f"There are {len(statuses)} statuses to pick from")
    else:
        await bot.change_presence(activity=discord.Game(name=random.choice(statuses)))
        await ctx.send("Changed status to a random one from the list")
        await logChannel.send(f"[Bot @ {logTime}] {ctx.user} has randomized this bot's status")


@delete()
@bot.group()
async def id(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Specify a valid mode")

@id.command()
async def add(ctx, id=""):
    user = str(ctx.author.id)
    if len(id) == 9 and id.isdigit():
        if user not in idlist:
            idlist[user] = id
            idlistFile = open("idlist.json", "w")
            json.dump(idlist, idlistFile, indent=4, sort_keys=True)
            idlistFile.close()
            await ctx.send(f"<@!{ctx.author.id}> > Added your Arcaea ID to the database")
        else:
            await ctx.send(f"<@!{ctx.author.id}> > You already have an Arcaea ID in the database for this account")
    else:
        await ctx.send(f"<@!{ctx.author.id}> > Invalid Arcaea ID. Check that your Arcaea ID is 9 digits long")
    
@id.command()
async def modify(ctx, id=""):
    user = str(ctx.author.id)
    if len(id) == 9 and id.isdigit():
        if user in idlist:
            idlist[user] = id
            idlistFile = open("idlist.json", "w")
            json.dump(idlist, idlistFile, indent=4, sort_keys=True)
            idlistFile.close()
            await ctx.send(f"<@!{ctx.author.id}> > Modified your Arcaea ID entry in the database")
        else:
            await ctx.send(f"<@!{ctx.author.id}> > You do not have an Arcaea ID in the database for this account")
    else:
        await ctx.send(f"<@!{ctx.author.id}> > Invalid Arcaea ID. Check that your Arcaea ID is 9 digits long")

@id.command()
async def remove(ctx):
    user = str(ctx.author.id)
    del idlist[user]
    idlistFile = open("idlist.json", "w")
    json.dump(idlist, idlistFile, indent=4, sort_keys=True)
    idlistFile.close()
    await ctx.send(f"<@!{ctx.author.id}> > Removed your Arcaea ID from the database")

@id.command()
async def current(ctx):
    user = str(ctx.author.id)
    if user in idlist:
        await ctx.author.send(f"The current Arcaea ID for your account is `{idlist[user]}`")
    else:
        await ctx.author.send(f"You do not have an Arcaea ID for this account yet. Use `{bot.command_prefix}id add (Arcaea ID)` to add your ID")


@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def pit(ctx):
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


@bot.command()
async def praise(ctx, character="", showCount=""):
    if character.lower() == "hikari":
        if showCount.lower() == "y":
            await ctx.send(f"There are {len(hikaripraises)} praises for Hikari")
        else:
            await ctx.send(random.choice(hikaripraises))
    elif character.lower() == "tairitsu":
        if showCount.lower() == "y":
            await ctx.send(f"There are {len(tairitsupraises)} praises for Tairitsu")
        else:
            await ctx.send(random.choice(tairitsupraises))
    elif character.lower() == "ayu":
        if showCount.lower() == "y":
            await ctx.send(f"There are {len(ayupraises)} praises for Ayu")
        else:
            await ctx.send(random.choice(ayupraises))
    else:
        await ctx.send(f"Specify a valid character\nValid characters:\n`{', '.join(characters)}`")


@delete()
@bot.group()
@commands.has_role(566124515202170890)
async def game(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.author.send("Invalid subcommand")


inviteActive = False
inviteTimer = None

async def inviteLogic(ctx, difficulty: str, time: float):
    global inviteActive
    inviteActive = True
    minutesec = time*60
    message = await joinChannel.send(f"A game of {difficulty} Arcaea Rhythm Royale is about to start!\nReact with <:join_game:567204134441320451> to join!\n"
                                     f"Invite expires in {str(time)} minutes.\n@everyone")
    await message.add_reaction(":join_game:567204134441320451")
    await logChannel.send(f"[Lobby 2 @ {logTime}] Created an invite with a length of {str(time/2)} minutes")
    await sleep(minutesec/2)
    await joinChannel.send(f"Invite expires in {str(time/2)} minutes.")
    await logChannel.send(f"[Lobby 2 @ {logTime}] Invite expires in {str(time/2)} minutes")
    await sleep(minutesec/2)
    await joinChannel.send("Invite expired.")
    await logChannel.send(f"[Lobby 2 @ {logTime}] Invite expired")
    reactions = (await ctx.get_message(message.id)).reactions  # Retrieve reactions
    reaction = [re for re in reactions if re.emoji == joinReaction][0]  # Get reaction instance to retrieve users
    # Retrieve a list of users that reacted with the specified reaction, excluding bot
    users = [u for u in (await reaction.users().flatten()) if not u.bot]
    # Guild instance has been defined on_ready()
    player = playerRole  # Get role instance to be added
    for user in users:  # Assign the role to those users
        await user.add_roles(player)
    await logChannel.send(f"[Lobby 3 @ {logTime}] Gave all participants Player 3 role")
    inviteActive = False

@game.command()
@commands.bot_has_guild_permissions(manage_roles=True)
@commands.bot_has_permissions(add_reactions=True)
async def createinvite(ctx, difficulty: str, time: float = 10):
    global inviteTimer, inviteActive
    if inviteActive:
        return await ctx.author.send("An existing invite is currently active")
    inviteTimer = bot.loop.create_task(inviteLogic(ctx, difficulty, time))

@game.command()
async def cancelinvite(ctx):
    global inviteActive, inviteTimer
    if not inviteActive:
        return await ctx.author.send("There is no existing invite currently active")
    inviteTimer.cancel()
    inviteActive = False
    await joinChannel.send("Invite has been canceled")
    await logChannel.send(f"[Lobby 2 @ {logTime}] Invite canceled")


@game.command()
@commands.bot_has_permissions(add_reactions=True)
async def songcheck(ctx, name="N/A", pack="N/A", difficulty="N/A"):
    message = await lobbyChannel.send(f"Do you have the following song unlocked? <@&614770824867479556>\nName: {name}\nPack: {pack}\nDifficulty: {difficulty}")
    await message.add_reaction(":owned:567204206142816273")
    await message.add_reaction(":not_owned:567204277148188686")
    await logChannel.send(f"[Lobby 2 @ {logTime}] Asked for ownership of the following song:\nName: {name}\nPack: {pack}\nDifficulty: {difficulty}")


roundActive = False
roundTimer = None

async def roundLogic(time: int):
    global roundActive
    roundActive = True
    minutes = time // 60
    seconds = time % 60
    await logChannel.send(f"[Lobby 2 @ {logTime}] Begin round triggered")
    await lobbyChannel.send("Round starts in 15 seconds")
    await sleep(10)
    await lobbyChannel.send("Round starts in 5 seconds")
    await sleep(5)
    if seconds >= 10:
        await lobbyChannel.send(f"Finish chart in {minutes}:{seconds}. Good luck! <@&614770824867479556>")
    else:
        await lobbyChannel.send(f"Finish chart in {minutes}:0{seconds}. Good luck! <@&614770824867479556>")
    await scoreChannel.send("-==========BEGIN==========-")
    await logChannel.send(f"[Lobby 2 @ {logTime}] Round begun")
    await sleep(time/2)
    await lobbyChannel.send("Half time")
    await scoreChannel.send("-========HALF TIME========-")
    await logChannel.send(f"[Lobby 2 @ {logTime}] Half time")
    await sleep(time/2)
    await lobbyChannel.send("Round is over. Verifying scores... <@&614770824867479556>")
    await scoreChannel.send("-===========END===========-")
    await logChannel.send(f"[Lobby 2 @ {logTime}] Round ended")
    roundActive = False

@game.command()
async def beginround(ctx, time: int):
    global roundTimer, roundActive
    if roundActive:
        return await ctx.author.send("A round is currently active")
    roundTimer = bot.loop.create_task(roundLogic(time))

@game.command()
async def cancelround(ctx):
    global roundActive, roundTimer
    if not roundActive:
        return await ctx.author.send("There is no round currently active")
    roundTimer.cancel()
    roundActive = False
    await lobbyChannel.send("Round has been cancelled <@&614770824867479556>")
    await scoreChannel.send("-========CANCELLED========-")
    await logChannel.send(f"[Lobby 2 @ {logTime}] Round cancelled")

@game.command()
@commands.bot_has_guild_permissions(manage_roles=True)
async def removeplayers(ctx):
    guild = bot.get_guild(discordServer)  # Get guild instance to retrieve role
    player = guild.get_role(playerRole)  # Get role instance to be added
    users = player.members  # Get all users with the role
    for user in users:  # Remove the role
        await user.remove_roles(player)
    await logChannel.send(f"[Lobby 2 @ {logTime}] Removed Player 2 role from existing role holders")


bot.run(token)
