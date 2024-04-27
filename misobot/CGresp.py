from revChatGPT.V1 import AsyncChatbot
from revChatGPT.V3 import Chatbot
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
import os

load_dotenv()
OPENAI_EMAIL = os.getenv("OPENAI_EMAIL")
OPENAI_PASSWORD = os.getenv("OPENAI_PASSWORD")
SESSION_TOKEN = os.getenv("SESSION_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ENGINE = os.getenv("OPENAI_ENGINE")
CHAT_MODEL = os.getenv("CHAT_MODEL")

if CHAT_MODEL ==  "UNOFFICIAL":
    unofficial_chatbot = AsyncChatbot(config={"email":OPENAI_EMAIL, "password":OPENAI_PASSWORD, "session_token":SESSION_TOKEN})
elif CHAT_MODEL == "OFFICIAL":
    offical_chatbot = Chatbot(api_key=OPENAI_API_KEY, engine=ENGINE)
    offical_chatbot_gpt4 = Chatbot(api_key=OPENAI_API_KEY, engine='gpt-4-1106-preview')

async def official_handle_response(message) -> str:
    responseMessage = await sync_to_async(offical_chatbot.ask)(message)
    return responseMessage

async def gpt4_handle_response(message) -> str:
    responseMessage = await sync_to_async(offical_chatbot_gpt4.ask)(message)
    return responseMessage

async def unofficial_handle_response(message) -> str:
    async for response in unofficial_chatbot.ask(message):
        responseMessage = response["message"]

    return responseMessage