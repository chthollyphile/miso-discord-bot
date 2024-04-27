# miso-discord-bot
一个群聊助手类机器人，包括AI对话，notion数据库查询以及其他一些杂项功能。

## 部署相关

建议使用版本：python 3.10 以上
在discord developer portal 中注册application的时候，需要在bot页面开启 message content intent 权限

**注意：部署的时候需要手动修改 revChatGPT 库中的部分代码！**

1. `git clone` 克隆本仓库
2. `pip install -r requirements.txt` 安装相关依赖
3. 按下面的方法修改 `Python311\Lib\site-packages\revChatGPT\V3.py`：

```py
ENGINES = [
    "gpt-3.5-turbo",
    ...
    "gpt-4-32k-0613",
    "gpt-4-1106-preview" # 添加
]
    ...
    self.max_tokens: int = max_tokens or (
        4000                                # 添加
        if "gpt-4-1106-preview" in engine   # 添加
        else 31000
        if "gpt-4-32k" in engine
        else 7000
    ...
```
4. 将 `/misobot/.env.backup` 重命名为  `/misobot/.env`，按照说明填写其中的键值
5. 在 `/misobot `目录下执行 `python bot.py` 启动bot

## 命令
### LLM 相关

- `/gemini` 使用 google-gemini-pro 接口进行聊天。该模型是免费模型，仅有每分钟调用次数为60次的限制。大部分情况下推荐使用这个命令进行聊天

- `/vision` 使用 google-gemini-vision 对图片进行解读，此命令不支持上下文。

- `/chat, /reset ` 使用 openai-gpt3.5-turbo 接口进行聊天,部分代码来自 Zero6992/chatGPT-discord-bot 。/reset可以重置当前和所有openai模型之间的会话。

- `/chats` 使用 openai-gpt4-8k 接口进行聊天。注意，该模型的token费用非常昂贵。

- `/summary ` 展示关于过去七天的聊天相关的数据和图表，并将其中消息最多的一个小时的消息内容发送给gpt4进行总结。

- `/summarylatest ` 将过去一小时内的聊天消息内容发送给gpt4进行总结。

### notion 相关
使用notion API对数据库进行写入和查询，出于安全性的考虑，没有提供删除和修改的功能。
注意，这些命令不通过discord命令菜单执行，且不会返回是否执行成功的信息（目的是尽量减少对聊天会话的干扰）
 - `/tag keyword` 列出notion数据库中所有包含 keyword 作为标签的项目

 - `/记录 keyword` 将 keyword 写入数据库，并打上默认标签

 - `/写入 keyword tag` 将 keyword 写入数据库，然后打上 tag 标签

 - `/搜索 keyword` 列出所有包含 keyword 作为内容的项目，结果过多的时候会返回查询链接

### 其他
 - `/romaji` 把日语转换到罗马音，准确率不是很高。

 - `/加密, /解密` 用生化奇兵海葬的同款密码来加密/解密字符串。
 
## 语境菜单

可使用discord语境菜单调用 `请Gemini钦点两句` 的命令，使用Gemini对用户发送过的对话或图片进行解读