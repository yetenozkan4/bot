import discord
from discord.ext import commands
from pymongo import MongoClient
import os
import requests

# MongoDB Ayarları
client = MongoClient(os.environ.get("MONGO_URI"))
db = client[os.environ.get("DB_NAME", "omniraai")]
users_col = db["users"]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Hiyerarşi Kontrolü
def can_promote(actor_rank, target_rank):
    if actor_rank == 255: return True # Süper Admin
    return actor_rank > target_rank    # Kendinden düşük olanlara işlem yapar

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot aktif: {bot.user}")

@bot.tree.command(name="kullanıcıyenile", description="Roblox bilgilerini veritabanına kaydeder")
async def kullanıcıyenile(interaction: discord.Interaction, üye: discord.Member):
    roblox_name = üye.nick if üye.nick else üye.name
    
    # Roblox ID Çekme
    res = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [roblox_name]}).json()
    if not res.get("data"):
        await interaction.response.send_message("Roblox kullanıcısı bulunamadı!", ephemeral=True)
        return
        
    roblox_id = res["data"][0]["id"]
    
    # MongoDB Güncelleme
    users_col.update_one(
        {"discord_id": str(üye.id)}, 
        {"$set": {"roblox_id": roblox_id, "roblox_username": roblox_name}}, 
        upsert=True
    )
    await interaction.response.send_message(f"{üye.display_name} kullanıcısı veritabanına işlendi (ID: {roblox_id}).")

@bot.tree.command(name="rütbelendir", description="Kullanıcıya rütbe atar (Yetki kontrollü)")
async def rütbelendir(interaction: discord.Interaction, üye: discord.Member, yeni_rütbe_id: int, sebep: str):
    # Yetkili ve Hedef verilerini çek
    actor = users_col.find_one({"discord_id": str(interaction.user.id)})
    target = users_col.find_one({"discord_id": str(üye.id)})
    
    if not actor or not target:
        await interaction.response.send_message("Kullanıcılar sistemde kayıtlı değil!", ephemeral=True)
        return

    if not can_promote(actor.get("roblox_rank_id", 0), target.get("roblox_rank_id", 0)):
        await interaction.response.send_message("Yetkiniz bu kullanıcıya rütbe vermeye yetmiyor!", ephemeral=True)
        return
        
    # İşlem başarılı mesajı (Buraya Roblox API PATCH isteği eklenecek)
    await interaction.response.send_message(f"İşlem başarılı! {üye.display_name} -> ID: {yeni_rütbe_id}. Sebep: {sebep}")

bot.run(os.environ.get("DISCORD_TOKEN"))
