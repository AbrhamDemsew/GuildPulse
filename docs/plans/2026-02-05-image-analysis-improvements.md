# Image Analysis Improvements Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Improve image analysis capabilities in the Discord bot with better error handling, logging, and multimodal processing

**Architecture:** Follow Clean Architecture principles - enhance the OpenAI adapter for robust image handling, add preprocessing in bot layer, and ensure tests cover edge cases

**Tech Stack:** Python 3.14, discord.py, OpenAI API, pytest

---

## Overview

The bot already has basic image handling, but it needs improvements:
1. Better handling of image URLs in OpenAI adapter
2. Better logging when images are processed
3. Better error handling for malformed attachments

---

## Task 1: Add Image Size Validation in Bot

**Files:**
- Modify: `src/frameworks_drivers/discord/bot.py:78-83`

**Step 1: Update image URL extraction with size check**

```python
# Current code (lines 78-83):
image_urls: tuple[str, ...] = tuple(
    attachment.url
    for attachment in message.attachments
    if attachment.content_type and attachment.content_type.startswith("image/")
)

# Update to include size check (max 10MB for OpenAI):
image_urls: tuple[str, ...] = tuple(
    attachment.url
    for attachment in message.attachments
    if attachment.content_type and attachment.content_type.startswith("image/")
    and (attachment.size is None or attachment.size <= 10 * 1024 * 1024)
)
```

**Step 2: Run test to verify bot still works**

```bash
cd /Users/nclsp/work/perso/py-besto-bot
python3 -m pytest tests/frameworks_drivers/test_discord_bot.py::TestHandleMessageProcessing -v
```
Expected: All tests pass

**Step 3: Commit**

```bash
git add src/frameworks_drivers/discord/bot.py
git commit -m "feat: add image size validation (max 10MB)"
```

---

## Task 2: Add Logging for Image Processing

**Files:**
- Modify: `src/frameworks_drivers/discord/bot.py:50-70`

**Step 1: Add image count logging**

```python
# Add after image_urls extraction:
if image_urls:
    logger.info(f"Detected {len(image_urls)} image(s) in message from {author_name}")
```

**Step 2: Run tests**

```bash
python3 -m pytest tests/frameworks_drivers/test_discord_bot.py::TestHandleMessageProcessing -v
```
Expected: All tests pass

**Step 3: Commit**

```bash
git add src/frameworks_drivers/discord/bot.py
git commit -m "feat: add logging for image detection"
```

---

## Task 3: Improve OpenAI Adapter Image Handling

**Files:**
- Modify: `src/infrastructure/ai/openai/adapter.py:23-45`

**Step 1: Update image handling to handle edge cases**

```python
# Update the image_urls handling section:
if image_urls:
    last_message = api_messages[-1]
    if last_message["role"] == "user":
        text_content = last_message["content"]
        multimodal_content: list[dict[str, Any]] = [{"type": "text", "text": text_content}]
        for url in image_urls:
            multimodal_content.append({"type": "image_url", "image_url": {"url": url}})
        api_messages[-1] = {"role": "user", "content": multimodal_content}
```

**Step 2: Run tests**

```bash
python3 -m pytest tests/infrastructure/test_openai_adapter.py -v
```
Expected: All tests pass

**Step 3: Commit**

```bash
git add src/infrastructure/ai/openai/adapter.py
git commit -m "refactor: improve image URL handling in OpenAI adapter"
```

---

## Task 4: Add Image Processing Unit Test

**Files:**
- Create: `tests/infrastructure/test_image_processing.py`

**Step 1: Write the failing test**

```python
"""Tests for image processing in OpenAI adapter."""

from unittest.mock import Mock

from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent
from src.infrastructure.ai.openai.adapter import OpenAIServiceAdapter
from src.infrastructure.ai.openai.client import OpenAIClient


class TestImageProcessing:
    """Tests for image processing functionality."""

    def test_image_processing_with_multiple_images(self):
        """Test processing with multiple image URLs."""
        mock_client = Mock(spec=OpenAIClient)
        mock_client.chat_completion.return_value = "Analysis complete"

        adapter = OpenAIServiceAdapter(mock_client)
        channel = Channel(channel_id=123)
        channel.add_message(Message(role="user", content=MessageContent(value="What's in these images?")))

        image_urls = (
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg",
            "https://example.com/image3.jpg"
        )

        result = adapter.generate_reply(channel, image_urls=image_urls)

        call_args = mock_client.chat_completion.call_args[0][0]
        last_message = call_args[-1]
        assert last_message["role"] == "user"
        assert isinstance(last_message["content"], list)
        assert len(last_message["content"]) == 4  # 1 text + 3 images
        assert last_message["content"][0]["type"] == "text"
        assert last_message["content"][1]["type"] == "image_url"
        assert last_message["content"][2]["type"] == "image_url"
        assert last_message["content"][3]["type"] == "image_url"

    def test_image_processing_with_single_image(self):
        """Test processing with single image URL."""
        mock_client = Mock(spec=OpenAIClient)
        mock_client.chat_completion.return_value = "Single image analysis"

        adapter = OpenAIServiceAdapter(mock_client)
        channel = Channel(channel_id=123)
        channel.add_message(Message(role="user", content=MessageContent(value="Analyze this image")))

        image_urls = ("https://example.com/single.jpg",)

        result = adapter.generate_reply(channel, image_urls=image_urls)

        call_args = mock_client.chat_completion.call_args[0][0]
        last_message = call_args[-1]
        assert isinstance(last_message["content"], list)
        assert len(last_message["content"]) == 2  # 1 text + 1 image

    def test_image_processing_with_no_images(self):
        """Test processing without image URLs."""
        mock_client = Mock(spec=OpenAIClient)
        mock_client.chat_completion.return_value = "Normal response"

        adapter = OpenAIServiceAdapter(mock_client)
        channel = Channel(channel_id=123)
        channel.add_message(Message(role="user", content=MessageContent(value="Hello")))

        result = adapter.generate_reply(channel, image_urls=())

        call_args = mock_client.chat_completion.call_args[0][0]
        last_message = call_args[-1]
        assert last_message["content"] == "Hello"
        assert isinstance(last_message["content"], str)

    def test_image_processing_with_empty_channel(self):
        """Test processing with no existing messages."""
        mock_client = Mock(spec=OpenAIClient)
        mock_client.chat_completion.return_value = "Response"

        adapter = OpenAIServiceAdapter(mock_client)
        channel = Channel(channel_id=123)

        image_urls = ("https://example.com/image.jpg",)

        result = adapter.generate_reply(channel, image_urls=image_urls)

        # With no user message, images should be ignored (or error)
        call_args = mock_client.chat_completion.call_args[0][0]
        assert len(call_args) == 1  # Only system prompt
```

