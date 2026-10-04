# Deployment

## Easiest public demo: Streamlit Community Cloud
1. Create a GitHub repository.
2. Upload all files in this folder.
3. In Streamlit Community Cloud choose the repository and `app.py`.
4. Deploy.
5. Use `sample_process_log.csv` for the first demo.

## Open-source AI upgrade
For the production version, run an open-source instruction model locally/inside a GPU service using Ollama or vLLM. Recommended starting point: Qwen2.5-7B-Instruct. The LLM should receive the structured process findings, SOP excerpts and policy rules, and produce ranked automation proposals. Keep the deterministic process-mining layer separate from the LLM so results remain measurable and auditable.

## Demo credentials
None are required for the MVP. This is intentional: the evaluator can open the app and immediately upload the sample CSV.
