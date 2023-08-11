import json
import discord
import pymongo
from discord.ext import commands
from GameList import game_list

with open('config.json', 'r') as f:
    config = json.load(f)

client = pymongo.MongoClient(config['mongoDBURI'])
db = client.custom_database
bot = commands.Bot(command_prefix=["!", "$", "@"], intents=discord.Intents.all(), case_insensitive=True)
bot.remove_command("help")
collection = None


@bot.check
async def correct_channel_check(ctx):
    global collection
    if ctx.channel.name == "game-bot":
        collection = db.board_game
        return True
    elif ctx.channel.name == "task-bot":
        collection = db.task_master
        return True
    return False


def find_or_create_user(handle):
    # Edge case of finding Game Data instead of specific user.
    # Game Data id is -1
    entry_id = -1 if handle == -1 else handle.id
    entry_name = "General Game" if handle == -1 else handle.name
    id_query = {"id": entry_id}
    user_data = collection.find_one(id_query)
    if user_data is None:
        collection.insert_one(
            {
                "id": entry_id,
                "name": entry_name,
                "point": 0,
                "message_count": 0
            }
        )
        user_data = collection.find_one(id_query)
    return user_data


def get_attribute(handle, key):
    return find_or_create_user(handle)[key]


def set_attribute(handle, key, value):
    user_data = find_or_create_user(handle)
    name = "General Game" if handle == -1 else handle.name
    collection.update_one(user_data, {"$set": {key: value, "name": name}})
    # Note database will keep the id even if user change username
    # so have to manually adjust here for display purposes.
    return user_data


def increment_attribute(handle, key, increment_amount=1):
    name = "General Game" if handle == -1 else handle.name
    user_data = find_or_create_user(handle)
    collection.update_one(user_data, {"$inc": {key: increment_amount}, "$set": {"name": name}})
    return user_data


@bot.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(bot))


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return
    increment_attribute(message.author, "message_count")
    if message.content == 'Hello bot':
        response = "Hi " + message.author.mention
        await message.channel.send(response)


@bot.command()
async def help(ctx):
    message = "```!gameid - display id/point/playercount of all games\n" + \
            "!stat [@ping] - display your stat/pinged user stat\n" + \
            "!gamestat - display general stat\n" + \
            "!leaderboard - display point leaderboard\n" + \
            "!leaderboard game - display overall games leaderboard\n" + \
            "!leaderboard [gameid] - display leaderboard for specific game\n```" + \
            "**The following commands can only be used by Officers:**" + \
            "```!givepoint [point] [@ping (1 or more users)] - give point to pinged users\n" + \
            "!recordgame [gameid] [@ping (1 or more users in descending order (first pinged = 1st place))]\n" + \
            "!rg [gameid] [@ping (1 or more users)] - shortcut for above ^ (record game played and award points)\n" + \
            "!changegamesplayed [gameid] [@ping] [amount] - change games played retroactively\n" + \
            "!changegameswon [gameid] [@ping] [amount] - change games won retroactively\n" + \
            "```"
    await ctx.channel.send(message)


@bot.command()
async def h(ctx):
    await help(ctx)


@bot.command()
async def gameid(ctx):
    message = "Game Database:\nActual Points are calculated using the following formula:\n" + \
              "(point / ranking) * (table size / best table size)\n*For example, if a game is worth 100 points, " + \
              "the best table size 4, and you rank 2nd in a 3-player game, you will gain " + \
              "(100 / 2) * (3 / 4) = 37.5 points = 37 points (rounded down)*\n```"
    for i in range(len(game_list)):
        message += f"{i} | {game_list[i][0]} | {game_list[i][1]} points | {game_list[i][2]} recommended players\n"
        if i % 20 == 0:
            message += "```"
            await ctx.channel.send(message)
            message = "```"
    message += "```"
    await ctx.channel.send(message)


@bot.command()
async def ping(ctx):
    await ctx.channel.send("pong")
    increment_attribute(ctx.author, "message_count")
    message_count = get_attribute(ctx.author, "message_count")
    await ctx.channel.send(f'You have sent a total of {message_count} messages.')


@bot.command()
async def stat(ctx, handle: discord.Member = None):
    if handle is None:
        handle = ctx.author
    user_data = find_or_create_user(handle)
    message = f'{handle.name} Stats:\nName: {handle.display_name}\nPoint: {user_data["point"]}\n' + \
              f'Message Count: {user_data["message_count"]}\nGames Played: '
    if "games_played" in user_data:
        message += ", ".join([f'{game_list[int(key)][0]}: {value}' for key, value in sorted(
                        user_data["games_played"].items(), key=lambda x:x[1], reverse=True)])
    else:
        message += "0"
    message += "\nGames Won: "
    if "games_won" in user_data:
        message += ", ".join([f'{game_list[int(key)][0]}: {value}' for key, value in sorted(
                        user_data["games_won"].items(), key=lambda x:x[1], reverse=True)])
    else:
        message += "0"
    await ctx.channel.send(message)


@bot.command()
async def gamestat(ctx):
    game_data = find_or_create_user(-1)
    message = f'General Info:\nGames Played: '
    if "games_played" in game_data:
        message += ", ".join([f'{game_list[int(key)][0]}: {value}' for key, value in sorted(
                        game_data["games_played"].items(), key=lambda x:x[1], reverse=True)])
    else:
        message += "0"
    await ctx.channel.send(message)


