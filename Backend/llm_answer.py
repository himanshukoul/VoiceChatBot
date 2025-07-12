import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FIN_PROMPT = """
You are a helpful and reliable financial assistant. A user has asked a question using voice, which has been converted to text. You have also been provided with up to 3 knowledge snippets (context) retrieved from a financial knowledge base.

1)START your ANSWER with: TWO very SHORT SENTENCES, each UNDER 8–10 words. These allow early audio playback.

2)Your job is to answer the user’s question using only the information in the provided context. If the context is strong and relevant, respond based on it. If the context is missing or insufficient, and the user’s query is a general finance concept (like what is saving, budgeting, or credit score), you may use your general financial knowledge to answer.

3)If the query is too vague or specific but the context is not helpful, ask the user to clarify or provide more detail. Never hallucinate or fabricate facts. Do not include any formatting like bullet points or markdown. Output only the final answer as a plain text string.

---

Context:
{context}

User Query:
{user_query}

---

Final Answer (in plain text):
"""

def get_llm_answer(user_query,context):
    
    prompt = FIN_PROMPT.format(context=context, user_query=user_query)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        #print("Error from OpenAI:", e)
        return "Sorry, something went wrong while generating the answer."
    
def stream_llm_answer(user_query, context):
    prompt = FIN_PROMPT.format(context=context, user_query=user_query)
    try:
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        print("Streaming error:", e)
        yield "[Error: Failed to stream response]"
