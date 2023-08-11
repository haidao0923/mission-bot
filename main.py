import json
import discord
import pymongo
from discord.ext import commands
from GameList import game_list

with open('config.json', 'r') as f:
    config = json.load(f)

client = pymongo.MongoClient(config['mongoDBURI'])
db = client.user_messages
bot = commands.Bot(command_prefix=["!", "$", "@"], intents=discord.Intents.all())

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
    db.users.update_one(user_data, {"$set": {key: value, "name": handle.name}})
    # Note database will keep the id even if user change username
    # so have to manually adjust here for display purposes.
    return user_data


def increment_attribute(handle, key, increment_amount=1):
    user_data = find_or_create_user(handle)
    db.users.update_one(user_data, {"$inc": {key: increment_amount}, "$set": {"name": handle.name}})
    return user_data


def display_user_stat(handle):
    user_data = find_or_create_user(handle)

    message = f'{handle.name} Stats:\nName: {handle.display_name}\nPoint: {user_data["point"]}\n' + \
              f'Message Count: {user_data["message_count"]}\nGames Played: '
    message += ", ".join([f'{game_list[int(key)][0]}: {value}' for key, value in user_data["games_played"].items()])
    message += "\n"
    message += ", ".join([f'{game_list[int(key)][0]}: {value}' for key, value in user_data["games_won"].items()])
    return message


def display_game_stat():
    game_data = find_or_create_user(-1)
    message = f'General Info:\nGames Played: '
    return message


def add_game():
    pass


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
async def stat(ctx, handle=None):
    if handle is None:
        handle = ctx.author
    await ctx.channel.send(display_user_stat(handle))


@bot.command()
@commands.check(correct_channel_check)
async def gamestat(ctx):
    await ctx.channel.send(display_game_stat())


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
async def recordgame(ctx, game_id: int, members: commands.Greedy[discord.Member]):
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
async def rg(ctx, game_id: int, members: commands.Greedy[discord.Member]):
    await recordgame(ctx, game_id, members)





bot.run(config['token'])
