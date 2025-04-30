# ollama-chat-with-edit

This is incredibly basic, adding onto the [example code](https://github.com/ollama/ollama-python/blob/main/examples/chat-with-history.py).

Features:
- Edit last response/inference in $EDITOR.
- Undo last prompt/response exchange.
- Response regeneration.
- Pseudo multi-line prompts (using Python `join`).
- Dreadfully primitive save/load.

# Help
Argument `-m` lets you pick an ollama model.

Use `ollama list` to see available models. Say you want to use `mistral-small`.

Then enter `python3 ollama-chat-with-edit2.py -m mistral-small`.
Change `DEFAULT_MODEL` in the code to pick a default.

