from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent

# ── LLM ──────────────────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    temperature=0.4,
)

# ── Herramientas ─────────────────────────────────────────────────────
tavily_search = TavilySearch(max_results=3)
tools = [tavily_search]

# ── System prompt ────────────────────────────────────────────────────
SYSTEM_PROMPT = (
    "Eres un asistente experto en comercio exterior, aduanas y aranceles de México. "
    "Responde en español de forma clara y concisa. "
    "Si necesitas datos actualizados (tipos de cambio, regulaciones vigentes, noticias, etc.), "
    "usa la herramienta de búsqueda en internet para obtener información confiable. "
    "Si no estás seguro de algo, dilo con honestidad."
)

# ── Agente ReAct ─────────────────────────────────────────────────────
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=SYSTEM_PROMPT,
)


async def chat_con_agente(mensaje: str) -> str:
    """Envía un mensaje al agente y devuelve la respuesta como texto."""
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": mensaje}]}
    )
    # La última entrada de messages es la respuesta del agente
    ai_message = response["messages"][-1]
    content = ai_message.content

    # Gemini a veces devuelve content como lista de bloques en vez de string
    if isinstance(content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    return str(content)
