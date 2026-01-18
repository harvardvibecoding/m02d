Run the people headcount scenario app

1. Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the Streamlit app:

```bash
streamlit run people_headcount_app.py
```

The app loads the roster from `data_room/people/employee_roster.csv`. Use the sidebar slider to set a target headcount and choose compensation prioritization.

