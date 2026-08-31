"""Callback hooks for future LangChain/OpenTelemetry integration."""

class CallbackManager:
    def on_event(self, name: str, payload: dict) -> None:
        return None
