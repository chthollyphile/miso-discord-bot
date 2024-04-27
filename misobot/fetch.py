import os
import asyncio
import time
from notion_client import AsyncClient
from notion_objects import no
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv('.env'))
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
PAGE_ID = os.getenv("PAGE_ID")
NOTION_SHARELINK = os.getenv("NOTION_SHARELINK")

# Initialize the client
notion = AsyncClient(auth=NOTION_TOKEN)
async def database_query(contains,propertys):
    results = (await notion.databases.query(
        **{
            "database_id": DATABASE_ID,
            "filter": {
                "property": propertys,  # notion database property, case-sensitive
                "rich_text": {
                "contains": contains
            }
        }
    })).get("results")
    no_of_results = len(results)
    if no_of_results == 0:
        mes = await database_retrieve_match_search(DATABASE_ID,contains)
        return mes
    ans = '查询到'+str(len(results))+'个记录\n'
    respond = ""
    for i in range(len(results)):
        result_properties = results[i]['properties'][propertys]['rich_text'][0]['plain_text']
        respond = respond + '\n\n' + result_properties  # text
    if len(respond)<=10000:
        return ans + respond.strip()
    else:
        return f'结果过长,请自行前往 {NOTION_SHARELINK}'

async def database_retrieve_match_search(database_id,keywords):
    respond = await notion.databases.retrieve(database_id)
    tag_list = respond['properties']['Tags']['multi_select']['options']
    l = []
    for i in range(len(tag_list)):
        tags = tag_list[i]['name']
        if keywords in tags:
            l.append(tags)
        else:
            pass
    ls = ', '.join(l)
    if len(l) == 0:
        return f"未找到包含{keywords}的记录"
    else:
        return f"未找到包含{keywords}的记录，请尝试使用 /tag 查询以下标签：{ls} "

async def snippets_notion(args): # notion database query - Tags
    results = (await notion.databases.query(
        **{
            "database_id": DATABASE_ID,
            "filter": {
                "property": 'Tags',  # notion database property, case-sensitive
                "multi_select": {
                    "contains": args
                }
            }
    })).get("results")
    no_of_results = len(results)
    if no_of_results == 0:
        # return f"未找到{args}标签"
        mes = await database_retrieve_match(database_id=DATABASE_ID,keywords=args)
        return mes
    respond = ""
    for i in range(len(results)):
        result_properties = results[i]['properties']['Content']['rich_text'][0]['plain_text']
        respond = respond + '\n\n' + result_properties # text
    if len(respond)<=10000:
       return respond.strip()
    else:
        return f'结果过多,请自行前往 {NOTION_SHARELINK}' 

async def database_retrieve_match(database_id,keywords):
    respond = await notion.databases.retrieve(database_id)
    tag_list = respond['properties']['Tags']['multi_select']['options']
    l = []
    for i in range(len(tag_list)):
        tags = tag_list[i]['name']
        if keywords in tags:
            l.append(tags)
        else:
            pass
    ls = ', '.join(l)
    if len(l) == 0:
        return f"未找到符合的标签"
    else:
        return f"你要找的是不是: "+ls

# Notion Insert
async def page_insert(args: str, title: str): # notion API
    ctime = time.strftime("%Y-%m-%d %X ", time.localtime())
    await asyncio.gather(
        notion.blocks.children.append(block_id=PAGE_ID, children=no.quote_object(args)),
        notion.pages.create(parent={"database_id": DATABASE_ID}, properties=no.database_object(flag=title, title=ctime, content =args)),
    )

async def embed_page_insert_with_p(args: str, title: str): # notion API
    ctime = time.strftime("%Y-%m-%d %X ", time.localtime())
    await asyncio.gather(
        notion.blocks.children.append(block_id=PAGE_ID, children=no.callout_object(title,args)),
        notion.pages.create(parent={"database_id": DATABASE_ID}, properties=no.database_object(flag=title, title=ctime, content =args)),
    )

if __name__ == "__main__":
    async def main():
        await asyncio.gather(database_query('contains','propertys'))
    asyncio.run(main())
    