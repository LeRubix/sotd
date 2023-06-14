import discord
import discord.utils
import asyncio
import datetime
from datetime import datetime
from discord.ext import commands
from discord import Spotify
intents = discord.Intents.all()
client = discord.Client(intents=intents)



BOT_TOKEN = ""
CHANNEL_ID = ""



@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = f'**You are on Cooldown!**\nPlease try again in **{error.retry_after:,.0f}** seconds / **{error.retry_after / 60:,.0f}** minutes / **{error.retry_after / 3600:,.0f}** hours.'
        await ctx.send(msg)
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have the role/permissions to use this command.")
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("The bot doesn't have the permissions to use this command.")
    else:
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)



@client.command()
@commands.cooldown(1,43200,commands.BucketType.user)
async def sotd(ctx, link=None):
    sotdchannel = ctx.guild.get_channel(CHANNEL_ID)
    user = ctx.author
    if(link != None):
            msg2 = await sotdchannel.send(datetime.now().strftime(f"__(%a, %d/%m)__\n**{ctx.author.name}**'s Song of the Day:\n{link}"))
            await ctx.message.delete()
            await msg2.add_reaction('<:Upvote:802500869773590548>')
            await msg2.add_reaction('<:Downvote:802500955521810432>')
            return
    for activity in user.activities:
        if isinstance(activity, Spotify):
            em = discord.Embed(color=activity.color)
            em.title = (datetime.now().strftime(f"(%a, %d/%m)\n__{ctx.author.name}'s__ Song of the Day:"))
            em.set_image(url=activity.album_cover_url)
            em.add_field(name="**Song:**", value=f"{activity.title}", inline=False)
            em.add_field(name="**Artist:**", value=f"{activity.artist}", inline=False)
            em.add_field(name="**Album:**", value=activity.album, inline=False)
            em.add_field(name=f"**_ _**", value=f"[Song Link](https://open.spotify.com/track/{activity.track_id})")
            confirm_msg = await ctx.reply(f'Are you sure you want to submit **"{activity.title} - {activity.artist}"** as your song of the day?\nRespond with "yes"/"y" to confirm or "no"/"n" to cancel. Confirmation will time out in 30 seconds.')

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                response = await client.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError:
                timeoutmsg = await ctx.send("Confirmation timed out.")
                await ctx.message.delete()
                await asyncio.sleep(6)
                await timeoutmsg.delete()
                await ctx.command.reset_cooldown(ctx)
                return
            
            # if response is different than yes / y - return
            if response.content.lower() not in ("yes", "y"):
                await confirm_msg.delete()
                await response.delete()
                await ctx.message.delete()
                ctx.command.reset_cooldown(ctx)
                cancelmsg = await ctx.send("Cancelled Confirmation.")
                await asyncio.sleep(6)
                await cancelmsg.delete()
                return

            msg = await sotdchannel.send(embed=em)
            await confirm_msg.delete()
            await response.delete()
            await ctx.message.delete()
            await msg.add_reaction('👍')
            await msg.add_reaction('👎')
            break
    else:
        if(link == None):
            errormsg = await ctx.reply("You're not listening to spotify right now. If you are, it's either a local file or discord isn't picking it up. Double check and try again or use a link instead. (?sotd <link>)")
            await ctx.command.reset_cooldown(ctx)
            await asyncio.sleep(6)
            await ctx.message.delete()
            await errormsg.delete()

client.run("BOT_TOKEN")
