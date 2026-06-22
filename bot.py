import discord
from discord.ext import commands
from pymongo import MongoClient
import os
import requests

# MongoDB Bağlantısı
client = MongoClient(os.environ.get("MONGO_URI"))
db = client[os.environ.get("DB_NAME", "omniraai")]
users_col = db["users"]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Roblox Rütbe Değiştirme Fonksiyonu
def set_roblox_rank(user_id, group_id, rank_id):
    cookie = os.environ.get("ROBLOX_COOKIE")
    headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
    
    # CSRF Token Al
    try:
        token_req = requests.post("https://auth.roblox.com/v2/login", headers=headers)
        csrf_token = token_req.headers.get("x-csrf-token")
        
        # Rütbe Güncelle (PATCH)
        patch_headers = {"Cookie": f".ROBLOSECURITY={cookie}", "x-csrf-token": csrf_token}
        url = f"https://groups.roblox.com/v1/groups/{group_id}/users/{user_id}"
        response = requests.patch(url, json={"roleId": rank_id}, headers=headers=patch_headers)
        return response.status_code == 200
    except:
        return False

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot Aktif: {bot.user}")

@bot.tree.command(name="rütbelendir", description="Kullanıcıya Roblox'ta rütbe verir")
async def rütbelendir(interaction: discord.Interaction, üye: discord.Member, rütbe_id: int):
    # Veritabanından yetkili ve hedef kullanıcıyı çek
    actor = users_col.find_one({"discord_id": str(interaction.user.id)})
    target = users_col.find_one({"discord_id": str(üye.id)})
    
    if not actor or not target:
        await interaction.response.send_message("Kayıtlı kullanıcı bulunamadı!", ephemeral=True)
        return

    # Hiyerarşi Kontrolü (Sadece 255 olanlar veya rütbesi yüksek olanlar)
    if actor.get("roblox_rank_id", 0) < 254:
        await interaction.response.send_message("Bu işlemi yapmak için yeterli yetkiniz yok!", ephemeral=True)
        return
        
    # Roblox API'yi çalıştır
    success = set_roblox_rank(target["roblox_id"], os.environ.get("GROUP_ID"), rütbe_id)
    
    if success:
        users_col.update_one({"discord_id": str(üye.id)}, {"$set": {"roblox_rank_id": rütbe_id}})
        await interaction.response.send_message(f"Başarılı! {üye.display_name} rütbesi güncellendi.")
    else:
        await interaction.response.send_message("Roblox API hatası! Cookie geçerliliğini kontrol et.", ephemeral=True)

bot.run(os.environ.get("DISCORD_TOKEN"))
