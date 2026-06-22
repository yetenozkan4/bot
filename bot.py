import discord
from discord.ext import commands
import os
import requests

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def set_roblox_rank(user_id, group_id, rank_id):
    cookie = os.environ.get("ROBLOX_COOKIE")
    if not cookie:
        return False, "ROBLOX_COOKIE bulunamadı!"

    # Session başlatıyoruz (Cookie ve CSRF takibi için)
    session = requests.Session()
    session.headers.update({"Cookie": f".ROBLOSECURITY={cookie}"})

    try:
        # 1. CSRF Token al
        # Roblox auth endpoint'ine boş bir post atarak token alıyoruz
        token_req = session.post("https://auth.roblox.com/v2/login")
        csrf_token = token_req.headers.get("x-csrf-token")
        
        if not csrf_token:
            return False, "CSRF Token alınamadı. Cookie süresi dolmuş veya hatalı!"

        # 2. Rütbe güncelleme isteği
        patch_headers = {
            "x-csrf-token": csrf_token,
            "Content-Type": "application/json"
        }
        url = f"https://groups.roblox.com/v1/groups/{group_id}/users/{user_id}"
        
        # Patch isteği
        response = session.patch(url, json={"roleId": rank_id}, headers=patch_headers)
        
        if response.status_code == 200:
            return True, "Başarıyla rütbelendirildi!"
        else:
            return False, f"Hata {response.status_code}: {response.text}"

    except Exception as e:
        return False, f"Teknik hata: {str(e)}"

@bot.event
async def on_ready():
    print(f"Bot Aktif: {bot.user}")
    await bot.tree.sync()

@bot.tree.command(name="rütbelendir", description="Kullanıcıya ID ile rütbe verir")
async def rütbelendir(interaction: discord.Interaction, kullanıcı_id: str, rütbe_id: int):
    # Yetki kontrolü
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Buna yetkin yok!", ephemeral=True)
        return
        
    await interaction.response.defer()
    
    success, message = set_roblox_rank(kullanıcı_id, os.environ.get("GROUP_ID"), rütbe_id)
    
    if success:
        await interaction.followup.send(f"✅ {message}")
    else:
        await interaction.followup.send(f"❌ {message}")

bot.run(os.environ.get("DISCORD_TOKEN"))
