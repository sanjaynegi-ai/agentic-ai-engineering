# Gradio

Gradio turns Python functions into local web demos. `gr.Interface` fits one-shot input/output functions; `gr.ChatInterface` manages chat-shaped input and history. In a notebook, `demo.launch(inline=True)` embeds the UI; for a browser use `demo.launch(inbrowser=True)`. Keep history in the session, catch exceptions at the UI boundary, and return helpful errors without secrets or stack traces.

For Hugging Face Spaces, keep `app.py` at the project root, pin dependencies, listen on the platform port, avoid local filesystem assumptions, and store keys as Space secrets. Do not enable public sharing for privileged tools.
