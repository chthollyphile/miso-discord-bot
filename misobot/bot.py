import discord
import os
import fetch
import bioshockCipher
import romanji
from discord.ext import commands
from dotenv import find_dotenv, load_dotenv
import CGresp
import log
import datetime
import aiohttp
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import io
import gemini

logger = log.setup_logger(__name__)

isPrivate = False
isReplyAll = False

load_dotenv(find_dotenv(".env"))
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
EMAIL = os.getenv("EMAIL")
PASSWD = os.getenv("PASSWD")
SESSION_TOKEN = os.getenv("SESSION_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ---------------------------------------------command handler-------------------------------------------------
async def Gemini_send_message(message: discord.Interaction, user_message: str):
    global isReplyAll
    if not isReplyAll:
        author = message.user.id
        await message.response.defer(ephemeral=isPrivate)  # 辟邪
    else:
        author = message.author.id
    try:
        user_message_preview = user_message if len(user_message) < 65 else f'{user_message[:65]}...'
        response = "> **" + user_message_preview + "** - <@" + str(author) + "> \n\n"
        response = f"{response}{await gemini.handle_response(message, user_message)}"
        await split_and_send(message, response)
    except Exception as e:
        await error_log(message, e)


async def Gemini_vision_send_message(
    message: discord.Interaction,
    attachment: discord.Attachment,
    user_message: str | None,
):
    global isReplyAll
    if not isReplyAll:
        author = message.user.id
        await message.response.defer(ephemeral=isPrivate)  # 辟邪
    else:
        author = message.author.id
    try:
        response = "> **" + attachment.url + "** - <@" + str(author) + "> \n\n"
        response = (
            f"{response}{await gemini.handle_vision(message, attachment,user_message)}"
        )
        await split_and_send(message, response)
    except Exception as e:
        await error_log(message, e)


async def Gemini_context_send_message(
    message: discord.Interaction,
    content: discord.Message,
):
    await message.response.defer(ephemeral=isPrivate)  # 辟邪
    author = content.author.id
    if content.attachments:
        attachment = content.attachments[0]
        try:
            response = "> **" + attachment.url + "** - <@" + str(author) + "> \n\n"
            response = f"{response}{await gemini.handle_vision(message, attachment,user_message=None)}"
            await split_and_send(message, response)
        except Exception as e:
            await error_log(message, e)
    else:
        try:
            user_message = content.content
            user_message_preview = user_message if len(user_message) < 65 else f'{user_message[:65]}...'
            response = "> **" + user_message_preview + "** - <@" + str(author) + "> \n\n"
            response = (
                f"{response}{await gemini.handle_response(message, user_message)}"
            )
            await split_and_send(message, response)
        except Exception as e:
            await error_log(message, e)


async def GPT_send_message(message: discord.Interaction, user_message, openaiModels):
    global isReplyAll
    if not isReplyAll:
        author = message.user.id
        await message.response.defer(ephemeral=isPrivate)  # 辟邪
    else:
        author = message.author.id
    try:
        user_message_preview = user_message if len(user_message) < 65 else f'{user_message[:65]}...'
        response = "> **" + user_message_preview + "** - <@" + str(author) + "> \n\n"
        chat_model = os.getenv("CHAT_MODEL")
        if chat_model == "OFFICIAL":
            if openaiModels == "gpt-3.5-turbo":
                response = (
                    f"{response}{await CGresp.official_handle_response(user_message)}"
                )
            elif openaiModels == "gpt-4":
                response = (
                    f"{response}{await CGresp.gpt4_handle_response(user_message)}"
                )
        elif chat_model == "UNOFFICIAL":
            response = (
                f"{response}{await CGresp.unofficial_handle_response(user_message)}"
            )
        await split_and_send(message, response)
    except Exception as e:
        await error_log(message, e)


# ---------------------------------------------misc functions-------------------------------------------------
        
async def error_log(message: discord.Interaction, e):
    if isReplyAll:
        await message.channel.send("> **Error: 出错了，过一会再试试**")
    else:
        await message.followup.send("> **Error: 出错了，过一会再试试**")
    logger.exception(f"Error while sending message: %s", e)


async def split_and_send(
    message: discord.Interaction, response: str, isReplyAll=False
) -> None:
    """
    将消息拆分为符合discord字数限制的消息段落，并依次发送。
    注意，必须先 defer 当前的 Interaction，才能使用：

    .. code-block:: python

        await interaction.response.defer(ephemeral=False)
        ...
        await message_spliter(message, response)

    """
    char_limit = 1900
    if len(response) > char_limit:
        # Split the response into smaller chunks of no more than 1900 characters each(Discord limit is 2000 per chunk)
        if "```" in response:
            # Split the response if the code block exists
            parts = response.split("```")

            for i, part in enumerate(parts):
                if i % 2 == 0:  # indices that are even are not code blocks
                    if isReplyAll:
                        await message.channel.send(part)
                    else:
                        await message.followup.send(part)

                    # Send the code block in a seperate message
                else:  # Odd-numbered parts are code blocks
                    code_block = part.split("\n")
                    formatted_code_block = ""
                    for line in code_block:
                        while len(line) > char_limit:
                            # Split the line at the 50th character
                            formatted_code_block += line[:char_limit] + "\n"
                            line = line[char_limit:]
                        formatted_code_block += (
                            line + "\n"
                        )  # Add the line and seperate with new line

                        # Send the code block in a separate message
                    if len(formatted_code_block) > char_limit + 100:
                        code_block_chunks = [
                            formatted_code_block[i : i + char_limit]
                            for i in range(0, len(formatted_code_block), char_limit)
                        ]
                        for chunk in code_block_chunks:
                            if isReplyAll:
                                await message.channel.send("```" + chunk + "```")
                            else:
                                await message.followup.send("```" + chunk + "```")
                    else:
                        if isReplyAll:
                            await message.channel.send(
                                "```" + formatted_code_block + "```"
                            )
                        else:
                            await message.followup.send(
                                "```" + formatted_code_block + "```"
                            )
        else:
            response_chunks = [
                response[i : i + char_limit]
                for i in range(0, len(response), char_limit)
            ]
            for chunk in response_chunks:
                if isReplyAll:
                    await message.channel.send(chunk)
                else:
                    await message.followup.send(chunk)
    else:
        if isReplyAll:
            await message.channel.send(response)
        else:
            await message.followup.send(response)


def GMT8Time() -> datetime.timezone:
    return datetime.timezone(datetime.timedelta(hours=8))

async def send_message(ctx, message):
    try:
        response = message
        if len(response) > 1990:
            # Split the response into smaller chunks of no more than 1990 characters each(Discord limit is 2000 per chunk)
            response_chunks = [
                response[i : i + 1990] for i in range(0, len(response), 1990)
            ]
            for chunk in response_chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(response)
    except Exception as e:
        await ctx.send("消息发送出现问题，请稍后再试")
        print(e)



async def send_message_interaction(interaction: discord.Interaction, response: str):
    char_limit = 1900
    if len(response) > char_limit:
        # Split the response into smaller chunks of no more than 1900 characters each(Discord limit is 2000 per chunk)
        response_chunks = [
            response[i : i + char_limit] for i in range(0, len(response), char_limit)
        ]
        for chunk in response_chunks:
            await interaction.followup.send(chunk)
    else:
        await interaction.followup.send(response)


async def send_start_prompt(client):
    config_dir = os.path.abspath(__file__ + "/../../")
    prompt_name = "starting-prompt.txt"
    prompt_path = os.path.join(config_dir, prompt_name)
    discord_channel_id = os.getenv("DISCORD_CHANNEL_ID")
    try:
        if os.path.isfile(prompt_path) and os.path.getsize(prompt_path) > 0:
            with open(prompt_path, "r") as f:
                prompt = f.read()
                if discord_channel_id:
                    logger.info(f"Send starting prompt with size {len(prompt)}")
                    chat_model = os.getenv("CHAT_MODEL")
                    response = ""
                    if chat_model == "OFFICIAL":
                        response1 = (
                            f"{response}{await CGresp.official_handle_response(prompt)}"
                        )
                        # response2 = f"{response}{await CGresp.gpt4_handle_response(prompt)}"
                    elif chat_model == "UNOFFICIAL":
                        response = f"{response}{await CGresp.unofficial_handle_response(prompt)}"
                    channel = client.get_channel(int(discord_channel_id))
                    await channel.send(response1)
                    logger.info(f"Starting prompt response:{response1}")
                else:
                    logger.info("No Channel selected. Skip sending starting prompt.")
        else:
            logger.info(f"No {prompt_name}. Skip sending starting prompt.")
    except Exception as e:
        logger.exception(f"Error while sending starting prompt: {e}")

        
# async def openai_usage():
#     url = "https://api.openai.com/dashboard/billing/usage"
#     today = datetime.date.today()
#     thisMonth = today.replace(day=1)
#     nextMonth = today.replace(day=1) + relativedelta.relativedelta(months=1)
#     querystring = {"end_date":nextMonth.strftime("%Y-%m-%d"),"start_date":thisMonth.strftime("%Y-%m-%d")}
#     headers = {"authorization": f"Bearer {OPENAI_API_KEY}"}
#     async with httpx.AsyncClient() as client:
#         response = await client.get(url, headers=headers, params=querystring)
#         json_response = response.json()
#         try:
#             total_usage = json_response["total_usage"]
#         except:
#             logger.exception(json_response)
#             return '> **Error: Openai API service error**'
#     total_usages = '%.2f'%(total_usage/100)
#     resp = f'> **Info: 本月已使用openai API额度 ${total_usages}**'
#     return resp


# 运行discord bot
# --------------------------------------------- BOT -------------------------------------------------
def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix="/", intents=intents)

    @client.event
    async def on_ready():
        await send_start_prompt(client)
        await client.tree.sync()
        await client.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="美少女たちのディープラーニングポーズ (｡-ω･)ﾉ･･━━☆ｷｭﾋﾟｰﾝ",
            )
        )
        print(f"logged in as {client.user}")

    @client.tree.command(name="chat", description="与chatGPT谈笑风生")
    async def chat(interaction: discord.Interaction, *, message: str):
        global isReplyAll
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        user_message = message
        channel = str(interaction.channel)
        openaiModels = "gpt-3.5-turbo"
        logger.info(f"\x1b[31m{username}\x1b[0m : '{user_message}' ({channel})")
        await GPT_send_message(interaction, user_message, openaiModels)

    @client.tree.command(name="gemini", description="与Google Gemini友好交流")
    @discord.app_commands.describe(message="对话内容. 发送 RESET 可重置对话")
    async def chat(interaction: discord.Interaction, *, message: str):
        global isReplyAll
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        user_message = message
        channel = str(interaction.channel)
        logger.info(f"\x1b[31m{username}\x1b[0m : '{user_message}' ({channel})")
        await Gemini_send_message(interaction, user_message)

    @client.tree.command(
        name="vision", description="Gemini-Vision图像识别(暂不支持上下文)"
    )
    @discord.app_commands.describe(attachment="图像文件",message="附加提示词，用于指示图像的解读")
    @discord.app_commands.rename(attachment="图片", message='提示词')
    async def chat(
        interaction: discord.Interaction,
        *,
        attachment: discord.Attachment,
        message: str | None = None,
    ):
        global isReplyAll
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        user_message = message
        channel = str(interaction.channel)
        logger.info(f"\x1b[31m{username}\x1b[0m : '{attachment.filename}' ({channel})")
        await Gemini_vision_send_message(interaction, attachment, user_message)

    @client.tree.context_menu(name="请Gemini钦点两句")
    async def chat(interaction: discord.Interaction, message: discord.Message):
        await Gemini_context_send_message(interaction, message)

    @client.tree.command(
        name="chats", description="与GPT4进行别样的指点江山(高消耗，慎用)"
    )
    async def chats(interaction: discord.Interaction, *, message: str):
        global isReplyAll
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        user_message = message
        channel = str(interaction.channel)
        openaiModels = "gpt-4"
        logger.info(f"\x1b[31m{username}\x1b[0m : '{user_message}' ({channel})")
        await GPT_send_message(interaction, user_message, openaiModels)

    @client.tree.command(name="reset", description="重置所有GPT会话")
    async def reset(interaction: discord.Interaction):
        chat_model = os.getenv("CHAT_MODEL")
        if chat_model == "OFFICIAL":
            CGresp.offical_chatbot.reset()
            CGresp.offical_chatbot_gpt4.reset()
        elif chat_model == "UNOFFICIAL":
            CGresp.unofficial_chatbot.reset_chat()
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send("> **Info: 已重置所有chatGPT, GPT4会话.**")
        logger.warning("\x1b[31mGPT has been successfully reset\x1b[0m")
        await send_start_prompt(client)

    @client.command()
    async def echos(ctx, arg):
        await ctx.send(arg)

    @client.command(name="搜索")
    async def _search(ctx, arg):
        ans = await fetch.database_query(arg, "Content")
        await send_message(ctx, ans)

    @client.command(name="tag")
    async def _tag(ctx, arg):
        ans = await fetch.snippets_notion(arg)
        await send_message(ctx, ans)

    @client.command(name="写入")
    async def _insert(ctx, arg1, *, arg):
        await fetch.embed_page_insert_with_p(arg, arg1)

    @client.command(name="记录")
    async def _archive(ctx, *, arg):
        await fetch.page_insert(arg, "神户盐")

    @client.command(name="加密")
    async def enc(ctx, arg):
        ans = await bioshockCipher.bioshockEnc(arg)
        await ctx.send(ans)

    @client.command(name="解密")
    async def dec(ctx, arg):
        ans = await bioshockCipher.bioshockDec(arg)
        await ctx.send(ans)

    @client.tree.command(name="romaji", description="日语转罗马音")
    async def romaji(interaction, words: str):
        response = "> " + words + "\n"
        rmj = await romanji.romanji(words)
        ans = f"{response}> {rmj}"
        await interaction.response.send_message(ans)

    # @client.tree.command(name='usage', description="查看当前月份的openai账号消费情况")
    # async def summary(interaction: discord.Interaction):
    #     await interaction.response.defer(ephemeral=isPrivate) # 辟邪
    #     resp = await openai_usage()
    #     await interaction.followup.send(resp)
        
    ## ---------------------------------------------!!!-------------------------------------------------
    ## 屎山，早期chatGPT自动生成的玩意，别想着改这个
    @client.tree.command(name="summary", description="最近7天的消息曲线")
    async def summary(interaction: discord.Interaction):
        channel = interaction.channel
        await interaction.response.defer(ephemeral=isPrivate)  # 辟邪
        seven_days_ago = datetime.datetime.now(tz=GMT8Time()) - datetime.timedelta(
            days=7
        )
        messages = []
        messagesContent = []
        async for message in channel.history(limit=None, after=seven_days_ago):
            messages.append(message)
        message_counts = {}
        for message in messages:
            time = message.created_at.astimezone(GMT8Time())
            day = time.strftime("%Y-%m-%d")
            hour = time.hour
            minute = time.minute // 15
            if day not in message_counts:
                message_counts[day] = {}
            if hour not in message_counts[day]:
                message_counts[day][hour] = [0] * 4
            message_counts[day][hour][minute] += 1

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://international.v1.hitokoto.cn?c=a&k&encode=text"
            ) as response:
                titleHtkt = await response.text()

        x = []
        y = []
        for day in message_counts:
            for hour in message_counts[day]:
                for minute in range(0, 60, 15):
                    x.append(day + " " + str(hour) + ":" + str(minute).zfill(2))
                    y.append(message_counts[day][hour][minute // 15])
        # 滑动窗口
        slider = max_y = sum(y[0:4])
        maxR = 3
        maxL = 0
        for i in range(1, len(y) - 3):
            slider = slider + y[i + 3] - y[i - 1]
            if slider >= max_y:
                max_y = slider
                maxR = i + 3
                maxL = i
        max_y_time_ago = datetime.datetime.strptime(x[maxL], "%Y-%m-%d %H:%M")
        max_y_time_after = datetime.datetime.strptime(x[maxR], "%Y-%m-%d %H:%M")
        one_hour_ago = max_y_time_ago.replace(tzinfo=GMT8Time())
        one_hour_after = max_y_time_after.replace(tzinfo=GMT8Time())
        async for message in channel.history(
            limit=None, after=one_hour_ago, before=one_hour_after
        ):
            messagesContent.append(message.content)

        prompt_message = f"用不超过1500字的中文来总结下面的聊天记录，不要发送除了总结之外的任何其他东西，用“当时我们讨论了”作为开头 {messagesContent}"
        try:
            bestowed = f"{await CGresp.gpt4_handle_response(prompt_message)}"
            print(f"openai reply: {bestowed}")
        except:
            print(f"openai reply: {bestowed}")
            bestowed = (
                "不过很遗憾，openai API返回了错误，因此您无从得知当时我们聊了什么。"
            )

        statistic = f'本周你群人的高光时刻是 {max_y_time_ago.strftime("%Y-%m-%d %H:%M")} 到 {max_y_time_after.strftime("%Y-%m-%d %H:%M")} ，共进行了**{max_y}**次指点江山\n\n{bestowed}'
        # fig = go.Figure(data=[go.Scatter(x=x, y=y, line=dict(color='#05946e'))]) ## 折线图
        fig = go.Figure(data=[go.Bar(x=x, y=y, marker=dict(color="#00dc07"))])
        fig.update_layout(
            yaxis_title="Message Count",
            plot_bgcolor="#2b2d31",
            paper_bgcolor="#2b2d31",
            font=dict(color="#d7d9dc"),
        )
        fig.update_xaxes(
            range=[seven_days_ago, datetime.datetime.now(tz=GMT8Time())],
            gridcolor="#47576a",
        )
        fig.update_yaxes(gridcolor="#47576a")
        img_bytes = fig.to_image(format="png")
        if len(img_bytes) == 0:
            await interaction.followup.send("过去一周内没有人发送过消息")
        elif len(bestowed) >= 1900:
            statistic1 = f'本周你群人的高光时刻是 {max_y_time_ago.strftime("%Y-%m-%d %H:%M")} 到 {max_y_time_after.strftime("%Y-%m-%d %H:%M")} ，共进行了**{max_y}**次指点江山'
            await interaction.followup.send(f"> **{titleHtkt}**\n\n{statistic1}\n")
            await send_message_interaction(interaction, bestowed)
            await interaction.followup.send(
                f"\n\n最近一周的消息图线: \n",
                file=discord.File(io.BytesIO(img_bytes), filename="plot.png"),
            )
        else:
            await interaction.followup.send(
                f"> **{titleHtkt}**\n\n{statistic}\n\n最近一周的消息图线: \n",
                file=discord.File(io.BytesIO(img_bytes), filename="plot.png"),
            )
    
    ## ---------------------------------------------!!!-------------------------------------------------
            
    @client.tree.command(name="summarylatest", description="刚才大家聊了啥?")
    async def summarylatest(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=isPrivate)  # 辟邪
        channel = interaction.channel
        # try:
        #     hoursInt = int(hours)
        #     hoursInt = hoursInt >= 2
        # except:
        #     logger.exception('hours 类型转换错误')
        #     return '> **Error: 必须输入整数**'
        last_two_messages = []
        async for message in channel.history(limit=2):
            last_two_messages.append(message)
        last_message_time = last_two_messages[1].created_at.astimezone(GMT8Time())
        hour_ago = last_message_time.replace(tzinfo=GMT8Time()) - datetime.timedelta(
            hours=1
        )
        messagesContent = []
        async for message in channel.history(limit=None, after=hour_ago):
            messagesContent.append(message.content)

        if len(messagesContent) <= 5:
            await interaction.followup.send("可以说几乎啥都没聊，自己看吧")
        else:
            prompt_message = f"用不超过1500字的中文来总结下面的聊天记录，不要发送除了总结之外的任何其他东西，用“刚才我们聊了”作为开头 {messagesContent}"
            try:
                bestowed = f"{await CGresp.gpt4_handle_response(prompt_message)}"
                print(f"openai reply: {bestowed}")
            except:
                print(f"openai reply: {bestowed}")
                bestowed = "> **Error: Openai API service error**"
            await send_message_interaction(interaction, f"{bestowed}")

    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    run_discord_bot()
