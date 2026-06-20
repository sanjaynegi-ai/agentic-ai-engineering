import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from comparison_no_framework.agent import TravelAgent
from comparison_no_framework.llm import OpenAILLM
from comparison_no_framework.ui import build_demo
if __name__ == "__main__": build_demo(TravelAgent(OpenAILLM())).launch(server_name="0.0.0.0", server_port=7860)
