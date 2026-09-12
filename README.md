# n8n Personal Life Automation Suite

A self-hosted automation system that turns natural language text messages into structured actions across my calendar, health tracking, and daily planning — built end-to-end on a self-managed VPS using n8n, the Claude API, and Telegram as the primary interface.

## Overview

This project explores how far a lightweight LLM (Claude Haiku 4.5) can go as the "glue" between everyday tools — calendar, spreadsheets, and messaging — without writing a traditional backend. Instead of building custom parsing logic for every input format, the AI handles natural language interpretation, classification, and structured data extraction, while n8n orchestrates the workflow and Google Sheets acts as persistent storage.

## Architecture

```
┌─────────────┐      ┌──────────────────────────────┐      ┌───────────────┐
│  Telegram   │ ───▶ │   n8n (self-hosted, Docker)   │ ───▶ │ Google Calendar│
│  (bots)     │ ◀─── │   on DigitalOcean VPS         │ ◀─── │ / Sheets API   │
└─────────────┘      │   HTTPS via Caddy + Let's     │      └───────────────┘
                      │   Encrypt                     │
                      └──────────────┬────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  Claude API       │
                            │  (Haiku 4.5)      │
                            │  parsing/classify │
                            └─────────────────┘
```

**Infrastructure:**
- DigitalOcean droplet (Ubuntu, Docker Compose)
- n8n self-hosted via Docker, reverse-proxied through Caddy for automatic HTTPS (Let's Encrypt)
- Telegram Bot API for two-way messaging (no per-message fees, unlike SMS)
- Google Calendar & Google Sheets APIs via OAuth2
- Anthropic API (Claude Haiku 4.5) for natural language parsing and content generation

## Workflows

### 1. Calendar Reminder Bot
Polls Google Calendar every 25 minutes and sends a Telegram alert for events starting soon.
- Filters out all-day events and already-started events (events that overlap the lookahead window but began in the past)
- Formats raw ISO timestamps into human-readable times (e.g., `8:15 AM`) using Luxon's `DateTime.fromISO()`

**File:** `workflows/Calendar_Bot.json`

### 2. Gamified Daily Quest Board
Runs once each morning, pulls the day's calendar events, and sends a "Solo Leveling"–style quest board via Telegram — reframing each event as a ranked quest with an EXP reward.

Extended with an RPG stat-progression system:
- Each event is classified by Claude into one of five stats: **Strength, Intelligence, Social, Vitality, Discipline**
- EXP is calculated from event duration (1 minute = 1 EXP)
- Running totals, levels, and progress bars are tracked per stat in a Google Sheet and updated daily
- Level-ups are called out automatically in the message

**File:** `workflows/To-Do_Bot.json`

### 3. Calorie & Weight Tracker
A conversational logging system — text the bot what you ate or your morning weight, in plain language, and it:
- Classifies the message (food, weight, or both) and estimates calories using Claude
- Maintains a running daily calorie total against a 3,000 kcal goal
- Appends each food description to a running daily log
- Replies with the day's total, remaining calories, and current weight

**File:** `workflows/Calorie_Weight_Watcher.json`

## Key Technical Challenges Solved

- **Caddyfile syntax debugging** — diagnosed a malformed ACME email directive causing SSL certificate issuance to fail against both Let's Encrypt and ZeroSSL
- **AI output reliability** — Claude occasionally wraps JSON responses in markdown code fences despite explicit instructions not to; added defensive stripping (`.replace(/```json/gi, '')`) before parsing
- **n8n data flow gotchas** — diagnosed cases where Google Sheets nodes silently drop non-column fields when passing data downstream, requiring recalculation nodes inserted before final message construction
- **Stateful daily aggregation** — implemented "get existing row → merge with new data → append or update" logic in Code nodes to support running totals (calories, EXP) across multiple messages per day, keyed by date
- **OAuth2 setup from scratch** — configured Google Cloud Console projects, consent screens, and scoped credentials for both Calendar and Sheets APIs

## Development Note

This project was built with Claude (Anthropic) as a technical collaborator — used for drafting initial workflow logic, debugging n8n/Docker/Caddy configuration issues, and refining AI prompts. All architecture decisions, testing, and integration work were done hands-on throughout the build process.

## Stack

`n8n` · `Docker` · `Docker Compose` · `Caddy` · `DigitalOcean` · `Telegram Bot API` · `Google Calendar API` · `Google Sheets API` · `Anthropic Claude API (Haiku 4.5)` · `JavaScript (n8n Code nodes)`

## Setup

These workflows are exported as JSON and can be imported directly into any n8n instance (Settings → Import from File). You'll need:
1. A Telegram bot token per workflow (via [@BotFather](https://t.me/botfather))
2. Google Cloud OAuth2 credentials with Calendar and Sheets APIs enabled
3. An Anthropic API key ([console.anthropic.com](https://console.anthropic.com))
4. Your own Google Sheet(s) matching the column structure referenced in each workflow

Placeholder values (`YOUR_EMAIL`, `YOUR_TELEGRAM_CHAT_ID`, `YOUR_GOOGLE_SHEET_URL_HERE`) will need to be replaced with your own before running.

