.PHONY: test api ui evaluate benchmark

test:
	python -m pytest -q

api:
	uvicorn app.api.main:app --reload

ui:
	streamlit run frontend/streamlit_app.py

evaluate:
	python scripts/evaluate.py

benchmark:
	python scripts/benchmark.py
