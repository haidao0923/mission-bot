# [Name, Points (play time * 10), Recommended Table Size]
# Formula for point: int((point / ranking) * (table size / recommended table size))
# As such, point should be calculated based on estimated time given full table
from enum import Enum
class GameType(Enum):
    ONE_WINNER = "1 Winner"
    MULTIPLE_WINNER = "Multiple Winners"

game_list = [["Other Games",0,GameType.MULTIPLE_WINNER],["Card Games",0,GameType.MULTIPLE_WINNER],["7 Wonders",70,GameType.ONE_WINNER],
             ["Above and Below",300,GameType.ONE_WINNER],["Acquire",225,GameType.ONE_WINNER],["Article 27",50,GameType.ONE_WINNER],
             ["Avalon: The Resistance",40,GameType.MULTIPLE_WINNER],["Battle Line",150,GameType.ONE_WINNER],["Bears vs. Babies",50,GameType.ONE_WINNER],
             ["Betrayal at House on the Hill",120,GameType.MULTIPLE_WINNER],["Blue Moon City",135,GameType.ONE_WINNER],["Bora Bora",250,GameType.ONE_WINNER],
             ["Brass",250,GameType.ONE_WINNER],["Carcassone",150,GameType.ONE_WINNER],["Cashflow 101",450,GameType.ONE_WINNER],
             ["Catan",250,GameType.ONE_WINNER],["Caverna",300,GameType.ONE_WINNER],["Civilization",325,GameType.ONE_WINNER],
             ["Clank",150,GameType.ONE_WINNER],["Codenames: Picture",35,GameType.MULTIPLE_WINNER],["Concept",70,GameType.MULTIPLE_WINNER],
             ["Cosmic Encounter",200,GameType.MULTIPLE_WINNER],["Coup",25,GameType.ONE_WINNER],["Cyclades",225,GameType.ONE_WINNER],
             ["Dead of Winter",250,GameType.ONE_WINNER],["Defenders of the Realm",225,GameType.MULTIPLE_WINNER],["Descent: Journeys in the Dark",250,GameType.MULTIPLE_WINNER],
             ["Dominion",80,GameType.ONE_WINNER],["Dune: Imperium",330,GameType.ONE_WINNER],["Elder Sign",225,GameType.MULTIPLE_WINNER],
             ["Fantasy Realms",30,GameType.ONE_WINNER],["Firefly: The Game",600,GameType.ONE_WINNER],["Formula D",120,GameType.ONE_WINNER],
             ["Gaia Project",400,GameType.ONE_WINNER],["Galaxy Trucker",150,GameType.ONE_WINNER],["Ghost Stories",150,GameType.MULTIPLE_WINNER],
             ["Globalization",150,GameType.ONE_WINNER],["Glory to Rome",200,GameType.ONE_WINNER],["Great Western Trail",400,GameType.ONE_WINNER],
             ["Harry Potter: Hogwarts Battle",150,GameType.MULTIPLE_WINNER],["Industrial Waste",200,GameType.ONE_WINNER],["Jaipur",150,GameType.ONE_WINNER],
             ["Just One",100,GameType.MULTIPLE_WINNER],["Kanagawa",110,GameType.ONE_WINNER],["Kemet",300,GameType.ONE_WINNER],
             ["King of Tokyo",75,GameType.ONE_WINNER],["Kingdom Builder",120,GameType.ONE_WINNER],["Kumo Hogosha",150,GameType.ONE_WINNER],
             ["Le Havre",400,GameType.ONE_WINNER],["Liar's Dice",50,GameType.ONE_WINNER],["Lords of Waterdeep",340,GameType.ONE_WINNER],
             ["Mascarade",50,GameType.ONE_WINNER],["Memoir '44",150,GameType.MULTIPLE_WINNER],["Monopoly",300,GameType.ONE_WINNER],
             ["Modern Art",120,GameType.ONE_WINNER],["Munchkin",225,GameType.ONE_WINNER],["New York 1901",150,GameType.ONE_WINNER],
             ["Once Upon a Time",75,GameType.ONE_WINNER],["Orleans",225,GameType.ONE_WINNER],["Pandemic",120,GameType.MULTIPLE_WINNER],
             ["Power Grid",300,GameType.ONE_WINNER],["Puerto Rico",300,GameType.ONE_WINNER],["Qwirkle",110,GameType.ONE_WINNER],
             ["Race for the Galaxy",150,GameType.ONE_WINNER],["Railway Express",150,GameType.ONE_WINNER],["Red Rising",150,GameType.ONE_WINNER],
             ["Resident Evil",100,GameType.ONE_WINNER],["Roll for the Galaxy",150,GameType.ONE_WINNER],["Rummikub",100,GameType.ONE_WINNER],
             ["Runewars",550,GameType.ONE_WINNER],["Sagrada",90,GameType.ONE_WINNER],["Santorini",100,GameType.MULTIPLE_WINNER],
             ["Scattergories",75,GameType.ONE_WINNER],["Scythe",250,GameType.ONE_WINNER],["Secret Hitler",50,GameType.MULTIPLE_WINNER],
             ["Small World",200,GameType.ONE_WINNER],["Space Alert",75,GameType.MULTIPLE_WINNER],["Spirit Island",450,GameType.MULTIPLE_WINNER],
             ["Splendor",100,GameType.ONE_WINNER],["StarCraft",600,GameType.ONE_WINNER],["Steampunk Rally",150,GameType.ONE_WINNER],
             ["Steam Works",340,GameType.ONE_WINNER],["Stone Age",225,GameType.ONE_WINNER],["Sushi Go Party!",50,GameType.ONE_WINNER],
             ["Terraforming Mars",400,GameType.ONE_WINNER],["The Castle of Burgundy",300,GameType.ONE_WINNER],["The Office",150,GameType.ONE_WINNER],
             ["Through the Ages",400,GameType.ONE_WINNER],["Ticket to Ride Europe",150,GameType.ONE_WINNER],["Tokaido",120,GameType.ONE_WINNER],
             ["Tsuro",30,GameType.ONE_WINNER],["Twilight Imperium",840,GameType.ONE_WINNER],["Twilight Struggle: The Cold War",750,GameType.ONE_WINNER],
             ["Tzolk'in: The Mayan Calendar",225,GameType.ONE_WINNER],["Viticulture",240,GameType.ONE_WINNER],["War of the Ring",800,GameType.ONE_WINNER],
             ["Wingspan",200,GameType.ONE_WINNER],["XCOM",300,GameType.MULTIPLE_WINNER]]

