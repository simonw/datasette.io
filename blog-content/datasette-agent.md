---
title: Datasette Agent, an extensible AI assistant for Datasette
datetime_utc: 2026-05-21 17:53:55
author: Simon Willison
author_url: https://simonwillison.net
---

Today we are releasing [Datasette Agent](https://agent.datasette.io/), an open source plugin for Datasette that provides an extensible AI assistant for interacting with your SQLite databases.

Datasette Agent integrates [LLM](https://llm.datasette.io/) into Datasette, providing support for hundreds of different tool-calling models - from frontier vendors like OpenAI, Anthropic and Google Gemini, through to open weight models that you can run on your own hardware.

The result is a conversational interface for answering questions about your data in SQLite, enhanced by additional plugins to add visualizations and other custom tools.

## Datasette Agent in action

This [video demo](https://www.youtube.com/watch?v=AFZKp6hbFjI) shows how Datasette Agent works and what you can do with it.

<lite-youtube videoid="AFZKp6hbFjI" playlabel="Play: Datasette Agent demo" style="background-image: url('https://i.ytimg.com/vi/AFZKp6hbFjI/maxresdefault.jpg');"></lite-youtube>

You can try the demo yourself [on agent.datasette.io](https://agent.datasette.io/). This requires you to sign in with a GitHub account to help prevent abuse.

The demo uses [Gemini 3.1 Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite) via the [llm-gemini](https://github.com/simonw/llm-gemini) plugin. That model is fast and inexpensive, and our testing has shown it to be proficient at the SQLite queries needed by Datasette Agent.

## Running Datasette Agent locally

If you want to try out Datasette Agent yourself, the easiest way to do so is using `uv`.

Here's how to run it with your own OpenAI API key. First grab a demo database:
```bash
wget https://datasette.io/legislators.db
```
Then set your API key as an environment variable:
```bash
export OPENAI_API_KEY="sk-..."
```
And start Datasette running like this:
```bash
uvx --prerelease=allow --with datasette-agent \
  datasette -s plugins.datasette-llm.default_model gpt-5.5 \
  --internal internal.db --root legislators.db
```
This will provide you with a link to sign in as root on your local machine, and set `gpt-5.5` as the default model.

If you have OpenAI Codex installed and configured, you can use [llm-openai-via-codex](https://github.com/simonw/llm-openai-via-codex) to avoid needing a separate API key and to bill your experiments to your existing ChatGPT subscription:

```bash
uvx --prerelease=allow --with datasette-agent --with llm-openai-via-codex \
  datasette -s plugins.datasette-llm.default_model openai-codex/gpt-5.5 \
  --internal internal.db --root legislators.db
```
Datasette Agent also works with local models. Here's how to run it with Qwen 3.5 9B served via a local installation of [LM Studio](https://lmstudio.ai/):
```bash
uvx --prerelease=allow \
  --with datasette-agent --with llm-lmstudio \
  datasette --internal internal.db --root \
  legislators.db \
  -s plugins.datasette-llm.default_model lmstudio/qwen3.5-9b
```

## Plugins for your agent

The Datasette ecosystem is built on plugins, and Datasette Agent continues that tradition. We are launching with three plugins:

- [datasette-agent-charts](https://github.com/datasette/datasette-agent-charts), shown in the video, adds charts to Datasette Agent, powered by [Observable Plot](https://observablehq.com/plot/).
- [datasette-agent-openai-imagegen](https://github.com/datasette/datasette-agent-openai-imagegen) adds an image generation tool to Datasette Agent using [ChatGPT Images 2.0](https://openai.com/index/introducing-chatgpt-images-2-0/).
- [datasette-agent-sprites](https://github.com/datasette/datasette-agent-sprites) provides tools for executing code in a [Fly Sprites](https://sprites.dev/) persistent sandbox.

Plugins are easy to build. The README includes [detailed documentation](https://github.com/datasette/datasette-agent/blob/main/README.md#registering-additional-tools-from-plugins), and we've found that coding agents like Codex and Claude Code can spin up new plugins really quickly.

We have several exciting plugins in the pipeline - expect to hear more about these over the next few days and weeks.

## Come hack with us

Today's alpha release is just the start. We're actively iterating on Datasette Agent and extra plugins for it right now - come and join us on Discord in the [#datasette-agent channel](https://discord.gg/hdxyusUFv) to learn more and share what you are planning to build.
