import os
import disnake
from disnake.ext import commands
import aiohttp
import traceback

intents = disnake.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

API_URL = "https://api.arizona-five.com/launcher/servers"

@bot.slash_command(description="Показать онлайн и очередь серверов Arizona RP, Mobile и Vice City")
async def online(inter: disnake.ApplicationCommandInteraction):
    await inter.response.defer()

    try:
        async with aiohttp.ClientSession() as session:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            async with session.get(API_URL, headers=headers, timeout=10) as resp:
                text_data = await resp.text()
                if resp.status != 200:
                    await inter.edit_original_response(f"HTTP Ошибка: {resp.status}")
                    return
                data = await resp.json()
    except Exception as e:
        await inter.edit_original_response(f"Ошибка сети/запроса: `{e}`")
        return

    try:
        embed = disnake.Embed(title="📊 Онлайн серверов Arizona RP", color=disnake.Color.gold())
        
        lines_main = []
        lines_mobile = []
        lines_vc = []
        total_players = 0

        # 1. Основные ПК сервера (arizona)
        servers_list = data.get("arizona", [])
        servers_list = sorted(servers_list, key=lambda x: x.get("number", 0))

        for srv in servers_list:
            number = srv.get("number", 0)
            name = srv.get("name", "Неизвестный")
            online_cnt = srv.get("online", 0)
            max_online = srv.get("maxplayers", 1000)
            queue = srv.get("queue", 0)

            total_players += online_cnt
            queue_str = f" `(Очередь: {queue})`" if queue > 0 else ""
            lines_main.append(f"**{name} ({number:02d})**: `{online_cnt}/{max_online}`{queue_str}")

        # 2. Мобильные сервера (arizonaMobile)
        mobile_list = data.get("arizonaMobile", [])
        mobile_list = sorted(mobile_list, key=lambda x: x.get("number", 0))

        for srv in mobile_list:
            number = srv.get("number", 0)
            name = srv.get("name", f"Mobile {number}")
            online_cnt = srv.get("online", 0)
            max_online = srv.get("maxplayers", 1000)
            queue = srv.get("queue", 0)

            total_players += online_cnt
            queue_str = f" `(Очередь: {queue})`" if queue > 0 else ""
            lines_mobile.append(f"📱 **{name}**: `{online_cnt}/{max_online}`{queue_str}")

        # 3. Vice City (vc)
        vc_list = data.get("vc", [])
        for srv in vc_list:
            name = srv.get("name", "Vice City")
            online_cnt = srv.get("online", 0)
            max_online = srv.get("maxplayers", 750)
            queue = srv.get("queue", 0)

            total_players += online_cnt
            queue_str = f" `(Очередь: {queue})`" if queue > 0 else ""
            lines_vc.append(f"🌴 **{name}**: `{online_cnt}/{max_online}`{queue_str}")

        # Раскладываем ПК-сервера на 2 колонки
        half = (len(lines_main) + 1) // 2
        col1 = lines_main[:half]
        col2 = lines_main[half:]

        if col1:
            embed.add_field(name="Сервера (Часть 1)", value="\n".join(col1), inline=True)
        if col2:
            embed.add_field(name="Сервера (Часть 2)", value="\n".join(col2), inline=True)
        
        # Мобильные сервера
        if lines_mobile:
            embed.add_field(name="Мобильные сервера", value="\n".join(lines_mobile), inline=False)

        # Блок Vice City
        if lines_vc:
            embed.add_field(name="Vice City", value="\n".join(lines_vc), inline=False)

        embed.set_footer(text=f"Всего игроков на проекте: {total_players}")
        await inter.edit_original_response(embed=embed)

    except Exception as parse_err:
        err_text = traceback.format_exc()
        await inter.edit_original_response(f"Ошибка парсинга:\n```py\n{err_text[-1500:]}\n```")

token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token)
