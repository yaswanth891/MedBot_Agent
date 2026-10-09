# MediBot — Render deployment (Mac / GitHub)

This replica keeps the Streamlit interface, clinical RAG logic, LangChain LLM adapter, and opt-in LangSmith tracing. Only presentation styles/layout and deployment files were added.

## Deploy using `render.yaml` (recommended)

1. Unzip this project and upload the **contents of `MedBot_Agent-main`** to a private GitHub repository. Keep `Rag_pdf.pdf` only if you want its included demo content to load automatically. **Never commit `.env` or patient PDFs.**
2. Open https://dashboard.render.com/ → **New → Blueprint** → connect the GitHub repository containing `render.yaml`.
3. Review the proposed **Starter (paid)** web service and set `LLM_API_KEY` when prompted. Set `LANGSMITH_API_KEY` only if you want tracing. Confirm the deploy.
4. Wait for build and startup to succeed; open the service's `https://...onrender.com` address. Render checks `/_stcore/health`.
5. If not using Groq, edit `LLM_BASE_URL` and `LLM_MODEL` in the Render Environment settings to match an OpenAI-compatible chat-completions endpoint, then redeploy.

### Manually creating a Render Web Service

- Runtime: **Python**, Root Directory: repository root (folder containing `app.py`).
- Build: `pip install -r requirements.txt`
- Start: `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true`
- Health check: `/_stcore/health`
- Python: `3.11.11` through `PYTHON_VERSION`.
- Add the environment variables listed in `render.yaml` in **Environment**. Never paste credentials into source code.

## Where to obtain API keys

- Groq LLM: https://console.groq.com/keys → set `LLM_API_KEY` in Render's **Environment**. The example model is `openai/gpt-oss-20b`; change it if your account's available model differs.
- LangSmith (optional): https://smith.langchain.com/ → set `LANGSMITH_API_KEY`. Set `LANGSMITH_TRACING=true` **only if authorized to transmit prompts and responses**, which may include sensitive health information. Default is `false`.
- A `.env` file is for **local** development only, and is not required when Render Environment variables are configured.

## Hosting/storage considerations

- **Starter paid plan is recommended**: installing PyTorch + sentence-transformers + a local FLAN-T5 fallback and loading embeddings may exhaust a small free instance. You may need a larger instance depending on real memory usage. This package does not promise compatibility with the free tier.
- The app stores FAISS indexes **per Streamlit session**. The bundled demo PDF has a local `.kb_cache` for reusable embedding computation, but it is not a durable database. Uploaded PDFs are session-scoped and are **not saved as a shared knowledge base**. A server restart, redeploy, or session reset can discard this state. Persistent multi-user storage would require a separate architecture change and is intentionally not included.
- Don't upload sensitive patient data to a public demo. Restrict access and assess the data-handling/privacy implications of your LLM provider and optional LangSmith tracing.

## Verification

From the project root:

```bash
python -m unittest test_rag_core.py
python -m py_compile app.py langchain_backend.py rag_core.py
```
