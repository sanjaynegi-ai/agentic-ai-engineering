import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE / "src"), str(HERE.parent / "no_framework" / "src")]
from comparison_openai_agents.ui import build_demo
if __name__ == "__main__": build_demo().launch(server_name="0.0.0.0", server_port=7860)
