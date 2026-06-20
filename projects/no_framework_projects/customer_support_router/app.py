import sys
from pathlib import Path
import gradio as gr
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))
from customer_support_router.service import run
def respond(text: str) -> str:
    return run(text).model_dump_json(indent=2)
if __name__ == "__main__":
    gr.Interface(fn=respond, inputs="text", outputs="text", title="Customer Support Router").launch(server_name="0.0.0.0", server_port=7860)
