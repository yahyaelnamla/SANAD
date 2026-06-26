# Fanar API Documentation for Cursor

This document provides a comprehensive guide to the Fanar API, specifically formatted for use within Cursor or other AI coding assistants. It includes all available endpoints, models, rate limits, and code examples to facilitate seamless integration.

## 1. Overview

The Fanar API provides access to various AI capabilities, including chat completion, text-to-speech (TTS), speech-to-text (STT), image generation, translation, poem generation, moderation, and tokenization.

- **Base URL:** `https://api.fanar.qa`

- **Authentication:** Bearer token in the `Authorization` header (`Authorization: Bearer YOUR_API_KEY` )

- **Compatibility:** Many endpoints (like Chat, TTS, STT, Image Generation) are compatible with the official OpenAI library. When using the OpenAI SDK, set the `base_url` to `https://api.fanar.qa/v1`.

## 2. Rate Limits

The API enforces rate limits to ensure optimal performance. Exceeding these limits results in a `429 Too Many Requests` status code.

| Model | Rate Limit |
| --- | --- |
| Fanar |
| Fanar-S-1-7B |
| Fanar-C-1-8.7 |
| Fanar-C-2-27B |  |
| Fanar-Sadiq |  |
| Fanar-Sadiq-Agentic |  |
| Fanar-Sadiq-TTS-1 |  |
| Fanar-Oryx-IVU-2 |  |
| Fanar-Aura-TTS-2 |  |
| Fanar-Aura-STT-1 |  |
| Fanar-Aura-STT-LF-1 |  |
| Fanar-Oryx-IG-2 |  |
| Fanar-Guard-2 |  |
| Fanar-Shaheen-MT-1 |  |
| Fanar-Diwan |  |

## 3. Endpoints

### 3.1 Chat Completions

Create a chat completion based on a sequence of messages. Compatible with the OpenAI library.

- **Endpoint:** `POST /v1/chat/completions`

- **Content-Type:** `application/json`

**Supported Models:**

- `Fanar`

- `Fanar-S-1-7B`

- `Fanar-C-1-8.7B`

- `Fanar-C-2-27B` (Supports `enable_thinking` parameter with additional authorization )

- `Fanar-Sadiq` (Replaces `Islamic-RAG`. Uses `book_names`, `exclude_sources`, `filter_sources`)

- `Fanar-Sadiq-Agentic`

- `Fanar-Oryx-IVU-2`

**Key Parameters:**

- `model` (string, required): The model to use.

- `messages` (array, required): Array of message objects (role, content).

- `enable_thinking` (boolean, optional): Enable thinking role (only for `Fanar-C-2-27B`).

- `book_names` (array of strings, optional): For `Fanar-Sadiq` model.

- `exclude_sources` / `filter_sources` (array, optional): For `Fanar-Sadiq` model.

**cURL Example:**

```bash
curl -X POST "https://api.fanar.qa/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY_HERE" \
  -d '{
    "model": "Fanar",
    "messages": [
      {
        "role": "user",
        "content": "Your message here"
      }
    ]
  }'
```

### 3.2 Audio: Text-to-Speech (TTS )

Generates audio from input text. Compatible with the OpenAI library.

- **Endpoint:** `POST /v1/audio/speech`

- **Content-Type:** `application/json`

**Supported Models:**

- `Fanar-Aura-TTS-2`

- `Fanar-Sadiq-TTS-1` (For Quranic text, use `quran_reciter` parameter)

**Key Parameters:**

- `model` (string, required): The TTS model.

- `input` (string, required): Text to generate audio for.

- `voice` (string, required): Voice to use (e.g., `Amelia`, `Hamad`, `Abdulrahman`, `Radwa`).

- `response_format` (string, optional): `mp3` or `wav`.

- `stream` (boolean, optional): Stream the audio.

- `with_emotion` (boolean, optional): Enable emotional speech (only for `Fanar-Aura-TTS-2` and supported voices like `Abdulrahman`, `Radwa`).

- `quran_reciter` (string, optional): For `Fanar-Sadiq-TTS-1` (e.g., `abdul-basit`, `maher-al-muaiqly`, `mahmoud-al-husary`).

**cURL Example:**

```bash
curl -X POST "https://api.fanar.qa/v1/audio/speech" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_API_KEY" \
--output greeting.mp3 \
-d '{
  "model": "Fanar-Aura-TTS-2",
  "input": "Hello! I hope you are having a wonderful day.",
  "voice": "Amelia",
  "response_format": "mp3"
}'
```

### 3.3 Audio: Speech-to-Text (STT )

Transcribes audio into text. Compatible with the OpenAI library.

- **Endpoint:** `POST /v1/audio/transcriptions`

- **Content-Type:** `multipart/form-data`

**Supported Models:**

- `Fanar-Aura-STT-1`: For short audio clips (up to 20–30 seconds).

- `Fanar-Aura-STT-LF-1`: For long-form transcription.

**Key Parameters:**

- `file` (binary, required): The audio file to transcribe.

