import asyncpg
import asyncio
import json
import os
from dotenv import load_dotenv

async def save_data(response):
    os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    load_dotenv()
    URL = os.getenv("DATABASE_URL")
    print(URL)
    conn = await asyncpg.connect(URL)

    # Extract the message content from AIMessage object
    messages = []
    for msg in response["messages"]:
        if hasattr(msg, 'content'):
            messages.append({
                "role": "assistant",
                "content": msg.content
            })
        else:
            messages.append(msg)  # fallback for non-AIMessage items

    # Insert into chat_history
    chat_id = await conn.fetchval(
        """
        INSERT INTO chat_history (user_query, llm_response, expanded_question, messages)
        VALUES ($1, $2, $3, $4) RETURNING id;
        """,
        response["original_question"],
        json.dumps({
            "original_question": response["original_question"],
            "expanded_question": response["expanded_question"],
            "search_queries": response["search_queries"],
            "search_results": response["search_results"],
            "messages": messages
        }),
        response["expanded_question"],
        json.dumps(messages)
    )

    # Insert into search_history
    for query in response["search_queries"]:
        await conn.execute(
            """
            INSERT INTO search_history (chat_id, generated_query, search_queries)
            VALUES ($1, $2, $3);
            """,
            chat_id, query, json.dumps(response["search_queries"])
        )

    # Insert into links
    for result in response["search_results"]:
        await conn.execute(
            """
            INSERT INTO links (search_link, title, content, similarity)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (search_link) DO NOTHING;
            """,
            result["url"], result["title"], result["content"], result["score"]
        )

    await conn.close()
    print(f"✅ Response saved with chat_id {chat_id}")


    