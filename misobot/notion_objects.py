class no:
    
    @staticmethod
    def block_object(content):
        block_object = [{
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": content
                        }
                    }
                ]
            }
        }]
        return block_object
    
    @staticmethod
    def database_object(flag,title,content): # 【 flag title | content | #flag #自动书记 】
        database_object = {
        "Title": {"title": [{"text": {"content": flag + ' ' + title}}]},
        "Tags": {"type": "multi_select", "multi_select": [{"name": flag},{"name": "自动书记"}]},
        "Content": {
            "type": "rich_text",
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": content},
                }
            ]
        }
        }
        return database_object

    @staticmethod
    def page_object(title):
        page_object = {
        "title": {
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": title
                    }
                }
            ]
        }}
        return page_object
        
    @staticmethod
    def quote_object(content):
        quote_object = [{
            "object": "block",
            "type": "quote",
            "quote": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": content
                        }
                    }
                ]
            }
        }]
        return quote_object
    
    @staticmethod
    def callout_object(title,content):
        callout_object = [{
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": title
                        }
                    }],
                "icon": {
                    "emoji": "📎"
                },
                "color": "gray_background",
                "children": [{
                    "object": "block",
                    "type": "quote",
                    "quote": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": content
                                }
                            }
                        ]
                    }
                }]
            }
        }]
        return callout_object
