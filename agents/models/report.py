from uagents import Model


class ReportRequest(Model):
    """Bridge -> Orchestrator. Triggers full report pipeline."""
    holdings: list[str]
    mock: bool = False
