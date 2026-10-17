import os
import disnake
from disnake.ext import commands
import aiohttp

intents = disnake.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

API_URL = "https://api.arizona-five.com/launcher/servers"

@bot.slash_command(description="Показать онлайн и очередь серверов Arizona RP")
async def online(inter: disnake.ApplicationCommandInteraction):
    await inter.response.defer()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, timeout=5) as resp:
                if resp.status != 200:
                    await inter.edit_original_response("Ошибка получения данных от API Arizona RP.")
                    return
                data = await resp.json()
    except Exception as e:
        await inter.edit_original_response(f"Не удалось подключиться к API: {e}")
        return

    embed = disnake.Embed(title="📊 Онлайн серверов Arizona RP", color=disnake.Color.gold())
    
    lines_main = []
    lines_extra = []
    total_players = 0

    # Разбираем массив серверов из API
    servers_list = data if isinstance(data, list) else data.get("servers", [])

    for srv in servers_list:
        name = srv.get("title") or srv.get("name") or "Неизвестный"
        online_cnt = srv.get("online", 0)
        max_online = srv.get("maxOnline", 1000)
        queue = srv.get("queue", srv.get("waitQueue", 0))

        total_players += online_cnt

        queue_str = f" `(Очередь: {queue})`" if queue > 0 else ""
        formatted_line = f"**{name}**: `{online_cnt}/{max_online}`{queue_str}"

        # Отделяем Vice City или мобильные сервера от основных
        if "Vice" in name or "VC" in name:
            lines_extra.append(formatted_line)
        else:
            lines_main.append(formatted_line)

    # Разбиваем список на 2 столбца
    half = (len(lines_main) + 1) // 2
    col1 = lines_main[:half]
    col2 = lines_main[half:]

    if col1:
        embed.add_field(name="Сервера (Часть 1)", value="\n".join(col1), inline=True)
    if col2:
        embed.add_field(name="Сервера (Часть 2)", value="\n".join(col2), inline=True)
    if lines_extra:
        embed.add_field(name="Специальные / Vice City", value="\n".join(lines_extra), inline=False)

    embed.set_footer(text=f"Всего игроков на проекте: {total_players}")

    await inter.edit_original_response(embed=embed)

token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token)
