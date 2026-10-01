# Deployment — deadline checklist

## 1. Test locally
```bash
pip install -r requirements.txt
python run_pipeline.py
streamlit run app.py
```

## 2. GitHub
Create a repository named `project-foresight-demand-inventory` and push this folder.
Do not commit `.venv/` or secrets.

## 3. Streamlit dashboard
Create a Streamlit Community Cloud app from the GitHub repository.
- Main file: `app.py`
- Python dependencies: `requirements.txt`

After deployment, copy the public dashboard URL into the submission form.

## 4. Scoring API
Deploy the same repository as a Python web service on Render.
- Build: `pip install -r requirements.txt`
- Start: `uvicorn service:app --host 0.0.0.0 --port $PORT`

Test:
`/` for health and `/score/SKU001` for an example SKU.

## 5. Demo video (3–5 minutes)
Show, in this order:
1. Business problem and four datasets.
2. `python run_pipeline.py` and the WAPE comparison.
3. Streamlit dashboard and risk list.
4. Select one SKU and show its forecast.
5. Open the scoring API URL for one SKU.
6. Explain the 150 inventory-only SKU limitation and why it is documented.
7. End with reorder/markdown counts and rupee impact.
