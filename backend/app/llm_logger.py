"""
LLM Logger for real-time UI updates.
Stores LLM generation outputs in a queue for SSE streaming.
"""
from collections import deque
from typing import Optional
from datetime import datetime
import json

# Global message queue (stores last 50 messages)
_llm_messages: deque = deque(maxlen=50)


class LLMMessage:
    """Represents a single LLM generation event."""
    
    def __init__(self, message_type: str, title: str, content: str, metadata: Optional[dict] = None):
        self.timestamp = datetime.now().isoformat()
        self.type = message_type  # "welcome", "skeleton", "story_points", "post_run"
        self.title = title
        self.content = content
        self.metadata = metadata or {}
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "type": self.type,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


def log_llm_output(message_type: str, title: str, content: str, metadata: Optional[dict] = None):
    """
    Log LLM output to the message queue.
    
    Args:
        message_type: Type of message ("welcome", "skeleton", "story_points", "post_run")
        title: Title/header of the message
        content: The actual LLM-generated content
        metadata: Additional metadata (route name, profile info, etc.)
    """
    message = LLMMessage(message_type, title, content, metadata)
    _llm_messages.append(message)
    return message


def get_recent_messages(limit: int = 20) -> list[dict]:
    """Get recent LLM messages."""
    return [msg.to_dict() for msg in list(_llm_messages)[-limit:]]


def clear_messages():
    """Clear all messages (for testing)."""
    _llm_messages.clear()



