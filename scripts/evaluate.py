from pathlib import Path
from app.evaluation.evaluator import Evaluator
from app.services.rag_service import RagService

print(Evaluator(RagService()).run(Path("data/evaluation/golden.jsonl")))
