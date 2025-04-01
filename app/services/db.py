import asyncpg
import json
import os
from dotenv import load_dotenv

async def save_data(response):
    # Load environment and connect to DB
    os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    load_dotenv()
    URL = os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(URL)

    try:
        # --- 1. Insert into chat_history ---
        chat_id = await conn.fetchval(
            """
            INSERT INTO chat_history (user_query, llm_response)
            VALUES ($1, $2)
            RETURNING id;
            """,
            response["original_question"],
            json.dumps({
                "original_question": response["original_question"],
                "expanded_question": response.get("expanded_question"),
                "search_queries": response.get("search_queries", []),
                "search_results": response.get("search_results", []),
                "messages": [
                    {"role": "assistant", "content": msg.content} 
                    if hasattr(msg, 'content') else msg
                    for msg in response.get("messages", [])
                ]
            })
        )

        # --- 2. Insert into search_history (supports 3 queries/links) ---
        queries = response.get("search_queries", [])
        links = [result["url"] for result in response.get("search_results", [])[:3]]  # Take first 3 links
        
        await conn.execute(
            """
            INSERT INTO search_history (
                chat_id,
                generated_query_1, search_link_1,
                generated_query_2, search_link_2,
                generated_query_3, search_link_3
            ) VALUES ($1, $2, $3, $4, $5, $6, $7);
            """,
            chat_id,
            queries[0] if len(queries) > 0 else None,
            links[0] if len(links) > 0 else None,
            queries[1] if len(queries) > 1 else None,
            links[1] if len(links) > 1 else None,
            queries[2] if len(queries) > 2 else None,
            links[2] if len(links) > 2 else None
        )

        # --- 3. Insert into llm_processing_steps ---
        if "expanded_question" in response:
            await conn.execute(
                """
                INSERT INTO llm_processing_steps (chat_id, expanded_prompt)
                VALUES ($1, $2);
                """,
                chat_id, response["expanded_question"]
            )

        

        print(f"✅ Data saved successfully! Chat ID: {chat_id}")

    except Exception as e:
        print(f"❌ Error saving data: {e}")
        raise
    finally:
        await conn.close()