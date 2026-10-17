import os
import asyncio
import disnake
from disnake.ext import commands
from samp_client.client import SampClient

intents = disnake.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

SERVERS = {
    "Phoenix (01)":     {"ip": "185.169.134.3",   "port": 7777},
    "Tucson (02)":      {"ip": "185.169.134.4",   "port": 7777},
    "Scottdale (03)":   {"ip": "185.169.134.43",  "port": 7777},
    "Chandler (04)":    {"ip": "185.169.134.44",  "port": 7777},
    "Brainburg (05)":   {"ip": "185.169.134.45",  "port": 7777},
    "Saint-Rose (06)":  {"ip": "185.169.134.5",   "port": 7777},
    "Mesa (07)":        {"ip": "185.169.134.59",  "port": 7777},
    "Red-Rock (08)":    {"ip": "185.169.134.61",  "port": 7777},
    "Yuma (09)":        {"ip": "185.169.134.107", "port": 7777},
    "Surprise (10)":    {"ip": "185.169.134.109", "port": 7777},
    "Prescott (11)":    {"ip": "185.169.134.166", "port": 7777},
    "Glendale (12)":    {"ip": "185.169.134.171", "port": 7777},
    "Kingman (13)":     {"ip": "185.169.134.172", "port": 7777},
    "Winslow (14)":     {"ip": "185.169.134.173", "port": 7777},
    "Payson (15)":      {"ip": "185.169.134.174", "port": 7777},
    "Gilbert (16)":     {"ip": "80.66.82.191",    "port": 7777},
    "Show Low (17)":    {"ip": "80.66.82.190",    "port": 7777},
    "Casa-Grande (18)": {"ip": "80.66.82.188",    "port": 7777},
    "Page (19)":        {"ip": "80.66.82.168",    "port": 7777},
    "Sun-City (20)":    {"ip": "80.66.82.159",    "port": 7777},
    "Queen-Creek (21)": {"ip": "80.66.82.200",    "port": 7777},
    "Sedona (22)":      {"ip": "80.66.82.144",    "port": 7777},
    "Holiday (23)":     {"ip": "80.66.82.132",    "port": 7777},
    "Wednesday (24)":   {"ip": "80.66.82.128",    "port": 7777},
    "Yava (25)":        {"ip": "80.66.82.242",    "port": 7777},
    "Faraway (26)":     {"ip": "80.66.82.87",     "port": 7777},
    "Bumble Bee (27)":  {"ip": "80.66.82.160",    "port": 7777},
    "Christmas (28)":   {"ip": "80.66.82.158",    "port": 7777},
    "Mirage (29)":      {"ip": "80.66.82.115",    "port": 7777},
    "Love (30)":        {"ip": "80.66.82.114",    "port": 7777},
    "Drake (31)":       {"ip": "80.66.82.100",    "port": 7777},
    "Bumble (32)":      {"ip": "80.66.82.99",     "port": 7777}
}

async def fetch_server(name, data):
    """Асинхронный опрос одного сервера с коротковатым таймаутом"""
    def query():
        try:
            with SampClient(address=data["ip"], port=data["port"]) as client:
                info = client.get_server_info()
                return name, info.players, info.max_players
        except Exception:
            return name, None, None

    # Опрашиваем в отдельном потоке с таймаутом 1.5 секунды
    try:
        return await asyncio.wait_for(asyncio.to_thread(query), timeout=1.5)
    except asyncio.TimeoutError:
        return name, None, None

@bot.slash_command(description="Показать онлайн серверов Arizona RP")
async def online(inter: disnake.ApplicationCommandInteraction):
    # Сразу сообщаем дискорду, что ответ готовится (чтобы не вылетал таймаут)
    await inter.response.defer()

    # Запускаем опрос ВСЕХ 32 серверов ОДНОВРЕМЕННО
    tasks = [fetch_server(name, data) for name, data in SERVERS.items()]
    results = await asyncio.gather(*tasks)

    total_players = 0
    total_max = 0
    embed = disnake.Embed(title="📊 Онлайн серверов Arizona RP", color=disnake.Color.blue())

    lines = []
    for name, players, max_players in results:
        if players is not None:
            total_players += players
            total_max += max_players
            lines.append(f"**{name}**: `{players}/{max_players}`")
        else:
            lines.append(f"**{name}**: `Оффлайн`")

    # Разбиваем список на 2 колонки в Embed
    half = len(lines) // 2
    embed.add_field(name="Сервера 1-16", value="\n".join(lines[:half]), inline=True)
    embed.add_field(name="Сервера 17-32", value="\n".join(lines[half:]), inline=True)
    embed.set_footer(text=f"Всего игроков: {total_players} / {total_max}")

    await inter.edit_original_response(embed=embed)

token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token)
