# Generation

Generation builds a grounded prompt from selected chunks, calls a configurable LLM provider, parses structured output, creates citations, and validates grounding. If retrieval is empty or grounding fails, the system returns an insufficient-evidence answer.
