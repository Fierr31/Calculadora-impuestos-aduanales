import os
from typing import Any

from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch


class AduanalChatAgent:
    def __init__(self) -> None:
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.2)
        self.search_tool = TavilySearch(max_results=4, search_depth="basic")

    @staticmethod
    def _extract_text(content: Any) -> str:
        if isinstance(content, str):
            return content

        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str):
                        parts.append(text)
            return "\n".join(part for part in parts if part).strip()

        if isinstance(content, dict):
            text = content.get("text")
            if isinstance(text, str):
                return text

        return str(content)

    @staticmethod
    def _normalize_search_results(raw_results: Any) -> tuple[str, list[str]]:
        if isinstance(raw_results, dict):
            raw_results = raw_results.get("results", [])

        if not isinstance(raw_results, list):
            return "", []

        snippets: list[str] = []
        urls: list[str] = []

        for item in raw_results:
            if not isinstance(item, dict):
                continue
            url = item.get("url", "")
            title = item.get("title", "Sin titulo")
            content = item.get("content", "")
            if url:
                urls.append(url)
            snippets.append(f"- {title}\nURL: {url}\nResumen: {content[:600]}")

        return "\n\n".join(snippets), urls

    def run(self, user_prompt: str) -> dict[str, Any]:
        if not user_prompt.strip():
            return {"answer": "Por favor escribe un mensaje.", "used_search": False, "sources": []}

        used_search = False
        sources: list[str] = []

        @tool("buscar_en_internet")
        def buscar_en_internet(query: str) -> str:
            """Busca informacion actualizada en internet y regresa contexto resumido con URLs."""
            nonlocal used_search, sources
            used_search = True
            try:
                raw = self.search_tool.invoke({"query": query})
                context, found_sources = self._normalize_search_results(raw)
                for url in found_sources:
                    if url and url not in sources:
                        sources.append(url)

                if not context:
                    return "No encontre resultados utiles en internet para esa consulta."
                return context
            except Exception as exc:
                return f"Error al buscar en internet: {exc}"

        tools = [buscar_en_internet]
        llm_with_tools = self.llm.bind_tools(tools)

        messages = [
            SystemMessage(
                content=(
                    "Eres un asistente de comercio exterior y calculo aduanal para Mexico. "
                    "Responde de forma clara y accionable en espanol. "
                    "Si necesitas datos actuales, usa la herramienta buscar_en_internet. "
                    "Cuando uses informacion de internet, cita las URLs al final."
                )
            ),
            HumanMessage(content=user_prompt),
        ]

        final_answer = ""
        for _ in range(4):
            ai_msg = llm_with_tools.invoke(messages)
            messages.append(ai_msg)

            tool_calls = getattr(ai_msg, "tool_calls", None) or []
            if not tool_calls:
                final_answer = self._extract_text(getattr(ai_msg, "content", ai_msg))
                break

            for call in tool_calls:
                tool_name = call.get("name")
                tool_args = call.get("args", {})
                tool_call_id = call.get("id") or "tool_call"

                if tool_name != "buscar_en_internet":
                    messages.append(
                        ToolMessage(
                            content="Herramienta no soportada.",
                            tool_call_id=tool_call_id,
                        )
                    )
                    continue

                try:
                    if isinstance(tool_args, dict):
                        tool_output = buscar_en_internet.invoke(tool_args)
                    else:
                        tool_output = buscar_en_internet.invoke({"query": str(tool_args)})
                except Exception as exc:
                    tool_output = f"Error al ejecutar herramienta: {exc}"

                messages.append(ToolMessage(content=tool_output, tool_call_id=tool_call_id))

        if not final_answer:
            final_answer = "No pude generar una respuesta final. Intenta reformular la pregunta."

        if sources and "fuentes:" not in final_answer.lower():
            final_answer = f"{final_answer}\n\nFuentes:\n" + "\n".join(f"- {url}" for url in sources)

        return {"answer": final_answer, "used_search": used_search, "sources": sources}
