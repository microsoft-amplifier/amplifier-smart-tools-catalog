---
smart_tool_format: 1
name: smart-tool-creator
version: 0.2.1
description: >
  Creates, validates, and evaluates smart tools that follow the Amplifier Smart Tool
  Spec. Use when you want to package domain expertise as a smart tool, check that an
  existing one conforms to the spec, or measure how well its smart capabilities work.
use_cases:
  - Scaffold a new smart tool that is ready to push and conforms to the spec
  - Check an existing smart tool against the spec and its conformance kit
  - Build and run evaluations for a smart tool's model-backed capabilities
platforms:
  - linux
  - macos
  - windows
requires:
  - name: uv
    purpose: >
      Installs the tool, runs its checks, and runs the conformance kit; every capability
      needs it.
    install: https://docs.astral.sh/uv/
  - name: git
    purpose: >
      init creates the new tool's repository and clones its references.
    install: https://git-scm.com/
  - name: prek
    purpose: >
      Runs the lint and format checks of the tool being extended by add-smart-capability.
      Without it that check is skipped.
    optional: true
    install: https://github.com/j178/prek
  - name: gh
    purpose: >
      Generates the token that signs in to GitHub Copilot, for the copilot agent provider.
      Without it, the model-backed capabilities cannot authenticate through copilot.
    optional: true
    install: https://cli.github.com/
  - name: github-copilot-subscription
    purpose: >
      A Copilot subscription on the account signed in to gh powers the model-backed
      capabilities, for the copilot agent provider.
    optional: true
    install: https://github.com/github/copilot-cli#prerequisites
  - name: amplifier-agent-provider-credentials
    purpose: >
      The credentials of the model provider the amplifier-agent agent provider calls, for
      instance OPENAI_API_KEY for its default model. Without them, the model-backed
      capabilities cannot run through amplifier-agent. See the full list of options at the install link.
    optional: true
    install: https://github.com/microsoft/amplifier-agent/blob/main/docs/providers.md
  - name: codex-sign-in
    purpose: >
      The Codex CLI signed in with ChatGPT or an API key, for the codex agent provider.
      Without it, the model-backed capabilities cannot run through codex.
    optional: true
    install: https://developers.openai.com/codex/auth
  - name: claude-credentials
    purpose: >
      ANTHROPIC_API_KEY, or a cloud provider's credentials, for the claude agent provider.
      Without them, the model-backed capabilities cannot run through claude.
    optional: true
    install: https://code.claude.com/docs/en/agent-sdk/quickstart
---

A smart tool for building smart tools. It scaffolds the structure the
[spec](https://github.com/microsoft/amplifier-smart-tools) requires, checks a tool against
the spec, and evaluates the tool's model-backed capabilities in isolation.

**The library is the tool.** `smart_tool_creator.lib` holds every capability. The CLI is a
thin wrapper over it, so anything you can do from the shell you can also do from Python.

## When to reach for it

- You have domain expertise in a harness, a bundle, or a set of skills and want to share it
  as a standalone tool that any agent can call.
- You built a smart tool and want to know whether it conforms to the spec before publishing it.
- You want evidence that a smart tool's model-backed capabilities work, independent of the
  harness that calls it.

Not for:

- Generating a general-purpose project, or as a template engine.
- Hosting or distributing smart tools; that is the catalog's job.
- Making a smart tool discoverable inside a host like Copilot or Claude Code; the catalog's
  skill does that.

## Before writing code

Every capability has its own skill. Read `smart-tool-creator <command> --help` before calling
it: it carries the arguments, a worked invocation, the result, and the failures. Do not fill
gaps from memory. The library source beside this file, `lib.py`, carries the signatures. The
repository's `docs/01-library.md` and `docs/02-cli.md` carry the rest.

## Install

```bash
# as a CLI
uv tool install "amplifier-smart-tool-creator[all] @ git+https://github.com/microsoft/amplifier-smart-tool-creator"

# as a library
uv add "amplifier-smart-tool-creator[all] @ git+https://github.com/microsoft/amplifier-smart-tool-creator"

# once, without installing
uvx --from "amplifier-smart-tool-creator[all] @ git+https://github.com/microsoft/amplifier-smart-tool-creator" smart-tool-creator --help
```

`[all]` brings every agent provider the model-backed capabilities run through. Alternatives:

```bash
# Only the GitHub Copilot agent provider
uv tool install "amplifier-smart-tool-creator[copilot] @ git+https://github.com/microsoft/amplifier-smart-tool-creator"
# Only the Amplifier Agent agent provider
uv tool install "amplifier-smart-tool-creator[amplifier-agent] @ git+https://github.com/microsoft/amplifier-smart-tool-creator"
# Only the Codex agent provider
uv tool install "amplifier-smart-tool-creator[codex] @ git+https://github.com/microsoft/amplifier-smart-tool-creator"
# Only the Claude agent provider
uv tool install "amplifier-smart-tool-creator[claude] @ git+https://github.com/microsoft/amplifier-smart-tool-creator"
# Deterministic capabilities only
uv tool install git+https://github.com/microsoft/amplifier-smart-tool-creator
```

Verify with `smart-tool-creator manifest`, which needs no credentials.

## Prerequisites

Deterministic capabilities need only `uv`. Model-backed capabilities run through an agent
provider, picked with `--agent-provider`, or the first installed of `copilot`,
`amplifier-agent`, `codex`, and `claude` when omitted:

- `copilot`: GitHub Copilot, signed in as the GitHub CLI's user. `gh` must be installed and
  `gh auth login` completed with an account that has a Copilot subscription.
- `amplifier-agent`: [Amplifier Agent](https://github.com/microsoft/amplifier-agent), calling
  the model provider named in `--model <provider>/<model>` with that provider's credentials,
  for instance `OPENAI_API_KEY` for the default `openai/...` models. See its
  [providers](https://github.com/microsoft/amplifier-agent/blob/main/docs/providers.md).
- `codex`: [OpenAI Codex](https://github.com/openai/codex), with the user's Codex configuration.
  The Codex CLI must be signed in with ChatGPT or an API key, see
  [authentication](https://developers.openai.com/codex/auth).
- `claude`: the [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python), with the
  user's Claude Code settings. Needs `ANTHROPIC_API_KEY`, or Amazon Bedrock, Claude Platform on AWS,
  Google Cloud's Agent Platform, or Microsoft Foundry credentials, see
  [authentication](https://code.claude.com/docs/en/agent-sdk/quickstart).

Runs on Linux, macOS, and Windows.

## Straight and smart paths

Deterministic capabilities run with no provider configured. 
Model-backed capabilities go through GitHub Copilot, Amplifier Agent, Codex, or Claude. 
A model-backed capability with nothing configured  fails immediately.

## Output and failure contract

Results go to stdout, diagnostics to stderr. A failure prints a message naming what went
wrong and how to fix it, and exits non-zero: 1 for a failure the tool can name, 2 for a bad
invocation. Never treat an empty result as success.

## Choosing a surface

Import the library from Python. Shell out to the CLI from anything that cannot import Python
in-process: a shell script, a CI job, or an agent that can run commands but not load a Python
object. Both reach the same capabilities.

To chain capabilities, here or with other smart tools, write a script against the libraries
and pass return values between calls. The CLI's text output is for reading, not for parsing.
