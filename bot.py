import os
import disnake
from disnake.ext import commands, tasks
from samp_query_parser import SampClient

bot = commands.Bot(command_prefix="!", intents=disnake.Intents.default())

# Актуальный словарь IP и портов всех 32 серверов Arizona RP
SERVERS = {
    "Phoenix (01)":      {"ip": "185.169.134.3",   "port": 7777},
    "Tucson (02)":       {"ip": "185.169.134.4",   "port": 7777},
    "Scottdale (03)":    {"ip": "185.169.134.43",  "port": 7777},
    "Chandler (04)":     {"ip": "185.169.134.44",  "port": 7777},
    "Brainburg (05)":    {"ip": "185.169.134.45",  "port": 7777},
    "Saint-Rose (06)":   {"ip": "185.169.134.5",   "port": 7777},
    "Mesa (07)":         {"ip": "185.169.134.59",  "port": 7777},
    "Red-Rock (08)":     {"ip": "185.169.134.61",  "port": 7777},
    "Yuma (09)":         {"ip": "185.169.134.107", "port": 7777},
    "Surprise (10)":     {"ip": "185.169.134.109", "port": 7777},
    "Prescott (11)":     {"ip": "185.169.134.166", "port": 7777},
    "Glendale (12)":     {"ip": "185.169.134.171", "port": 7777},
    "Kingman (13)":      {"ip": "185.169.134.172", "port": 7777},
    "Winslow (14)":      {"ip": "185.169.134.173", "port": 7777},
    "Payson (15)":       {"ip": "185.169.134.174", "port": 7777},
    "Gilbert (16)":      {"ip": "80.66.82.191",    "port": 7777},
    "Show Low (17)":     {"ip": "80.66.82.190",    "port": 7777},
    "Casa-Grande (18)":  {"ip": "80.66.82.188",    "port": 7777},
    "Page (19)":         {"ip": "80.66.82.168",    "port": 7777},
    "Sun-City (20)":     {"ip": "80.66.82.159",    "port": 7777},
    "Queen-Creek (21)":  {"ip": "80.66.82.200",    "port": 7777},
    "Sedona (22)":       {"ip": "80.66.82.144",    "port": 7777},
    "Holiday (23)":      {"ip": "80.66.82.132",    "port": 7777},
    "Wednesday (24)":    {"ip": "80.66.82.128",    "port": 7777},
    "Yava (25)":         {"ip": "80.66.82.113",    "port": 7777},
    "Faraway (26)":      {"ip": "80.66.82.82",     "port": 7777},
    "Bumble Bee (27)":   {"ip": "80.66.82.87",     "port": 7777},
    "Christmas (28)":    {"ip": "80.66.82.54",     "port": 7777},
    "Mirage (29)":       {"ip": "80.66.82.39",     "port": 7777},
    "Love (30)":         {"ip": "80.66.82.33",     "port": 7777},
    "Drake (31)":        {"ip": "80.66.82.22",     "port": 7777},
    "Home (32)":         {"ip": "80.66.82.235",    "port": 7777},
}

def get_server_info(ip: str, port: int):
    try:
        client = SampClient(address=ip, port=port)
        info = client.get_server_info()
        
        players = info.players
        max_players = info.max_players
        
        queue = 0
        if players >= max_players:
            queue = players - max_players
            
        return {
            "online": True,
            "players": players,
            "max_players": max_players,
            "queue": queue
        }
    except Exception:
        return {"online": False, "players": 0, "max_players": 0, "queue": 0}

@bot.event
async def on_ready():
    print(f"✅ Бот {bot.user} успешно запущен!")
    update_online.start()

@tasks.loop(seconds=30)
async def update_online():
    data = get_server_info(SERVERS["Casa-Grande (18)"]["ip"], SERVERS["Casa-Grande (18)"]["port"])
    if data["online"]:
        status_text = f"Casa-Grande: {data['players']}/{data['max_players']}"
        if data["queue"] > 0:
            status_text += f" (Оч: {data['queue']})"
        await bot.change_presence(activity=disnake.Game(name=status_text))

@bot.slash_command(name="online", description="Показать онлайн и очередь серверов Arizona RP")
async def online(inter: disnake.ApplicationCommandInteraction):
    await inter.response.defer()
    
    embed = disnake.Embed(
        title="📊 Мониторинг серверов Arizona RP",
        color=0xFFD700
    )
    
    for name, addr in SERVERS.items():
        data = get_server_info(addr["ip"], addr["port"])
        if data["online"]:
            if data["queue"] > 0:
                status = f"🟢 `{data['players']}/{data['max_players']}` | ⏳ **+{data['queue']}**"
            else:
                status = f"🟢 `{data['players']}/{data['max_players']}`"
        else:
            status = "🔴 `Недоступен`"
            
        embed.add_field(name=name, value=status, inline=True)
        
    embed.set_footer(text="Gasparov Empire • Direct SAMP Query")
    await inter.edit_original_message(embed=embed)

# Безопасный запуск через токен из Secrets
token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("❌ Ошибка: DISCORD_TOKEN не найден в переменных окружения!")