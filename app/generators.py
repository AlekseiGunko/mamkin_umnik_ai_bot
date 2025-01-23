from openai import AsyncOpenAI
import httpx

from config import AITOKEN, PROXY

client = AsyncOpenAI(api_key=AITOKEN,
                     http_client=httpx.AsyncClient(proxy=PROXY,
                                                   transport=httpx.AsyncHTTPTransport(local_address="0.0.0.0")))


async def gpt_text(req, model):
    completion = await client.chat.completions.create(
        messages=[{"role": "user", "content": req}],
        model=model
    )
    return completion.choices[0].message.content