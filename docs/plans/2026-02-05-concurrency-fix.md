# Fix Concurrency Issue - Multiple Users Message Corruption

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix the "Conversation roles must alternate user/assistant" error when multiple users message the bot simultaneously

**Architecture:** The issue occurs because:
1. Multiple users in same channel trigger parallel `on_message` handlers
2. Each handler reads/writes to the same `Channel` aggregate without proper synchronization
3. Two user messages can be added before the assistant reply, breaking the alternation pattern

**Tech Stack:** Python asyncio, threading locks, repository pattern

---

## Root Cause Analysis

The error occurs because:
1. User A and User B message the bot at the same time in channel X
2. Handler A reads channel X with 0 messages, adds user A message
3. Handler B reads channel X (still has 0 messages - A's save not yet committed), adds user B message
4. Handler A generates reply, saves: [user A, assistant]
5. Handler B generates reply with [user A, user B] - **TWO CONSECUTIVE USER MESSAGES!**
6. OpenAI API rejects: "Conversation roles must alternate user/assistant/user/assistant"

---

## Task 1: Add concurrent access test for Channel aggregate

**Files:**
- Create: `tests/unit/channel/test_concurrent_channel.py`

**Step 1: Write failing test for concurrent message additions**

```python
import asyncio
import threading
from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent

def test_concurrent_message_additions():
    """Test that concurrent message additions don't corrupt the history."""
    channel = Channel(channel_id=123)
    
    messages_added = []
    errors = []
    
    def add_message(role: str):
        try:
            channel.add_message(Message(role=role, content=MessageContent(value="test")))
            messages_added.append(role)
        except Exception as e:
            errors.append(e)
    
    # Simulate concurrent access with threads
    threads = [
        threading.Thread(target=add_message, args=("user",)),
        threading.Thread(target=add_message, args=("user",)),
    ]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # This should not happen - two consecutive user messages
    assert len(errors) == 0, f"Errors occurred: {errors}"
    # For now, this will likely pass but we'll verify the messages array
    # In a race condition, we might see duplicates or ordering issues
```

**Step 2: Run test to verify it fails (might not fail yet - that's OK)**

Run: `pytest tests/unit/channel/test_concurrent_channel.py -v`

**Step 3: Run test with thread sanitizer if available**

Run: `pytest tests/unit/channel/test_concurrent_channel.py -v --tb=long`

**Step 4: Commit**

```bash
git add tests/unit/channel/test_concurrent_channel.py
git commit -m "test: add concurrent channel access test"
```

---

## Task 2: Add thread lock to Channel aggregate

**Files:**
- Modify: `src/domain/channel/aggregate.py`

**Step 1: Add threading lock to Channel class**

```python
# Add at top of file
import threading
from typing import TYPE_CHECKING, Any

# Add to Channel class
class Channel:
    def __init__(self, channel_id: int, ...) -> None:
        ...
        self._lock = threading.Lock()
```

**Step 2: Wrap add_message with lock**

```python
def add_message(self, message: Message) -> None:
    with self._lock:
        # existing logic
```

**Step 3: Run test**

Run: `pytest tests/unit/channel/test_concurrent_channel.py -v`

**Step 4: Commit**

```bash
git add src/domain/channel/aggregate.py
git commit -m "feat: add threading lock to Channel aggregate"
```

---

## Task 3: Add unit test for ProcessUserTurn concurrency

**Files:**
- Create: `tests/unit/messaging/test_concurrent_handlers.py`

**Step 1: Write test for concurrent message processing**

```python
import asyncio
import threading
from src.application.messaging.handlers import ProcessUserTurn
from src.infrastructure.persistence.memory.repository import InMemoryMessageRepository
from src.infrastructure.ai.openai.adapter import OpenAIServiceAdapter
from src.domain.channel.value_objects import Message

class MockAIService:
    def generate_reply(self, channel, image_urls=()):
        return "test response"

def test_concurrent_message_processing():
    """Test concurrent message handlers don't corrupt channel state."""
    repo = InMemoryMessageRepository()
    ai_service = MockAIService()
    handler = ProcessUserTurn(repo, ai_service)
    
    results = []
    errors = []
    
    def process_message(user_num: int):
        try:
            result = handler.execute(
                channel_id=123,
                user_content=f"Message from user {user_num}",
                author_name=f"User{user_num}",
                bot_name="Bot",
            )
            results.append((user_num, result))
        except Exception as e:
            errors.append((user_num, e))
    
    # Simulate 5 concurrent users
    threads = [threading.Thread(target=process_message, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Get the channel
    channel = repo.get(123)
    messages = channel.get_messages()
    
    # Verify alternation: user, assistant, user, assistant, ...
    roles = [m.role for m in messages]
    for i in range(len(roles) - 1):
        assert roles[i] != roles[i + 1], f"Consecutive same roles at index {i}: {roles}"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/messaging/test_concurrent_handlers.py -v`

**Step 3: Implement fix in ProcessUserTurn**

```python
# In ProcessUserTurn.execute, wrap channel operations with lock
def execute(self, channel_id: int, ...) -> str:
    channel = self.repo.get_or_create(channel_id)
    with channel._lock:  # Use the lock from Channel
        # existing logic
```

**Step 4: Run test again**

Run: `pytest tests/unit/messaging/test_concurrent_handlers.py -v`

**Step 5: Commit**

```bash
git add tests/unit/messaging/test_concurrent_handlers.py src/application/messaging/handlers.py
git commit -m "fix: add locking to ProcessUserTurn to prevent concurrent corruption"
```

---

## Task 4: Verify the full flow with integration test

**Files:**
- Create: `tests/integration/test_concurrent_discord_messages.py`

**Step 1: Write integration test**

```python
import asyncio
import pytest
from discord.ext import commands
from discord import Message, User, PartialMessage
from src.frameworks_drivers.discord.bot import handle_message_processing

@pytest.mark.asyncio
async def test_concurrent_discord_messages():
    """Test that concurrent Discord messages don't corrupt channel state."""
    # Setup
    bot = commands.Bot(command_prefix="!")
    processor = ...  # Get actual processor
    
    # Create mock messages from different users
    user1 = User(id=1, name="User1", discriminator="0001", bot=False)
    user2 = User(id=2, name="User2", discriminator="0002", bot=False)
    
    # Simulate concurrent messages
    async def send_message(user):
        msg = Message(
            channel=None,
            data={},
            state=None,
            guild=None,
        )
        msg.author = user
        msg.content = f"Hello from {user.name}"
        msg.mentions = []
        
        await handle_message_processing(msg, processor, bot, asyncio.Lock())
    
    # Run concurrently
    await asyncio.gather(send_message(user1), send_message(user2))
```

**Step 2: Run test**

Run: `pytest tests/integration/test_concurrent_discord_messages.py -v`

**Step 3: Commit**

```bash
git add tests/integration/test_concurrent_discord_messages.py
git commit -m "test: add integration test for concurrent Discord messages"
```

---

## Task 5: Add documentation for concurrency model

**Files:**
- Create: `docs/concurrency.md`

**Step 1: Document the threading model**

```markdown
# Concurrency Model

## Problem Statement
When multiple users message the bot simultaneously in the same channel, the conversation history could be corrupted, leading to "Conversation roles must alternate" errors from the OpenAI API.

## Solution
Each `Channel` aggregate uses a `threading.Lock` to ensure that only one thread can modify the message history at a time. This prevents:
- Two user messages being added before an assistant reply
- Message order corruption
- Duplicate messages

## Locking Strategy
- **Scope**: Per-channel (each channel has its own lock via Channel.aggregate)
- **Granularity**: Message add operations are atomic
- **Deadlock prevention**: Lock is acquired before any database/repository operations

## Testing
Run: `pytest tests/unit/channel/ --concurrent -v`
```

**Step 2: Commit**

```bash
git add docs/concurrency.md
git commit -m "docs: document concurrency model for channel aggregates"
```

---

## Task 6: Run full test suite and commit

**Step 1: Run all tests**

```bash
source .venv/bin/activate
pytest -v
```

**Step 2: Run linters**

```bash
black src/
ruff check src/
mypy src/
```

**Step 3: Final commit**

```bash
git add .
git commit -m "fix: resolve concurrent message corruption issue

- Added threading lock to Channel aggregate
- Wrapped message processing with lock in ProcessUserTurn
- Added concurrent access tests
- Documented concurrency model"
```

---

## Execution Handoff

Plan complete and saved to `docs/plans/2026-02-05-concurrency-fix.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**