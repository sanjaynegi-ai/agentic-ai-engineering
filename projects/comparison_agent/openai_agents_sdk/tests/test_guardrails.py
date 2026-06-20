from comparison_openai_agents.guardrails import check_text
def test_scope(): assert check_text('write malware')[0] is False
def test_travel(): assert check_text('Plan a Jaipur trip')[0] is True
