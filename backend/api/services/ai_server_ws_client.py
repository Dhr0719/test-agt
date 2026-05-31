import asyncio
import json
import re

import websockets
from django.conf import settings


def clean_json_text(text):
    """
    清理 AI 可能返回的 Markdown JSON 代码块。
    """
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```json", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"^```", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

    return text


async def _ask_ai_server_chat_async(message, kb_name):
    """
    通过 ai-server 的 WebSocket /api/v1/chat 发起一次 RAG 问答。
    等到 type=result 后返回最终内容。
    """

    ws_url = f"{settings.AI_SERVER_WS_BASE_URL}/api/v1/chat"

    payload = {
        "message": message,
        "session_id": None,
        "kb_name": kb_name,
        "enable_rag": True,
        "enable_web_search": False,
        "history": None,
    }

    async with websockets.connect(ws_url, ping_interval=None) as websocket:
        await websocket.send(json.dumps(payload, ensure_ascii=False))

        final_content = ""
        sources = []

        while True:
            raw_message = await websocket.recv()
            event = json.loads(raw_message)

            event_type = event.get("type")

            if event_type == "session":
                continue

            if event_type == "status":
                continue

            if event_type == "stream":
                continue

            if event_type == "sources":
                sources = event.get("rag", [])
                continue

            if event_type == "result":
                final_content = event.get("content", "")
                break

            if event_type == "error":
                raise RuntimeError(event.get("message") or event.get("detail") or "ai-server WebSocket 调用失败")

        return {
            "content": final_content,
            "sources": sources,
        }


def ask_ai_server_chat(message, kb_name):
    """
    给 Django 同步代码调用的包装函数。
    """
    return asyncio.run(_ask_ai_server_chat_async(message, kb_name))


def ask_ai_server_for_knowledge_mapping(kb_name, knowledge_points):
    """
    调用 ai-server RAG 问答，让它基于知识库内容映射 Django 的 KnowledgePoint。
    """

    knowledge_points_text = "\n".join([
        f"ID:{item['id']}｜名称:{item['name']}｜分类:{item.get('category', '')}｜关键词:{item.get('keywords', '')}｜描述:{item.get('description', '')}"
        for item in knowledge_points
    ])

    prompt = f"""
你是学习资料知识点映射助手。请基于当前知识库中的上传文件内容，从下面给定的知识点列表中选择最相关的知识点。

要求：
1. 只能从给定知识点列表中选择，不能编造新的知识点。
2. 返回严格 JSON，不要返回 Markdown，不要解释。
3. confidence 为 0 到 1 之间的小数。
4. reason 用中文说明匹配原因。
5. summary 用中文概括上传文件主要内容。
6. 如果没有明显匹配项，matched_points 返回空数组。

知识点列表：
{knowledge_points_text}

请严格返回如下 JSON 格式：
{{
  "summary": "文件摘要",
  "matched_points": [
    {{
      "knowledge_point_id": 1,
      "name": "知识点名称",
      "confidence": 0.9,
      "reason": "匹配原因"
    }}
  ]
}}
"""

    result = ask_ai_server_chat(
        message=prompt,
        kb_name=kb_name,
    )

    content = clean_json_text(result["content"])

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise RuntimeError(f"AI 返回的不是合法 JSON：{content}")

    if "summary" not in data:
        data["summary"] = ""

    if "matched_points" not in data:
        data["matched_points"] = []

    return data