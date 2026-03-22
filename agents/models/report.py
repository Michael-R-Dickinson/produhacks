from uagents import Model


class ReportRequest(Model):
    """Bridge -> Orchestrator. Triggers full report pipeline."""
    holdings: list[str]
    mock: bool = False
    knowledge_level: int = 2  # 1=Beginner … 5=Expert
