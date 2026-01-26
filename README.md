# duckdb-kb: An AI That Actually Knows You

> **Location matters:** Click "Use this template" to create your own private copy, then clone it to your home directory (`~/duckdb-kb`). Always run Claude Code from that location. The MCP expects this path. See [Quick Start Alias](#quick-start-alias) at the end for a one-command setup.

---

## What You're Used To

You open ChatGPT. You ask a question. It answers. Maybe you have a few back-and-forth exchanges. Then you close the tab and move on.

Next time you come back, it's a blank slate. You can scroll through old chats, sure. And maybe you turned on that "memory" feature that remembers a few things about you.

But try asking it what you talked about three months ago. Try asking it to connect something from last week to something from last month. Try asking it to notice you've asked the same question four times.

It can't. The memory feature gives it a collection of loosely-held facts. Not a real picture, especially across months/years.

---

## What This Is

**duckdb-kb** is a personal knowledge base that sits alongside Claude (Anthropic's AI). It gives Claude genuine, structured memory - not impressions, but records.

- Every conversation gets logged
- Key facts get filed where you can find them
- Decisions get saved with the reasoning behind them
- Mistakes get tracked so they don't repeat

When you start a new conversation, Claude loads all this context first. It knows who you are, what you're working on, what happened last time, and what's still pending.

**What it looks like:** You work in a terminal window (a text interface - think of it like texting, but on your computer). You type messages, Claude responds. The difference is what Claude knows before you type anything.

---

## Who This Is For

Let me be direct: this isn't for everyone.

**This is for you if:**
- You already use AI frequently and want more from it
- You're comfortable with (or willing to learn) a command-line interface
- You have ongoing work that requires context - projects, people, history
- You're willing to invest an afternoon in setup for long-term payoff

**This probably isn't for you if:**
- You use ChatGPT occasionally for quick questions
- You want something that works out of the box with no setup
- The phrase "terminal window" makes you want to close this page

Still here? Good.

---

## What Changes

**Before:**

You: *"I need to write an email to my coworker about the project we discussed. She prefers bullet points and hates corporate jargon. The deadline moved to Friday and I need to explain why without throwing anyone under the bus..."*

AI: *"I'd be happy to help you draft that email! Here's a version..."*

*(Two months later)*

You: *"Can you help me follow up on that email I sent? The one about the deadline?"*

AI: *"Of course! Could you remind me of the context?"*

---

**After:**

You: *"Can you help me follow up with Sarah about the X project?"*

AI: *"The infrastructure migration? Last email you mentioned the Friday deadline shift. She responded but you haven't replied yet. Want me to draft something? I'll keep it casual - she hates corporate speak."*

---

The AI knows Sarah. Knows the project. Knows your last exchange. Knows her preferences. You didn't re-explain any of it.

---

## How It Actually Works

**The knowledge base** is a collection of files on your computer. Plain text (you can read it), organized by type:
- References (people, systems, facts)
- Patterns (how you do things)
- Projects (what you're working on)
- Logs (what happened each session)
- Transcripts (actual conversation records)

**A session** is one continuous work period. You start with `/open` - Claude loads your context. You work. When you're done, you type `/close` - Claude saves what happened and sets up the handoff for next time.

**You control everything.** The files are on your machine. You can read them, edit them, delete them. You decide what gets saved. This is your profile of yourself - not someone else's profile of you.

---

## Examples Beyond Work

This isn't just for office stuff.

**Personal projects:** You're learning Spanish. Claude remembers what you've covered, what trips you up, what methods work for you.

**Life admin:** You're dealing with a complicated insurance claim. Claude remembers the timeline, the people you've talked to, what they said, what's still unresolved.

**Creative work:** You're writing a novel. Claude remembers your characters, plot threads, the feedback you got, the changes you decided to make.

**Health stuff:** You're tracking symptoms for a doctor's appointment. Claude remembers what you reported when, so you can walk in with an actual history.

The value is anywhere context matters and accumulates over time.

---

## Make It Yours

The examples above aren't features - they're conversations you could have.

Want to track your runs? Your diet? Your reading list? Sleep patterns? You don't need a specialized app. You describe what you want to track, Claude helps you design a structure, and the KB becomes that thing.

This isn't a product with a fixed feature set. It's a substrate that grows with you through dialogue.

---

## Share With Your Team

Your knowledge base is personal by default. But you can share specific entries with colleagues.

**How it works:** You create a shared Git repository (like `team-patterns`) and clone it into your `markdown/` folder. Claude automatically pulls changes when you start a session and pushes your contributions when you close.

**What you share, you control.** Want to share useful patterns but keep your personal notes private? Easy - only entries in the shared folder get synced. Your main knowledge base stays yours.

**No central server.** It's just Git. Your team can use GitHub, GitLab, or any Git host. Each person maintains their own knowledge base; the shared repo is just an overlay.

This works well for:
- Team patterns and best practices
- Shared reference documentation
- Collaborative troubleshooting guides

---

## The Investment

**Setup:** Plan for an afternoon. You'll install Claude Code (a free tool from Anthropic), download the knowledge base, and run through initial configuration. If you've never used a terminal before, budget extra time or find someone to help.

**Ongoing:** A few extra seconds per session. `/open` at the start, `/close` at the end. That's it.

**Cost:** Claude Pro subscription ($20/month). The knowledge base itself is free.

**Learning curve:** Gentle if you're used to command lines. Steeper if you're not. The system teaches you as you go, but it's not point-and-click.

---

## What About Privacy?

Honest answer: your conversations go through Anthropic's servers. That's how Claude works. This doesn't change that.

What this *does* give you: your own copy of everything, structured and searchable. The knowledge base lives on your computer. You can back it up, export it, take it with you.

You're not just renting context from a company - you're building something you own.

---

## The Moment It Clicks

It usually happens in the second week.

You start a session. Claude asks about something you mentioned days ago. Or flags that you're circling back to a problem you already solved. Or remembers a detail you'd forgotten yourself.

That's when you realize: this isn't a chatbot. It's becoming a partner that actually knows your world.

---

## Ready?

If this sounds like what you want, the setup.md guide walks Claude through everything step by step.

---

## Quick Start Alias

Create an alias so you always launch Claude from the right place.

**Mac / Linux (bash):** Add to `~/.bashrc` or `~/.bash_profile`:
```bash
alias kb='cd ~/duckdb-kb && claude'
```

**Mac / Linux (zsh):** Add to `~/.zshrc`:
```zsh
alias kb='cd ~/duckdb-kb && claude'
```

**Windows (PowerShell):** Add to your PowerShell profile (`$PROFILE`):
```powershell
function kb { Set-Location "$HOME\duckdb-kb"; claude }
```

**Windows (Command Prompt):** Create a batch file `kb.bat` in a folder on your PATH:
```batch
@echo off
cd /d "%USERPROFILE%\duckdb-kb" && claude
```

After adding, restart your terminal (or run `source ~/.zshrc` etc.). Then just type `kb` to start.

> **Why this matters:** The MCP server and workflow commands (`/open`, `/close`, `/audit`) expect to run from `~/duckdb-kb`. Cloning elsewhere or running from a different directory will break things.