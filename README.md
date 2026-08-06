# Project Alpha — Primary-Source Podcast Pipeline

A personal pipeline that pulls primary-source economic/investment text (central bank
statements, SEC filings) and turns it into a daily podcast, so the listener hears the
raw signal instead of a commentator's interpretation of it.

## Why "primary source" and not just "another finance podcast"

Popular finance podcasts are secondary sources: someone already read the Fed statement
or the 8-K and is telling you what they think it means. That's a second layer of
interpretation on top of the original text, and it's the same layer everyone else is
hearing too — there's no edge in it. This project reads the original text itself, so
the interpretation is left to the listener.

Note that "primary source" doesn't mean "unbiased" — a Fed statement is a deliberately
crafted communication, and an 8-K's management commentary is curated PR. What this
project avoids isn't bias in the source, it's an *additional* layer of bias from a
commentator on top of the source.

## How it works

```
sources → extract → text-to-speech → assemble → RSS feed
```

1. **Sources** (`pipeline/sources/`) fetch new items from each origin: Fed and Bank of
   Canada press releases (via their official RSS feeds), and SEC 8-K filings for a
   watchlist of tickers (via SEC EDGAR's public API).
2. **Extract** (`pipeline/extract.py`) turns each item's raw HTML into clean, readable
   text — stripping navigation, legal boilerplate, and other non-content — without
   summarizing or rewriting anything. The goal is subtraction only, never addition.
3. **Text-to-speech** (`pipeline/tts.py`) synthesizes the cleaned text into audio using
   OpenAI's TTS API.
4. **Assemble** (`pipeline/assemble.py`) stitches the day's clips into one MP3.
5. **Feed** (`pipeline/feed.py`) publishes that episode into a podcast RSS feed, hosted
   on GitHub Pages, so it can be subscribed to from a normal podcast app.

A GitHub Actions workflow (`.github/workflows/daily.yml`) runs this once a day so a new
episode is ready by morning.

## Project status

This is being built incrementally, one phase at a time, each one manually verified
before moving to the next. See the plan for the current phase breakdown. As of now:
Fed and Bank of Canada ingestion is in progress; SEC filings, TTS, assembly, feed
generation, and automation are not yet built.

## Explicitly out of scope (for now)

Earnings call transcripts, ECB statements, economic data releases (CPI/jobs),
summarization of long documents, and pruning of old episodes from the repo.
These are deferred, not forgotten — the pipeline is built to add sources
incrementally.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
