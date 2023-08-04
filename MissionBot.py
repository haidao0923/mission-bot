import json
import discord
import pymongo
from discord.ext import commands
from GameList import game_list

with open('config.json', 'r') as f:
    config = json.load(f)

client = pymongo.MongoClient(config['mongoDBURI'])
db = client.user_messages
bot = commands.Bot(command_prefix=["!", "$", "@"], intents=discord.Intents.all(), case_insensitive=True)


@bot.check
async def correct_channel_check(ctx):
    return ctx.channel.name == "game-bot"


def find_or_create_user(handle):
    # Edge case of finding Game Data instead of specific user.
    # Game Data id is -1
    entry_id = -1 if handle == -1 else handle.id
    entry_name = "General Game" if handle == -1 else handle.name
    id_query = {"id": entry_id}
    user_data = db.users.find_one(id_query)
    if user_data is None:
        db.users.insert_one(
            {
                "id": entry_id,
                "name": entry_name,
                "point": 0,
                "message_count": 0
            }
        )
        user_data = db.users.find_one(id_query)
    return user_data


def get_attribute(handle, key):
    return find_or_create_user(handle)[key]


def set_attribute(handle, key, value):
    user_data = find_or_create_user(handle)
    name = "General Game" if handle == -1 else handle.name
    db.users.update_one(user_data, {"$set": {key: value, "name": name}})
    # Note database will keep the id even if user change username
    # so have to manually adjust here for display purposes.
    return user_data


def increment_attribute(handle, key, increment_amount=1):
    name = "General Game" if handle == -1 else handle.name
    user_data = find_or_create_user(handle)
    db.users.update_one(user_data, {"$inc": {key: increment_amount}, "$set": {"name": name}})
    return user_data


@bot.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(bot))


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return
    print(message.content)
    if message.content == 'start':
        response = "Hi there!"
        await message.channel.send(response)


@bot.command()
@commands.check(correct_channel_check)
async def ping(ctx):
    await ctx.channel.send("pong")
    increment_attribute(ctx.author, "message_count")
    message_count = get_attribute(ctx.author, "message_count")
    await ctx.channel.send(f'You have sent a total of {message_count} messages.')


@bot.command()
@commands.check(correct_channel_check)
async def stat(ctx, handle: discord.Member = None):
    if handle is None:
        handle = ctx.author
        user_data = find_or_create_user(handle)
    message = f'{handle.name} Stats:\nName: {handle.display_name}\nPoint: {user_data["point"]}\n' + \
              f'Message Count: {user_data["message_count"]}\nGames Played: '
    message += ", ".join([f'{game_list[int(key)]}: {value}' for key, value in sorted(
                    user_data["games_played"].items(), key=lambda x:x[1], reverse=True)])
    message += "\nGames Won: "
    message += ", ".join([f'{game_list[int(key)]}: {value}' for key, value in sorted(
                    user_data["games_won"].items(), key=lambda x:x[1], reverse=True)])
    await ctx.channel.send(message)


@bot.command()
@commands.check(correct_channel_check)
async def gamestat(ctx):
    game_data = find_or_create_user(-1)
    message = f'General Info:\nGames Played: '
    message += ", ".join([f'{game_list[int(key)]}: {value}' for key, value in sorted(
                    game_data["games_played"].items(), key=lambda x:x[1], reverse=True)])
    await ctx.channel.send(message)


@bot.command()
@commands.check(correct_channel_check)
async def leaderboard(ctx):
    user_count = 10 # How many user to display
    message = "**Leaderboard**\n"
    games_played_list = db.users.find({},
        {"name": 1, "games_played": 1})
    parsed_dict = {}
    for i in games_played_list:
        parsed_dict[i["name"]] = sum(i["games_played"].values()) if "games_played" in i else 0
    message += "\n".join([f'{key}: {value}' for key, value in sorted(
                        parsed_dict.items(), key=lambda x:x[1], reverse=True)[0:10]])
    await ctx.channel.send(message)


@bot.command()
@commands.has_role("Officer")
async def givepoint(ctx, point: int, members: commands.Greedy[discord.Member]):
    send_message = "Hi "
    for i in range(len(members)):
        send_message += members[i].mention + str(members[i].id)
        increment_attribute(members[i], "point", point)
    await ctx.channel.send(send_message)


@bot.command()
@commands.has_role("Officer")
async def addgame(ctx, game_id: int, members: commands.Greedy[discord.Member]):
    if game_id < 0 or game_id >= len(game_list):
        await ctx.channel.send("That Game ID is invalid!")
        return
    for i in range(len(members)):
        increment_attribute(members[i], f"games_played.{game_id}")

    increment_attribute(-1, f"games_played.{game_id}")
    increment_attribute(members[0], f"games_won.{game_id}")
    await ctx.channel.send("Game Recorded")


@bot.command()
@commands.has_role("Officer")
async def ag(ctx, game_id: int, members: commands.Greedy[discord.Member]):
    await addgame(ctx, game_id, members)


@bot.command()
@commands.has_role("Officer")
async def changegamesplayed(ctx, game_id: int, member: discord.Member, amount=0):
    if game_id < 0 or game_id >= len(game_list):
        await ctx.channel.send("That Game ID is invalid!")
        return
    if amount == 0:
        await ctx.channel.send("How much do you want to change?")
    increment_attribute(member, f"games_played.{game_id}", amount)
    increment_attribute(-1, f"games_played.{game_id}", amount)
    await ctx.channel.send("Data Changed")


@bot.command()
@commands.has_role("Officer")
async def changegameswon(ctx, game_id: int, member: discord.Member, amount=0):
    if game_id < 0 or game_id >= len(game_list):
        await ctx.channel.send("That Game ID is invalid!")
        return
    if amount == 0:
        await ctx.channel.send("How much do you want to change?")
    increment_attribute(member, f"games_won.{game_id}", amount)
    increment_attribute(-1, f"games_won.{game_id}", amount)
    await ctx.channel.send("Data Changed")


bot.run(config['token'])
