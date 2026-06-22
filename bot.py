import discord
from discord.ext import commands
import os
import requests

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# RÜTBE LİSTESİ: Kendi grubuna göre burayı düzenle
ROBLOX_ROLES = [
    discord.SelectOption(label="Üye", value="1"), # Value kısmına Roblox'taki rol ID'sini yaz
    discord.SelectOption(label="Yetkili", value="2"),
    discord.SelectOption(label="Yönetici", value="3")
]

def set_roblox_rank(user_id, group_id, rank_id):
    cookie = os.environ.get("ROBLOX_COOKIE")
    headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
    try:
        token_req = requests.post("https://auth.roblox.com/v2/login", headers=headers)
        csrf_token = token_req.headers
