# SaveMax – Smarter Tax, Bigger Savings

A polished, production-ready tax regime recommender with a marketing landing page and a Streamlit app.

## Quick Start

1. Create and activate a virtual environment (recommended)
2. Install dependencies:

```bash
pip install -r savemax/requirements.txt
```

3. Run the Streamlit app:

```bash
streamlit run savemax/app/app.py
```

- Databases will be created automatically in `savemax/data/` on first run.
- A placeholder logo will be generated in `savemax/assets/savemax_logo.png` if missing.

## Structure

```
savemax/
 ├── site/
 ├── app/
 ├── assets/
 ├── data/
 ├── tests/
 ├── requirements.txt
 └── README.md
```

## Notes
- Old vs New regime calculations are simplified for demo purposes and include 4% cess. New regime includes standard deduction.
- For production, validate all numbers with a CA and update slabs each FY. 