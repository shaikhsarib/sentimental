# Sentimental Fine-Tune Hooks

This folder provides scaffolding for local LoRA fine-tuning. Groq does not support fine-tuning, so the recommended path is to fine-tune an open model and run it via Ollama.

## Output target
- Use `LOCAL_MODEL=sentimental-ft` and `USE_LOCAL_MODEL=true` to route requests to your fine-tuned model.
- The backend will automatically call Ollama when `USE_LOCAL_MODEL` is enabled.

## Dataset format (ChatML-style JSONL)
Each line is a JSON object with a `messages` array:

```
{"messages": [{"role": "system", "content": "You are a risk analyst."}, {"role": "user", "content": "<content>"}, {"role": "assistant", "content": "<expected response>"}]}
```

## Suggested steps
1. Generate data: `python backend/training/prepare_dataset.py`
2. Fine-tune using your preferred LoRA toolchain.
3. Serve with Ollama or llama.cpp.
4. Set `USE_LOCAL_MODEL=true` and `LOCAL_MODEL=sentimental-ft` in `.env`.

## Notes
- Keep prompts consistent with your production system prompts.
- Use a holdout set for evaluation before deployment.
