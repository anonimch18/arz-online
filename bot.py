import os
import disnake
from disnake.ext import commands
import aiohttp

intents = disnake.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

API_URL = "https://api.arizona-five.com/launcher/servers"

@bot.slash_command(description="Показать онлайн и очередь серверов Arizona RP и Vice City")
async def online(inter: disnake.ApplicationCommandInteraction):
    await inter.response.defer()

    try:
        async with aiohttp.ClientSession() as session:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            async with session.get(API_URL, headers=headers, timeout=5) as resp:
                if resp.status != 200:
                    await inter.edit_original_response(f"Ошибка API: статус {resp.status}")
                    return
                data = await resp.json()
    except Exception as e:
        await inter.edit_original_response(f"Ошибка запроса: `{e}`")
        return

    embed = disnake.Embed(title="📊 Онлайн серверов Arizona RP", color=disnake.Color.gold())
    
    lines_main = []
    lines_extra = []
    total_players = 0

    # 1. Собираем основные сервера из ключа "arizona"
    servers_list = data.get("arizona", [])
    servers_list = sorted(servers_list, key=lambda x: x.get("number", 0))

    for srv in servers_list:
        number = srv.get("number", "")
        name = srv.get("name", "Неизвестный")
        online_cnt = srv.get("online", 0)
        max_online = srv.get("maxplayers", 1000)
        queue = srv.get("queue", 0)

        total_players += online_cnt
        queue_str = f" `(Очередь: {queue})`" if queue > 0 else ""
        lines_main.append(f"**{name} ({number:02d})**: `{online_cnt}/{max_online}`{queue_str}")

    # 2. Достаем Vice City из ключа "vc"
    vc_list = data.get("vc", [])
    for srv in vc_list:
        name = srv.get("name", "Vice City")
        online_cnt = srv.get("online", 0)
        max_online = srv.get("maxplayers", 750)
        queue = srv.get("queue", 0)

        total_players += online_cnt
        queue_str = f" `(Очередь: {queue})`" if queue > 0 else ""
        lines_extra.append(f"🌴 **{name}**: `{online_cnt}/{max_online}`{queue_str}")

    # Разделяем основные сервера на две колонки
    half = (len(lines_main) + 1) // 2
    col1 = lines_main[:half]
    col2 = lines_main[half:]

    if col1:
        embed.add_field(name="Сервера (Часть 1)", value="\n".join(col1), inline=True)
    if col2:
        embed.add_field(name="Сервера (Часть 2)", value="\n".join(col2), inline=True)
    
    # Выводим Vice City отдельным блоком внизу
    if lines_extra:
        embed.add_field(name="Специальные / Vice City", value="\n".join(lines_extra), inline=False)

    embed.set_footer(text=f"Всего игроков на проекте: {total_players}")

    await inter.edit_original_response(embed=embed)

token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token)