- `model` (string, required): The STT model.

- `format` (string, optional): `text`, `srt`, or `json`. (`Fanar-Aura-STT-1` only supports `text`).

**cURL Example:**

```bash
curl -X POST "https://api.fanar.qa/v1/audio/transcriptions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.wav" \
  -F "model=Fanar-Aura-STT-1"
```

### 3.4 Audio: Voices Management

Manage available and personalized voices.

- **List Voices:** `GET /v1/audio/voices`

- **Create Voice:** `POST /v1/audio/voices` (Requires special authorization )

- **Delete Voice:** `DELETE /v1/audio/voices/{name}` (Requires special authorization)

### 3.5 Image Generation

Creates an image given a text prompt. Compatible with the OpenAI library.

- **Endpoint:** `POST /v1/images/generations`

- **Content-Type:** `application/json`

**Supported Models:**

- `Fanar-Oryx-IG-2`

**Key Parameters:**

- `model` (string, required): The image generation model.

- `prompt` (string, required): Text description of the desired image.

- `revise` (boolean, optional): Automatically revise prompt for better results.

**cURL Example:**

```bash
curl -X POST "https://api.fanar.qa/v1/images/generations" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_API_KEY" \
-d '{
  "model": "Fanar-Oryx-IG-2",
  "prompt": "A serene sunset over a mountain lake with reflections of colorful clouds and pine trees"
}'
```

### 3.6 Translations

Translate text between English and Arabic.

- **Endpoint:** `POST /v1/translations`

- **Content-Type:** `application/json`

**Supported Models:**

- `Fanar-Shaheen-MT-1`

**Key Parameters:**

- `model` (string, required ): The translation model.

- `text` (string, required): Text to translate (max 4,000 words).

- `langpair` (string, required): `en-ar` or `ar-en`.

- `preprocessing` (string, optional): `default`, `preserve_html`, `preserve_whitespace`, `preserve_whitespace_and_html`.

**cURL Example:**

```bash
curl -X POST "https://api.fanar.qa/v1/translations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "Fanar-Shaheen-MT-1",
    "text": "Your text here",
    "langpair": "ar-en",
    "preprocessing": "default"
  }'
```

### 3.7 Poem Generation

Creates a poem given a prompt. Compatible with the OpenAI library.

- **Endpoint:** `POST /v1/poems/generations`

- **Content-Type:** `application/json`

**Supported Models:**

- `Fanar-Diwan`

**Key Parameters:**

- `model` (string, required ): The poem generation model.

- `prompt` (string, required): Text description of the desired poem.

**cURL Example:**

```bash
curl -X POST "https://api.fanar.qa/v1/poems/generations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "Fanar-Diwan",
    "prompt": "Your text here"
  }'
```

### 3.8 Moderations

Identify safety and cultural-awareness scores for prompt-response pairs.

- **Endpoint:** `POST /v1/moderations`

- **Content-Type:** `application/json`

**Supported Models:**

- `Fanar-Guard-2`

**Key Parameters:**

- `model` (string, required ): The moderation model.

- `prompt` (string, required): The prompt.

- `response` (string, required): The model's response.

**cURL Example:**

```bash
curl -X POST "https://api.fanar.qa/v1/moderations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "Fanar-Guard-2",
    "prompt": "Your prompt here",
    "response": "Response from the model here"
  }'
```

### 3.9 Tokens

Get token count for a given text.

- **Endpoint:** `POST /v1/tokens`

- **Content-Type:** `application/json`

**Supported Models:**

- `Fanar-S-1-7B`

- `Fanar-C-1-8.7B`

- `Fanar-C-2-27B`

**Key Parameters:**

- `model` (string, required ): The LLM model.

- `content` (string, required): The text content.

**cURL Example:**

```bash
curl -X POST "https://api.fanar.qa/v1/tokens" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "content": "Your text content here",
    "model": "Fanar-C-1-8.7B"
  }'
```

### 3.10 Models

List all available models.

- **Endpoint:** `GET /v1/models`

**cURL Example:**

```bash
curl -X GET "https://api.fanar.qa/v1/models" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## 4. Cursor Integration Tips

When using Cursor to write code interacting with the Fanar API:

1. **OpenAI SDK Compatibility:** Since many endpoints (Chat, Audio, Images, Poems ) are compatible with the OpenAI SDK, you can instruct Cursor to use the standard `openai` Python or Node.js packages. Just ensure you override the `base_url` to `https://api.fanar.qa/v1` and use the specific Fanar model names.

1. **Model Names:** Always use the exact model names provided in this documentation (e.g., `Fanar-C-2-27B`, `Fanar-Aura-TTS-2` ).

1. **Custom Endpoints:** For endpoints like Translations (`/v1/translations`) or Moderations (`/v1/moderations`), instruct Cursor to use standard HTTP clients (like `requests` in Python or `fetch` in JS/TS) as these might not map directly to standard OpenAI SDK methods.

1. **Authentication:** Remind Cursor to always include the `Authorization: Bearer YOUR_API_KEY` header.

