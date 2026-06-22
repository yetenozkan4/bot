import discord
from discord.ext import commands
from pymongo import MongoClient
import os

# --- AYARLAR ---
MONGO_URI = os.environ.get("MONGO_URI") # Render'da Environment kısmına eklemeyi unutma
client = MongoClient(MONGO_URI)
db = client["omniraai"] # Aynı veritabanı
users_col = db["users"]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot aktif: {bot.user}")

# --- KULLANICI YENİLE KOMUTU ---
@bot.command()
async def kullanıcıyenile(ctx):
    # Kullanıcıyı veritabanına kaydeden veya güncelleyen mantık buraya gelecek
    # Örnek: ctx.author.nick üzerinden Roblox verisini çekme
    await ctx.send("Kullanıcı verileri yenileniyor...")

@bot.command()
async def rütbelendir(ctx, üye: discord.Member, rütbe_id: int, *, sebep: str):
    # Yetki kontrolü ve Roblox API isteği buraya gelecek
    await ctx.send(f"{üye.display_name} kullanıcısına {rütbe_id} rütbesi veriliyor. Sebep: {sebep}")

# Bot Tokenini Render'da "DISCORD_TOKEN" olarak ekle
bot.run(os.environ.get("DISCORD_TOKEN"))
