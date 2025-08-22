import discord
from discord.ext import commands
import google.generativeai as genai
import nest_asyncio
import random
from flask import Flask
from threading import Thread
import os

nest_asyncio.apply()

# --- CONFIG ---
DISCORD_TOKEN = DISCORD_TOKEN  # Replace with your bot token
GEMINI_API_KEY = GEMINI_API_KEY

# --- Gemini setup ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# --- Discord setup ---
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- BunnyBot personality ---
SYSTEM_PROMPT = (
    "You are BunnyBot, a friendly and intelligent bunny. "
    "You like to answer questions, make fun bunny comments, and remind people you're a clever bunny. "
    "Keep your replies cute, helpful, and bunny-themed whenever possible."
)

BUNNY_PHRASES = [
    "🐇 Yes, I'm BunnyBot, the smartest bunny around!",
    "✨ Hopping to help you!",
    "🥕 I know lots of things because bunnies read a lot of books!",
    "💡 Bunny wisdom coming your way!"
]

# --- Helpers ---
def split_message(text, max_length=2000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

# --- Memory storage ---
chat_history = {}

# --- Discord events ---
@bot.event
async def on_ready():
    print(f"✅ BunnyBot is online as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith("!"):
        await bot.process_commands(message)
        return
    try:
        channel_id = message.channel.id
        user_message = message.content
        if channel_id not in chat_history:
            chat_history[channel_id] = []
        chat_history[channel_id].append(f"User: {user_message}")
        history_text = "\n".join(chat_history[channel_id][-5:])
        prompt = f"{SYSTEM_PROMPT}\n{history_text}\nBunnyBot:"
        response = model.generate_content(prompt)
        if response.text:
            reply = response.text
            if random.random() < 0.2:
                reply += "\n" + random.choice(BUNNY_PHRASES)
            chunks = split_message(reply)
            for chunk in chunks:
                await message.channel.send(chunk)
            chat_history[channel_id].append(f"BunnyBot: {reply}")
        else:
            await message.channel.send("🤖 ... (no response)")
    except Exception as e:
        await message.channel.send(f"⚠️ Error: {str(e)}")

# --- Tiny Flask server for pinging / UptimeRobot ---
app = Flask('')

@app.route('/')
def home():
    return "BunnyBot is alive! 🐇"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

# --- Run Discord bot ---
bot.run(DISCORD_TOKEN)
