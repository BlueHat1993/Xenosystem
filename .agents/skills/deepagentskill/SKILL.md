---
name: deepagentskill
description: A skill that implements a Deep Agents research agent in this working directory.
---

<!-- Tip: Use /create-skill in chat to generate content with agent assistance -->
Build a Deep Agents research agent in this working directory by following the Deep Agents quickstart.

## Step 1: Read the guide

Detect whether this project uses Python or TypeScript/JavaScript. Fetch and follow the matching page; treat it as the source of truth for package names, model strings, search-tool setup, and code:

* Python: [https://docs.langchain.com/oss/python/deepagents/quickstart.md](https://docs.langchain.com/oss/python/deepagents/quickstart.md)
* TypeScript: [https://docs.langchain.com/oss/javascript/deepagents/quickstart.md](https://docs.langchain.com/oss/javascript/deepagents/quickstart.md)

## Step 2: Install dependencies

Install `deepagents` (and `langchain` / `@langchain/core` on TypeScript) with the package manager already used in this project. Add Tavily only if the user is not using a Google, OpenAI, or Anthropic built-in provider search tool.

## Step 3: Configure model credentials

Check for a supported provider API key (for example `GOOGLE_API_KEY`, `OPENAI_API_KEY`, or `ANTHROPIC_API_KEY`). If none is set, ask the user which provider to use, then stop and wait while they create a key and set it in the shell or a `.env` file. Do not invent, hardcode, or commit API keys. If they need Tavily, ask them to set `TAVILY_API_KEY` the same way.

## Step 4: Implement the research agent

Follow the quickstart steps in order:

1. Create the internet search tool (prefer the provider built-in search tool when the chosen model supports it; otherwise use Tavily).
2. Call `create_deep_agent` with the search tool, a `provider:model` string (or initialized model) from the guide, and the research system prompt shown on the page.
3. Optionally enable LangSmith tracing by asking the user to set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` themselves.
4. Run the agent on a sample research query from the guide and print the final response.

## Rules

* Stay scoped to this quickstart. Do not add Managed Deep Agents deployment, evals, or unrelated frameworks.
* Prefer provider built-in web search when available; use Tavily only when needed.
* Ask rather than guess when a secret, provider choice, or project convention is unclear.