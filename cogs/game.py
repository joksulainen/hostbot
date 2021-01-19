import random
import os
import time
import json
from asyncio import sleep

import discord
from discord.ext import commands

# Dependency on idlist variable
import general

# Define automatic command deletion
# Credits to DJ#4806
def delete():
    async def predicate(ctx):
        await ctx.message.delete()
        return True
    return commands.check(predicate)

class Game(commands.Cog):
    def __init__(self, bot, logChannel, logTime):
        self.bot = bot
        self.logChannel = logChannel
        self.logTime = logTime
        
        self.joinChannel = bot.get_channel(614731761875943434)
        self.lobbyChannel = bot.get_channel(614731837587324929)
        self.scoreChannel = bot.get_channel(614770687521062928)
        self.joinReaction = bot.get_emoji(567204134441320451)
        self.discordServer = bot.get_guild(566111034063192085)
        self.playerRole = self.discordServer.get_role(614770824867479556)

    @delete()
    @commands.group()
    @commands.has_role(566124515202170890)
    async def game(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.author.send("Invalid subcommand")


    inviteActive = False
    inviteTimer = None

    async def inviteLogic(self, ctx, difficulty: str, time: float):
        global inviteActive
        inviteActive = True
        minutesec = time*60
        message = await self.joinChannel.send(f"""A game of {difficulty} Arcaea Rhythm Royale is about to start!\nReact with <:join_game:567204134441320451> to join!\n
                                              Invite expires in {str(time)} minutes.\n@everyone""")
        await message.add_reaction(":join_game:567204134441320451")
        await self.logChannel.send(f"[Lobby 2 @ {self.logTime}] Created an invite with a length of {str(time/2)} minutes")
        await sleep(minutesec/2)
        await self.joinChannel.send(f"Invite expires in {str(time/2)} minutes.")
        await self.logChannel.send(f"[Lobby 2 @ {self.logTime}] Invite expires in {str(time/2)} minutes")
        await sleep(minutesec/2)
        await self.joinChannel.send("Invite expired.")
        await self.logChannel.send(f"[Lobby 2 @ {self.logTime}] Invite expired")
        reactions = (await ctx.get_message(message.id)).reactions  # Retrieve reactions
        reaction = [re for re in reactions if re.emoji == self.joinReaction][0]  # Get reaction instance to retrieve users
        # Retrieve a list of users that reacted with the specified reaction, excluding bot
        users = [u for u in (await reaction.users().flatten()) if not u.bot]
        # Guild and role instance have been defined in on_ready event
        for user in users:  # Assign the role to those users
            await user.add_roles(self.playerRole)
        await self.logChannel.send(f"[Lobby 2 @ {self.logTime}] Gave all participants Player 2 role")
        inviteActive = False

    @game.command()
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.bot_has_permissions(add_reactions=True)
    async def createinvite(self, ctx, difficulty: str, time: float = 10):
        global inviteTimer, inviteActive
        if inviteActive:
            return await ctx.author.send("An existing invite is currently active")
        inviteTimer = self.bot.loop.create_task(self.inviteLogic(ctx, difficulty, time))

    @game.command()
    async def cancelinvite(self, ctx):
        global inviteActive, inviteTimer
        if not inviteActive:
            return await ctx.author.send("There is no existing invite currently active")
        inviteTimer.cancel()
        inviteActive = False
        await self.joinChannel.send("Invite has been canceled")
        await self.logChannel.send(f"[Lobby 2 @ {self.logTime}] Invite canceled")


    @game.command()
    @commands.bot_has_permissions(add_reactions=True)
    async def songcheck(self, ctx, name="N/A", pack="N/A", difficulty="N/A"):
        message = await self.lobbyChannel.send(f"Do you have the following song unlocked? <@&614770824867479556>\nName: {name}\nPack: {pack}\nDifficulty: {difficulty}")
        await message.add_reaction(":owned:567204206142816273")
        await message.add_reaction(":not_owned:567204277148188686")
        await self.logChannel.send(f"[Lobby 2 @ {self.logTime}] Asked for ownership of the following song:\nName: {name}\nPack: {pack}\nDifficulty: {difficulty}")


    roundActive = False
    roundTimer = None

    async def roundLogic(self, time: int):
        global roundActive
        roundActive = True
        minutes = time // 60
        seconds = time % 60
        await self.logChannel.send(f"[Lobby 2 @ {self.logTime}] Begin round triggered")
        await self.lobbyChannel.send("Round starts in 15 seconds")
        await sleep(10)
        await self.lobbyChannel.send("Round starts in 5 seconds")
        await sleep(5)
        if seconds >= 10:
            await self.lobbyChannel.send(f"Finish chart in {minutes}:{seconds}. Good luck! <@&614770824867479556>")
        else:
            await self.lobbyChannel.send(f"Finish chart in {minutes}:0{seconds}. Good luck! <@&614770824867479556>")
        await self.scoreChannel.send("-==========BEGIN==========-")
        await self.logChannel.send(f"[Lobby 2 @ {self.logTime}] Round begun")
        await sleep(time/2)
        await self.lobbyChannel.send("Half time")
        await self.scoreChannel.send("-========HALF TIME========-")
        await self.logChannel.send(f"[Lobby 2 @ {self.logTime}] Half time")
        await sleep(time/2)
        await self.lobbyChannel.send("Round is over. Verifying scores... <@&614770824867479556>")
        await self.scoreChannel.send("-===========END===========-")
        await self.logChannel.send(f"[Lobby 2 @ {self.logTime}] Round ended")
        roundActive = False

    @game.command()
    async def beginround(self, ctx, time: int):
        global roundTimer, roundActive
        if roundActive:
            return await ctx.author.send("A round is currently active")
        roundTimer = self.bot.loop.create_task(self.roundLogic(time))

    @game.command()
    async def cancelround(self, ctx):
        global roundActive, roundTimer
        if not roundActive:
            return await ctx.author.send("There is no round currently active")
        roundTimer.cancel()
        roundActive = False
        await self.lobbyChannel.send("Round has been cancelled <@&614770824867479556>")
        await self.scoreChannel.send("-========CANCELLED========-")
        await self.logChannel.send(f"[Lobby 2 @ {self.logTime}] Round cancelled")

    @game.command()
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def removeplayers(self, ctx):
        users = self.playerRole.members  # Get all users with the role
        for user in users:  # Remove the role
            await user.remove_roles(self.playerRole)
        await self.logChannel.send(f"[Lobby 2 @ {self.logTime}] Removed Player 2 role from existing role holders")
