import time
import random
import json
import os
from asyncio import sleep

import discord
from discord.ext import commands

# Import cogs for commands
import cogs.general
import cogs.game

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

logTime = time.strftime("%d.%m.%Y %H:%M:%S UTC", time.gmtime())

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=random.choice(statuses)))
    # Define important things
    global appInfo, logChannel
    appInfo = await bot.application_info()
    logChannel = bot.get_channel(631136267366694913)
    # Register cogs
    bot.add_cog(cogs.general.General(bot, appInfo, logChannel, statuses, logTime))
    bot.add_cog(cogs.game.Game(bot, logChannel, logTime))


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
        await ctx.send(f"Cooldown is active. Try again in {round(error.retry_after, 1)} seconds")
    elif isinstance(error, commands.errors.NoPrivateMessage):
        await ctx.author.send("This command can't be used in direct messages")
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


bot.run(token)
