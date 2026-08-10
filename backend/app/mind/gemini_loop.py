"""Gemini streaming loop and tool-call handling for the Mind."""
from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

try:
    from google import genai  # type: ignore
    from google.genai import types  # type: ignore

    _HAS_GENAI = True
except ImportError:
    _HAS_GENAI = False

from .. import config
from ..hands.registry import REGISTRY, run_tool


def build_gemini_tools() -> list[Any]:
    """Convert tool registry to Gemini FunctionDeclaration list."""
    if not _HAS_GENAI:
        return []

    declarations = []
    for tool in REGISTRY.values():
        declarations.append(
            types.FunctionDeclaration(
                name=tool["name"],
                description=tool["description"],
                parameters=tool.get("parameters", {}),
            )
        )

    return [types.Tool(function_declarations=declarations)] if declarations else []


async def gemini_stream(
    system_prompt: str,
    history: list[dict[str, Any]],
    user_text: str,
    session_id: str,
    device_id: str,
) -> AsyncGenerator[str, None]:
    if not _HAS_GENAI:
        yield "[Error: google-genai not installed. Run: pip install google-genai]"
        return

    client = genai.Client(api_key=config.GEMINI_API_KEY)

    contents: list[types.Content] = []
    for msg in history[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

    contents.append(types.Content(role="user", parts=[types.Part(text=user_text)]))

    tools: list[types.Tool] = build_gemini_tools()

    for _turn in range(5):
        try:
            response = await client.aio.models.generate_content_stream(
                model=config.LLM_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    tools=tools if tools else None,
                    temperature=0.7,
                ),
            )

            tool_calls = []
            final_text = ""

            async for chunk in response:
                if chunk.text:
                    final_text += chunk.text
                    yield chunk.text
                if chunk.function_calls:
                    tool_calls.extend(chunk.function_calls)

            if not tool_calls:
                break

            parts = []
            if final_text:
                parts.append(types.Part(text=final_text))
            parts += [types.Part(function_call=fc) for fc in tool_calls]
            contents.append(types.Content(role="model", parts=parts))

            tool_responses = []
            for fc in tool_calls:
                name = fc.name
                params = dict(fc.args) if fc.args else {}

                yield f"\n[Calling tool: {name}...]\n"

                result = await run_tool(
                    name,
                    params,
                    session_id=session_id,
                    device_id=device_id,
                    user_text=user_text,
                )

                tool_responses.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=name,
                            response=result,
                        )
                    )
                )

            contents.append(types.Content(role="user", parts=tool_responses))

        except Exception as exc:
            yield f"\n[LLM Error: {exc}]"
            break
