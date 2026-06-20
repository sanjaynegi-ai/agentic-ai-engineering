import gradio as gr
from agents import Runner
from .agents import build_agents
from .memory import create_session
def build_demo():
    agents = build_agents(); session = create_session()
    async def chat(message: str, history: list[dict]) -> str:
        try:
            result = await Runner.run(agents["triage"], input=message, session=session, max_turns=8)
            output = result.final_output
            return output.model_dump_json(indent=2) if hasattr(output, "model_dump_json") else str(output)
        except Exception as exc: return f"Agent stopped safely: {exc}"
    return gr.ChatInterface(fn=chat, title="OpenAI Agents SDK Travel Team")
