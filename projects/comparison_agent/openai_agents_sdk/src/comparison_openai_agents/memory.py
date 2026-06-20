from agents import SQLiteSession
def create_session(session_id: str = "local-demo") -> SQLiteSession: return SQLiteSession(session_id, "agent_sessions.db")
