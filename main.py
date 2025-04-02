import nextcord
from nextcord.ext import commands
import requests
import os
from dotenv import load_dotenv
from flask import Flask

# Load environment variables
load_dotenv()

# Get Discord Token from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

 Start Flask server to keep Render happy
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

# Get the port from the environment or use 8080
PORT = int(os.getenv("PORT", 8080))

# Roblox-related functionality
class Bypass:
    def __init__(self, cookie: str) -> None:
        self.cookie = cookie

    def start_process(self) -> str:
        self.xcsrf_token = self.get_csrf_token()
        if "Error" in self.xcsrf_token:
            return self.xcsrf_token

        self.rbx_authentication_ticket = self.get_rbx_authentication_ticket()
        if "Error" in self.rbx_authentication_ticket:
            return self.rbx_authentication_ticket

        return self.get_set_cookie()

    def get_set_cookie(self) -> str:
        response = requests.post(
            "https://auth.roblox.com/v1/authentication-ticket/redeem",
            headers={"rbxauthenticationnegotiation": "1"},
            json={"authenticationTicket": self.rbx_authentication_ticket}
        )
        set_cookie_header = response.headers.get("set-cookie")
        if not set_cookie_header:
            return "Error: Unable to retrieve set_cookie."
        return set_cookie_header.split(".ROBLOSECURITY=")[1].split(";")[0]

    def get_rbx_authentication_ticket(self) -> str:
        response = requests.post(
            "https://auth.roblox.com/v1/authentication-ticket",
            headers={
                "rbxauthenticationnegotiation": "1",
                "referer": "https://www.roblox.com/camel",
                "Content-Type": "application/json",
                "x-csrf-token": self.xcsrf_token
            },
            cookies={".ROBLOSECURITY": self.cookie}
        )
        ticket = response.headers.get("rbx-authentication-ticket")
        if not ticket:
            return "Error: Unable to retrieve authentication ticket."
        return ticket

    def get_csrf_token(self) -> str:
        response = requests.post(
            "https://auth.roblox.com/v2/logout", 
            cookies={".ROBLOSECURITY": self.cookie}
        )
        xcsrf_token = response.headers.get("x-csrf-token")
        if not xcsrf_token:
            return "Error: Invalid cookie. Sorry."
        return xcsrf_token

# Discord Bot Setup
intents = nextcord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(
        status=nextcord.Status.dnd, 
        activity=nextcord.Game("WACTHING SAI | !bypass (cookie)")
    )

# Existing bypass command
@bot.command()
async def bypass(ctx, cookie: str):
    if ctx.guild is None:  # Check if the command is used in DMs
        try:
            bypasser = Bypass(cookie)
            result = bypasser.start_process()

            embed = nextcord.Embed()
            if "Error" in result:
                embed.title = "Bypass Failed"
                embed.description = result
                embed.color = nextcord.Color.red()
            else:
                embed.title = "Bypass Successful"
                embed.description = f"{result}"
                embed.color = nextcord.Color.green()

            await ctx.send(embed=embed)
        except Exception as e:
            error_embed = nextcord.Embed(
                title="Error",
                description=str(e),
                color=nextcord.Color.red()
            )
            await ctx.send(embed=error_embed)

# New command: Get Roblox User Info
@bot.command()
async def roblox_user_info(ctx, username: str):
    """Fetch Roblox user info by username"""
    url = f"https://api.roblox.com/users/get-by-username?username={username}"
    response = requests.get(url)

    if response.status_code == 200:
        user_info = response.json()
        if user_info.get("success"):
            embed = nextcord.Embed(title=f"Roblox User Info: {username}")
            embed.add_field(name="User ID", value=user_info["userId"], inline=False)
            embed.add_field(name="Username", value=user_info["username"], inline=False)
            embed.add_field(name="Display Name", value=user_info["displayName"], inline=False)
            embed.add_field(name="Avatar URL", value=user_info["avatarUrl"], inline=False)
            embed.color = nextcord.Color.blue()
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Error: User `{username}` not found.")
    else:
        await ctx.send("Error: Unable to fetch user data.")

# New command: Check if the Roblox account is currently online
@bot.command()
async def roblox_user_online(ctx, username: str):
    """Check if a Roblox user is online"""
    url = f"https://users.roblox.com/v1/users/{username}/status"
    response = requests.get(url)

    if response.status_code == 200:
        user_status = response.json()
        if user_status.get("status") == "Online":
            await ctx.send(f"User `{username}` is currently online!")
        else:
            await ctx.send(f"User `{username}` is not online.")
    else:
        await ctx.send("Error: Unable to fetch user online status.")

# New command: Get Roblox game info
@bot.command()
async def roblox_game_info(ctx, game_id: int):
    """Fetch Roblox game info by game ID"""
    url = f"https://api.roblox.com/marketplace/game-info/{game_id}"
    response = requests.get(url)

    if response.status_code == 200:
        game_info = response.json()
        if game_info.get("success"):
            embed = nextcord.Embed(title=f"Roblox Game Info: {game_id}")
            embed.add_field(name="Game Name", value=game_info["name"], inline=False)
            embed.add_field(name="Game Creator", value=game_info["creator"], inline=False)
            embed.add_field(name="Description", value=game_info["description"], inline=False)
            embed.add_field(name="Visits", value=game_info["visits"], inline=False)
            embed.color = nextcord.Color.green()
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Error: Game with ID `{game_id}` not found.")
    else:
        await ctx.send("Error: Unable to fetch game data.")
        
        # Start Flask server and bot together
if __name__ == "__main__":
    from threading import Thread

    # Start Flask server in a separate thread
    Thread(target=lambda: app.run(host="0.0.0.0", port=PORT)).start()


bot.run(DISCORD_TOKEN)
