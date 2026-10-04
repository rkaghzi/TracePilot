# TracePilot AI -- MVP

TracePilot discovers how an operation actually runs from event/process data, identifies bottlenecks and recommends high-value AI automation opportunities.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit.

## MVP flow

CSV process log → schema detection → event normalization → process transitions → duration analysis → bottleneck ranking → automation recommendations.

## Production evolution

1. Add process mining with PM4Py.
2. Add local LLM reasoning with Ollama + an Apache-2.0/open model such as Qwen2.5.
3. Add RAG over SOPs/policies with sentence-transformers + FAISS.
4. Add governed tool execution through APIs/RPA.
5. Add human approval thresholds and an immutable audit log.
6. Add connectors for ERP/CRM/ticketing/email systems.

The MVP intentionally works without an API key so it can run immediately.
#