**Step 2: Run test to verify it fails**

```bash
python3 -m pytest tests/infrastructure/test_image_processing.py -v
```
Expected: FAIL with "No tests collected" (file needs to be in tests folder)

**Step 3: Move test file to correct location**

```bash
mv tests/infrastructure/test_image_processing.py tests/infrastructure/test_image_processing.py
```

**Step 4: Run test again**

```bash
python3 -m pytest tests/infrastructure/test_image_processing.py -v
```
Expected: Test fails as expected (mock_client.chat_completion not called yet)

**Step 5: Run existing tests to ensure no regression**

```bash
python3 -m pytest tests/infrastructure/test_openai_adapter.py -v
```
Expected: All existing tests still pass

**Step 6: Commit**

```bash
git add tests/infrastructure/test_image_processing.py
git commit -m "test: add image processing tests"
```

---

## Task 5: Update OpenAI Adapter for Edge Cases

**Files:**
- Modify: `src/infrastructure/ai/openai/adapter.py:23-45`

**Step 1: Add edge case handling**

```python
def generate_reply(self, channel: "Channel", image_urls: tuple[str, ...] = ()) -> str:
    """Generate a reply using OpenAI."""
    messages = channel.get_messages_for_api()
    system_prompt = self.settings.CHAT_SYSTEM_PROMPT
    api_messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]
    for msg in messages[-100:]:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    if image_urls:
        # Find the last user message to attach images
        last_user_idx = None
        for i in range(len(api_messages) - 1, -1, -1):
            if api_messages[i]["role"] == "user":
                last_user_idx = i
                break

        if last_user_idx is not None:
            text_content = api_messages[last_user_idx]["content"]
            multimodal_content: list[dict[str, Any]] = [{"type": "text", "text": text_content}]
            for url in image_urls:
                multimodal_content.append({"type": "image_url", "image_url": {"url": url}})
            api_messages[last_user_idx] = {"role": "user", "content": multimodal_content}

    return self.client.chat_completion(api_messages)
```

**Step 2: Run tests**

```bash
python3 -m pytest tests/infrastructure/test_image_processing.py -v
python3 -m pytest tests/infrastructure/test_openai_adapter.py -v
```
Expected: All tests pass

**Step 3: Commit**

```bash
git add src/infrastructure/ai/openai/adapter.py
git commit -m "refactor: handle edge cases for image URL attachment"
```

---

## Task 6: Add Documentation

**Files:**
- Create: `docs/image-handling.md`

**Step 1: Create documentation file**

```markdown
# Image Handling in py-besto-bot

## Overview

The bot supports analyzing images attached to messages using multimodal AI models.

## How It Works

1. **Discord Message Processing** (`src/frameworks_drivers/discord/bot.py`)
   - Images are detected from `message.attachments` with content type starting with "image/"
   - Image size is validated (max 10MB)

2. **OpenAI Adapter** (`src/infrastructure/ai/openai/adapter.py`)
   - Images are attached to the most recent user message
   - Uses OpenAI's multimodal content format with text + image_url entries

## Image Format

Images are sent to OpenAI in this format:

```json
{
  "role": "user",
  "content": [
    {"type": "text", "text": "User's message"},
    {"type": "image_url", "image_url": {"url": "https://cdn.discordapp.com/attachments/.../image1.jpg"}},
    {"type": "image_url", "image_url": {"url": "https://cdn.discordapp.com/attachments/.../image2.jpg"}}
  ]
}
```

## Usage

1. User sends a message with image attachments
2. Bot detects images and includes them in the AI request
3. AI analyzes the images and generates a response
4. Response is sent to the channel

## Limitations

- Maximum 10MB per image (Discord limit)
- Images are attached to the most recent user message
- Only the last 100 messages are included in conversation history
```

**Step 2: Run tests to ensure everything works**

```bash
python3 -m pytest tests/ -v -o addopts=""
```
Expected: All 205 tests pass

**Step 3: Final commit**

```bash
git add docs/image-handling.md
git commit -m "docs: add image handling documentation"
```

---

## Test Results Summary

After all changes, run:

```bash
python3 -m pytest tests/ -v -o addopts=""
```

Expected: All tests pass with new image processing tests added