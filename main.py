import google.generativeai as genai
import requests
import time
import json
import os

import twitchio
from twitchio.ext import commands
from dotenv import load_dotenv
from gtts import gTTS
from config import *

from utils import get_random_entry

class Jazzica(commands.Bot):
    def __init__(self, twitch_key:str, client_id: str, client_secret: str, gemini_key: str, system_instructions: str):
        super().__init__(token=twitch_key, client_id=client_id, client_secret=client_secret, prefix='!', initial_channels=['mrblackreal'])
        self.gemini_api_key = gemini_key

        genai.configure(api_key=self.gemini_api_key)

        self.personality = system_instructions
        self.brain = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=self.personality)
        self.last_query_time = -1

    async def event_ready(self: commands.Bot):
        print(f"Bot is ready! Logged in as {self.nick}")

    async def event_message(self, message: twitchio.Message):
        print(f"Message received from {message.author.name} ({message.echo}): {message.content}")

        if message.echo:
            return

        # Handle user messages here

        if not (message.channel.name == message.author.name):
            return

        # Handle broadcaster messages here
        
        # if message.content.startswith("!ask "):
        #     query = message.content[5:]
        #     response = await self.get_gemini_response(query)
        #     await message.channel.send(response)

        # # You can add more commands here
        # elif message.content.startswith("!compliment"):
        #     compliment = self.get_compliment(message.author.name)
        #     await message.channel.send(compliment)
        # elif message.content.startswith("!catfact"):
        #     fact = self.get_cat_fact()
        #     await message.channel.send(fact)

    async def get_gemini_response(self, prompt: str):
        current_time = time.time()
        time_since_last_query = current_time - self.last_query_time

        if time_since_last_query < 10:
            return get_random_entry(ratelimit_response)

        self.last_query_time = current_time

        try:
            response = self.brain.generate_content(prompt)
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return "Oops, something went wrong while talking to my brain..."

    def get_compliment(self, username: str) -> str:
        compliments = [
            f"{username}, you're an absolute legend!",
            f"Hey {username}, you're basically the reason the sun shines.",
            f"How does it feel to be the most awesome person in the chat, {username}?",
            f"{username}, if I could give you a high-five, I totally would!",
        ]
        
        return get_random_entry(compliments)

    def get_cat_fact(self) -> str:
        return get_random_entry(cat_facts)


if __name__ == "__main__":
    load_dotenv()

    twitch_key = os.getenv("TWITCH_TOKEN")
    gemini_key = os.getenv("GEMINI_API_KEY")

    twitch_client_id = os.getenv("TWITCH_CLIENT_ID")
    twitch_client_secret = os.getenv("TWITCH_CLIENT_SECRET")

    # url = "https://id.twitch.tv/oauth2/token"

    # payload = f'client_id={twitch_client_id}&client_secret={twitch_client_secret}&grant_type=client_credentials'
    # headers = {
    #     'Content-Type': 'application/x-www-form-urlencoded'
    # }

    # response = requests.request("POST", url, headers=headers, data=payload).json()

    # access_token = response["access_token"]
    # expires_in = json_response["expires_in"] 

    bot = Jazzica(twitch_key=twitch_key, client_id=twitch_client_id, gemini_key=gemini_key, client_secret=twitch_client_secret, system_instructions=system_instruction)
    bot.run()
