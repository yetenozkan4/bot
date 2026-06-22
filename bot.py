import discord
from discord.ext import commands
import os
import requests

# intents tanımları
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Roblox Rütbe Güncelleme Fonksiyonu
def set_roblox_rank(user_id, group_id, rank_id):
    cookie = os.environ.get("ROBLOX_COOKIE")
    headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
    
    # CSRF Token Al
    try:
        token_req = requests.post("https://auth.roblox.com/v2/login", headers=headers)
        csrf_token = token_req.headers.get("x-csrf-token")
        
        # Rütbe Güncelle (Düzeltilmiş Satır)
        patch_headers = {"Cookie": f".ROBLOSECURITY={cookie}", "x-csrf-token": csrf_token}
        url = f"https://groups.roblox.com/v1/groups/{group_id}/users/{user_id}"
        
        response = requests.patch(url, json={"roleId": rank_id}, headers=patch_headers)
        return response.status_code == 200
    except Exception as e:
        print(f"Hata: {e}")
        return False

@bot.event
async def on_ready():
    print(f"Bot Aktif: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} komut senkronize edildi.")
    except Exception as e:
        print(f"Senkronizasyon hatası: {e}")

@bot.tree.command(name="rütbelendir", description="Kullanıcıya Roblox'ta rütbe verir")
async def rütbelendir(interaction: discord.Interaction, üye_id: str, rütbe_id: int):
    # Basit bir yetki kontrolü (örnek: sadece yöneticiler)
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Yetkiniz yok!", ephemeral=True)
        return
        
    success = set_roblox_rank(üye_id, os.environ.get("GROUP_ID"), rütbe_id)
    
    if success:
        await interaction.response.send_message(f"Başarılı! {üye_id} ID'li kullanıcı güncellendi.")
    else:
        await interaction.response.send_message("Roblox API hatası! Cookie'yi kontrol et.", ephemeral=True)

bot.run(os.environ.get("DISCORD_TOKEN"))
