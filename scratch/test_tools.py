import asyncio
import httpx
import json

async def test_tools():
    print("Testing tool call: hello_world")
    async with httpx.AsyncClient() as c:
        res = await c.post(
            'http://localhost:8787/chat', 
            json={'text': 'Call the hello_world tool with the name "Jarvis User". Only call the tool, do not add any other pleasantries.'}
        )
        
        async for line in res.aiter_lines():
            if line:
                print(line)

if __name__ == "__main__":
    asyncio.run(test_tools())
