import google.generativeai as genai
import requests
import time
import json
import os

from twitchio.ext import commands
from dotenv import load_dotenv
from gtts import gTTS
from config import *

class Jazzica(commands.Bot):
    def __init__(self, twitch_key:str, client_id: str, gemini_key: str, system_instructions: str):
        super().__init__(token=twitch_key, client_id=client_id, prefix='!', initial_channels=['mrblackreal'])
        self.gemini_api_key = gemini_key

        genai.configure(api_key=self.gemini_api_key)

        self.personality = system_instructions
        self.brain = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=self.personality,
        )
        self.last_query_time = -1

    async def event_ready(self):
        print(f"Bot is ready! Logged in as {self.nick}")

    async def event_message(self, message):
        print(f"Message received from {message.author.name} ({message.echo}): {message.content}")

        if message.echo:
            return

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

    async def get_gemini_response(self, prompt):
        current_time = time.time()
        time_since_last_query = current_time - self.last_query_time

        if time_since_last_query < 10:
            return ratelimit_response[time.time() % len(ratelimit_response)]

        self.last_query_time = current_time

        try:
            response = self.brain.generate_content(prompt)
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return "Oops, something went wrong while talking to my brain..."

    def get_compliment(self, username):
        compliments = [
            f"{username}, you're an absolute legend!",
            f"Hey {username}, you're basically the reason the sun shines.",
            f"How does it feel to be the most awesome person in the chat, {username}?",
            f"{username}, if I could give you a high-five, I totally would!",
        ]
        return compliments[time.time() % len(compliments)]

    def get_cat_fact(self):
        return cat_facts[int(time.time()) % len(cat_facts)]

    def text_to_speech(self, text: str):
        try:
            tts = gTTS(text)
            tts.save("response.mp3")
            if os.name == 'nt':  # Windows
                os.system("start response.mp3")
            else:  # For macOS or Linux
                os.system("mpg123 response.mp3")
        except Exception as e:
            print(f"Error with TTS: {e}")
            return "Sorry, I couldn't speak that out loud."

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

    bot = Jazzica(twitch_key=twitch_key, client_id=twitch_client_id, gemini_key=gemini_key, system_instructions=system_instruction)
    bot.run()
