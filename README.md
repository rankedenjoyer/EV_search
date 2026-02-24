# Bet Intelligence Platform

## Project Overview

This project is a real-time betting intelligence platform that aggregates odds from multiple bookmakers, analyzes betting opportunities using quantitative strategies, and provides daily actionable betting insights.

The system performs:

- Live sportsbook scraping
- Odds normalization
- Value betting detection (+EV)
- Arbitrage opportunity detection
- Kelly Criterion bankroll optimization
- Historical tracking and analytics dashboard

This repository is designed for automated development using Codex.  
README.md is the authoritative architectural specification.

---

## Architecture Overview

Scraper Workers (Playwright Python)
        ↓
PostgreSQL Database
        ↓
FastAPI Backend (Strategy Engine)
        ↓
React Frontend Dashboard
        ↓
Nginx Reverse Proxy

---

## Supported Bookmakers (Phase 1)

- Picklebet
- Dabble
- EliteBet
- Bet365
- Neds
- Ladbrokes
- Unibet

---

## Core Strategies

### 1. Value Betting (+EV)

Expected Value:

EV = (true_probability * odds) - 1

Condition:
EV > 0

---

### 2. Arbitrage Detection

Arbitrage exists when:

sum(1 / best_odds_outcome) < 1

---

### 3. Kelly Criterion

Formula:

f = (bp − q) / b

Where:
b = odds - 1  
p = win probability  
q = 1 - p  

Stake = bankroll * f * risk_factor

---

## Database Concepts

events
odds
odds_history
value_bets
arbitrage_opportunities
users
bet_history

---

## Development Rules

- Scrapers NEVER perform calculations.
- Scrapers ONLY collect and store data.
- Backend performs all analysis.
- Frontend NEVER computes strategies.
- Only today's events are processed.
- Historical odds are stored permanently.

---

## Quick Start

Copy environment variables:

cp .env.example .env

Run system:

docker compose up --build

Backend API:
http://localhost:8000

Frontend:
http://localhost:5173

---

## Development Commands

Start services:
docker compose up

Rebuild:
docker compose up --build

Stop:
docker compose down

---

## Adding a New Bookmaker

1. Create scraper in:
   scraper/app/bookmakers/

2. Normalize team names.

3. Send standardized data to backend API.

---

## Codex Operating Instructions

Codex MUST:

- Read README.md before every task.
- Follow architecture strictly.
- Update README.md if architecture changes.
- Ensure docker compose builds successfully after changes.

README.md is persistent project memory.

---

## Future Expansion

- Telegram alerts
- Discord notifications
- ML probability models
- Reinforcement learning bettor
- Live betting support
