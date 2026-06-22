import discord
from discord.ext import commands
import os
import requests

# Intents tanımları (Gerekli izinler açık)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def set_roblox_rank(user_id, group_id, rank_id):
    cookie = os.environ.get("ROBLOX_COOKIE")
    if not cookie:
        print("KRİTİK HATA: ROBLOX_COOKIE bulunamadı!")
        return False
        
    headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
    
    try:
        # Roblox API'den X-CSRF-TOKEN alma
        token_req = requests.post("https://auth.roblox.com/v2/login", headers=headers)
        csrf_token = token_req.headers.get("x-csrf-token")
        
        if not csrf_token:
            print(f"HATA: CSRF Token alınamadı. Cookie süresi dolmuş olabilir. Response: {token_req.text}")
            return False
            
        # Rütbe güncelleme işlemi
        patch_headers = {
            "Cookie": f".ROBLOSECURITY={cookie}", 
            "x-csrf-token": csrf_token,
            "Content-Type": "application/json"
        }
        url = f"https://groups.roblox.com/v1/groups/{group_id}/users/{user_id}"
        
        response = requests.patch(url, json={"roleId": rank_id}, headers=patch_headers)
        
        if response.status_code == 200:
            return True
        else:
            print(f"HATA: Roblox API isteği başarısız. Durum Kodu: {response.status_code}, Cevap: {response.text}")
            return False
            
    except Exception as e:
        print(f"HATA: Beklenmedik teknik hata: {e}")
        return False

@bot.event
async def on_ready():
    print(f"Bot Başarıyla Aktif: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} adet komut senkronize edildi.")
    except Exception as e:
        print(f"Senkronizasyon hatası: {e}")

@bot.tree.command(name="rütbelendir", description="Kullanıcıya Roblox'ta rütbe verir")
async def rütbelendir(interaction: discord.Interaction, üye_id: str, rütbe_id: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Bu komutu kullanmak için yönetici yetkiniz yok!", ephemeral=True)
        return
        
    await interaction.response.defer() # Uzun sürebileceği için bekleme mesajı gönder
    
    success = set_roblox_rank(üye_id, os.environ.get("GROUP_ID"), rütbe_id)
    
    if success:
        await interaction.followup.send(f"✅ Başarılı! {üye_id} ID'li kullanıcı {rütbe_id} rütbesine atandı.")
    else:
        await interaction.followup.send("❌ Roblox API hatası oluştu. Lütfen logları kontrol et.")

bot.run(os.environ.get("DISCORD_TOKEN"))
