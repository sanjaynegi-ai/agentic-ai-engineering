import gradio as gr
def build_demo(agent):
    def chat(message: str, history: list[dict]) -> str:
        try: return agent.run(message).answer
        except Exception as exc: return f"Agent stopped safely: {exc}"
    return gr.ChatInterface(fn=chat, title="No-framework Travel Planning Agent")
