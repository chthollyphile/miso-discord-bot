import aiohttp
import google.generativeai as genai
from google.generativeai.types import generation_types
import os
import re
import discord
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(".env"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MAX_HISTORY = int(os.getenv("GEMINI_MAX_HISTORY"))

# Configure the generative AI model
genai.configure(api_key=GEMINI_API_KEY)
text_generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}
image_generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]
text_model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=text_generation_config,
    safety_settings=safety_settings,
)
image_model = genai.GenerativeModel(
    model_name="gemini-pro-vision",
    generation_config=image_generation_config,
    safety_settings=safety_settings,
)

def trim_history(chat: genai.ChatSession, override=None):
    max_history = GEMINI_MAX_HISTORY or override 
    if len(chat.history) > max_history:
        chat.history = chat.history[-max_history:]


class ChatManager:
    """gemini会话管理器

    管理类 - 创建不同的gemini会话

    使用示例
    .. code-block:: python

        manager = ChatManager()

        chat = manager.start_session()
        chat_123 = manager.start_session(user_id="user123")

        # ChatManager().start_session()返回一个 genai.ChatSession 对象，因此可以直接使用
        response1 = chat.send_message("What is the weather today?")
        response_123 = chat_123.send_message("Hello.")
        
        # 或者，也可以使用 ChatManager().send_message(user_id, message), 效果相同
        response_123 = manager.send_message(user_id="user123","What is the weather today?")        

        print(response1.text)

    """    
    def __init__(self) -> None:
        self.sessions: dict[str, genai.ChatSession] = {}

    def start_session(self,user_id="owner") -> genai.ChatSession:
        chat = text_model.start_chat(history=[])
        self.sessions[user_id] = chat
        return chat
    
    def select_session(self, user_id: str) -> genai.ChatSession:
        if user_id in self.sessions:
            return self.sessions[user_id]
        else:
            raise ValueError("No session found for the specified user id.")

    def send_message(self, user_id: str, message: str) -> generation_types.GenerateContentResponse:
        session = self.select_session(user_id)
        return session.send_message(message)

    def clear_history(self, user_id: str):
        session = self.select_session(user_id)
        session.history.clear()

chats = ChatManager()
chat = chats.start_session()

async def handle_vision(
    message: discord.Interaction,
    attachment: discord.Attachment,
    user_message: str | None,
) -> str:
    cleaned_text = None
    if user_message:
        cleaned_text = clean_discord_message(user_message)
    if any(
        attachment.filename.lower().endswith(ext)
        for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]
    ):
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                if resp.status != 200:
                    return "无法获取该图片，可能是网络问题"

                image_data = await resp.read()
                response_text = await generate_response_with_image_and_text(
                    image_data, cleaned_text
                )
                return response_text


async def handle_response(message: discord.Interaction, user_message: str) -> str:
    cleaned_text = clean_discord_message(user_message)
    if cleaned_text == "RESET":
        chat.history.clear()
        return "> **RESET: Gemini会话已重置**"
    if GEMINI_MAX_HISTORY == 0:
        responseMessage = await generate_response_with_single_text(cleaned_text)
        return responseMessage
    responseMessage = await generate_response_with_texts(cleaned_text)
    return responseMessage

async def generate_response_with_texts(message_text) -> str:
    prompt_parts = [message_text]
    response = chat.send_message(prompt_parts)
    if response._error:
        print(response._error)
        return "> **Error: Gemini API 响应错误**"
    trim_history(chat,150)
    return response.text


async def generate_response_with_single_text(message_text) -> str:
    prompt_parts = [message_text]
    # print("Got textPrompt: " + message_text)
    response = text_model.generate_content(prompt_parts)
    if response._error:
        print(response._error)
        return "> **Error: Gemini API 响应错误**"
    return response.text


async def generate_response_with_image_and_text(image_data, text):
    image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
    prompt_parts = [
        image_parts[0],
        f"\n{text if text else '请用中文描述这张图片的内容，要求尽可能详细，并给出一些独特的见解'}",
    ]
    response = image_model.generate_content(prompt_parts)
    if response._error:
        print(response._error)
        return "> **Error: Gemini API 响应错误**"
    return response.text


def clean_discord_message(input_string) -> str:
    # Create a regular expression pattern to match text between < and >
    bracket_pattern = re.compile(r"<[^>]+>")
    cleaned_content = bracket_pattern.sub("", input_string)
    return cleaned_content
