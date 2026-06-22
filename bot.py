import discord
from discord.ext import commands
import os
import requests

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def set_roblox_rank(user_id, group_id, rank_id):
    cookie = os.environ.get("ROBLOX_COOKIE")
    if not cookie:
        return False, "ROBLOX_COOKIE ayarlanmamış!"
        
    headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
    
    try:
        # CSRF Token al
        token_req = requests.post("https://auth.roblox.com/v2/login", headers=headers)
        csrf_token = token_req.headers.get("x-csrf-token")
        
        if not csrf_token:
            return False, "CSRF Token alınamadı (Cookie geçersiz olabilir)."
            
        # Rütbe güncelle
        patch_headers = {
            "Cookie": f".ROBLOSECURITY={cookie}", 
            "x-csrf-token": csrf_token,
            "Content-Type": "application/json"
        }
        url = f"https://groups.roblox.com/v1/groups/{group_id}/users/{user_id}"
        
        response = requests.patch(url, json={"roleId": rank_id}, headers=patch_headers)
        
        if response.status_code == 200:
            return True, "Başarılı!"
        else:
            return False, f"Hata: {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, str(e)

@bot.event
async def on_ready():
    print(f"Bot Aktif: {bot.user}")
    await bot.tree.sync()

@bot.tree.command(name="rütbelendir", description="ID ile rütbe ver")
async def rütbelendir(interaction: discord.Interaction, kullanıcı_id: str, rütbe_id: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Yönetici değilsin!", ephemeral=True)
        return
        
    await interaction.response.defer()
    
    success, message = set_roblox_rank(kullanıcı_id, os.environ.get("GROUP_ID"), rütbe_id)
    
    if success:
        await interaction.followup.send(f"✅ İşlem Tamamlandı: {message}")
    else:
        await interaction.followup.send(f"❌ İşlem Başarısız: {message}")

bot.run(os.environ.get("DISCORD_TOKEN"))