@bot.command()
async def leaderboard(ctx, parameter="point"):
    user_count = 10  # How many user to display
    filtered_list = None
    if parameter.isdigit():
        game_id = parameter
        if int(game_id) < 0 or int(game_id) >= len(game_list):
            ctx.channel.send("That Game ID does not exist!")
            return
        message = f"**{game_list[int(game_id)][0]} Leaderboard**\n"
        filtered_list = collection.find({}, {"name": 1, "games_played": 1, "games_won": 1})
        parsed_dict = {}
        for i in filtered_list:
            if i["name"] == "General Game":
                try:
                    total_played = i["games_played"][game_id]
                except KeyError:
                    total_played = 0
                    message += "No one has played this game yet!"
                    continue
                try:
                    total_won = i["games_won"][game_id]
                except KeyError:
                    total_won = 0
                message += f"Total Games Played: {total_played} | Average Table Size: {round(total_played / total_won, 2)}\n"
                continue

            try:
                games_played = i["games_played"][game_id]
            except KeyError:
                games_played = 0
                continue
            try:
                games_won = i["games_won"][game_id]
            except KeyError:
                games_won = 0
            winrate = round(games_won / games_played * 100, 2)

            parsed_dict[i["name"]] = [games_won, games_played, winrate]
        message += "\n".join([f'{key}: {value[0]} (win) | {value[1]} (played) | Winrate: {value[2]}%' for key, value in sorted(
                                    parsed_dict.items(), key=lambda x:(x[1][0], x[1][2], x[1][1]), reverse=True)[0:user_count]])
        await ctx.channel.send(message)
        return
    if parameter == "point":
        message = "**Point Leaderboard**\n"
        filtered_list = collection.find({}, {"name": 1, "point": 1})
        parsed_dict = {}
        for i in filtered_list:
            if i["name"] == "General Game":
                total_point = i["point"]
                message += f"Total Point: {total_point}\n"
                continue
            parsed_dict[i["name"]] = i["point"]
        message += "\n".join([f'{key}: {value}' for key, value in sorted(
                            parsed_dict.items(), key=lambda x:x[1], reverse=True)[0:user_count]])
    elif parameter == "game" or parameter == "games":
        message = "**Games Leaderboard**\n"
        filtered_list = collection.find({}, {"name": 1, "games_played": 1, "games_won": 1})
        parsed_dict = {}
        for i in filtered_list:
            if i["name"] == "General Game":
                try:
                    total_played = sum(i["games_played"].values())
                except KeyError:
                    total_played = 0
                    message += "No one has played this game yet!"
                    continue
                try:
                    total_won = sum(i["games_played"].values())
                except KeyError:
                    total_won = 0
                message += f"Total Games Played: {total_played} | Average Table Size: {round(total_played / total_won, 2)}\n"
                continue
            try:
                games_played = sum(i["games_played"].values())
            except KeyError:
                games_played = 0
                continue
            try:
                games_won = sum(i["games_won"].values())
            except KeyError:
                games_won = 0
            winrate = round(games_won / games_played * 100, 2)
            parsed_dict[i["name"]] = [games_won, games_played, winrate]
        message += "\n".join([f'{key}: {value[0]} (win) | {value[1]} (played) | Winrate: {value[2]}%' for key, value in sorted(
                            parsed_dict.items(), key=lambda x:(x[1][0], x[1][2], x[1][1]), reverse=True)[0:user_count]])
    await ctx.channel.send(message)


@bot.command()
@commands.has_role("Officer")
async def givepoint(ctx, point: int, members: commands.Greedy[discord.Member]):
    if type(members) == discord.Member:
        increment_attribute(-1, "point", point)
        increment_attribute(members, "point", point)
        return
    for i in range(len(members)):
        increment_attribute(-1, "point", point)
        increment_attribute(members[i], "point", point)
    await ctx.channel.send("Points Awarded")


@bot.command()
@commands.has_role("Officer")
async def recordgame(ctx, game_id: int, members: commands.Greedy[discord.Member]):
    if game_id < 0 or game_id >= len(game_list):
        await ctx.channel.send("That Game ID is invalid!")
        return
    for i in range(len(members)):
        increment_attribute(members[i], f"games_played.{game_id}")
        # Formula for point: int((point / ranking) * (table size / max player count))
        point = int((game_list[game_id][1] / (i+1)) * (len(members) / game_list[game_id][2]))
        await givepoint(ctx, point, members[i])

    increment_attribute(-1, f"games_played.{game_id}")
    increment_attribute(-1, f"games_won.{game_id}", 1 / len(members))
    increment_attribute(members[0], f"games_won.{game_id}")
    await ctx.channel.send("Game Recorded")


@bot.command()
@commands.has_role("Officer")
async def rg(ctx, game_id: int, members: commands.Greedy[discord.Member]):
    await recordgame(ctx, game_id, members)


@bot.command()
@commands.has_role("Officer")
async def changegamesplayed(ctx, game_id: int, member: discord.Member, amount=0):
    if game_id < 0 or game_id >= len(game_list):
        await ctx.channel.send("That Game ID is invalid!")
        return
    if amount == 0:
        await ctx.channel.send("How much do you want to change?")
        return
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
        return
    increment_attribute(member, f"games_won.{game_id}", amount)
    increment_attribute(-1, f"games_won.{game_id}", amount)
    await ctx.channel.send("Data Changed")


bot.run(config['token'])
