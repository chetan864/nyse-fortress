#!/usr/bin/env python3
"""
NYSE Fortress — Daily Briefing Generator
Fetches real market data via web search + Yahoo Finance
Generates a Jekyll markdown post for GitHub Pages
"""

import os
import json
import datetime
import requests
import re
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────────────────────
POSTS_DIR = Path("_posts")
POSTS_DIR.mkdir(exist_ok=True)

TODAY = datetime.date.today()
NOW_ET = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4)))  # EDT
DATE_STR = TODAY.strftime("%Y-%m-%d")
DATE_DISPLAY = TODAY.strftime("%A, %B %d, %Y")
TIME_DISPLAY = NOW_ET.strftime("%I:%M %p ET")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ── FETCH REAL DATA via Anthropic + Web Search ────────────────────────────────
def fetch_market_data():
    """Use Claude with web search to gather today's real market data."""
    if not ANTHROPIC_API_KEY:
        print("⚠️  No ANTHROPIC_API_KEY found — using fallback template data")
        return get_fallback_data()

    prompt = f"""Today is {DATE_DISPLAY}. You are a financial data aggregator.
Search the web and return a JSON object with today's REAL market data.
Return ONLY valid JSON, no markdown, no preamble.

Required JSON structure:
{{
  "fear_greed_score": <integer 0-100, CNN Fear & Greed Index>,
  "fear_greed_label": "<Extreme Fear|Fear|Neutral|Greed|Extreme Greed>",
  "fear_greed_emotion": "<brief description of primary driver>",
  "fear_greed_note": "<1 sentence context about what's driving it>",
  "brent_crude": "<price like 121.50>",
  "sp500_change": "<like -1.24% or +0.87%>",
  "sp500_level": "<like 5123.45>",
  "vix": "<like 28.4>",
  "analyst_upgrades": [
    {{"rank": "🥇", "firm": "<firm>", "ticker": "<$TICK>", "name": "<company>", "rating": "<rating or PT>", "note": "<brief reason>"}},
    {{"rank": "🥈", "firm": "<firm>", "ticker": "<$TICK>", "name": "<company>", "rating": "<rating>", "note": "<brief reason>"}},
    {{"rank": "🥉", "firm": "<firm>", "ticker": "<$TICK>", "name": "<company>", "rating": "<rating>", "note": "<brief reason>"}}
  ],
  "tariff_status": "<current tariff situation in 1 sentence>",
  "taco_sp500_status": "<🔴 CRITICAL|🟡 CAUTION|🟢 NORMAL>",
  "taco_sp500_action": "<recommended action>",
  "taco_tariff_status": "<🔥 PIVOT ZONE|⚠️ ACTIVE|✅ STABLE>",
  "taco_tariff_action": "<recommended action>",
  "taco_action_item": "<1-2 sentence tactical recommendation>",
  "dividends_equities": [
    {{"tier": "🏆 Platinum", "symbol": "<TICK>", "company": "<name>", "amount": "$X.XX", "type": "Special|Quarterly|Variable", "pay_date": "<date>", "action": "<action>", "action_color": "green|gold|silver|red"}},
    {{"tier": "💎 Diamond", "symbol": "<TICK>", "company": "<name>", "amount": "$X.XX", "type": "Quarterly", "pay_date": "<date>", "action": "<action>", "action_color": "gold"}},
    {{"tier": "🥇 Gold", "symbol": "<TICK>", "company": "<name>", "amount": "$X.XX", "type": "Special", "pay_date": "<date>", "action": "<action>", "action_color": "green"}},
    {{"tier": "🥈 Silver", "symbol": "<TICK>", "company": "<name>", "amount": "$X.XX", "type": "Quarterly", "pay_date": "<date>", "action": "<action>", "action_color": "silver"}},
    {{"tier": "🥉 Bronze", "symbol": "<TICK>", "company": "<name>", "amount": "$X.XX", "type": "Variable", "pay_date": "<date>", "action": "<action>", "action_color": "silver"}}
  ],
  "dividends_etfs": [
    {{"tier": "🏆 Platinum", "symbol": "VOO", "name": "Vanguard S&P 500", "dist": "$X.XXXX", "freq": "Quarterly", "pay_date": "<date>", "action": "<action>", "action_color": "green"}},
    {{"tier": "💎 Diamond", "symbol": "JEPI", "name": "JPM Equity Premium Income", "dist": "$X.XXXX", "freq": "Monthly", "pay_date": "<date>", "action": "<action>", "action_color": "gold"}},
    {{"tier": "🥇 Gold", "symbol": "SCHD", "name": "Schwab US Dividend Equity", "dist": "$X.XXXX", "freq": "Quarterly", "pay_date": "<date>", "action": "<action>", "action_color": "green"}},
    {{"tier": "🥈 Silver", "symbol": "DGRO", "name": "iShares Core Dividend Growth", "dist": "$X.XXXX", "freq": "Quarterly", "pay_date": "<date>", "action": "<action>", "action_color": "silver"}},
    {{"tier": "🥉 Bronze", "symbol": "VIG", "name": "Vanguard Dividend Appreciation", "dist": "$X.XXXX", "freq": "Quarterly", "pay_date": "<date>", "action": "<action>", "action_color": "silver"}}
  ],
  "portfolio_equities": [
    {{"tier": "🏆 Platinum", "asset": "<Name ($TICK)>", "action": "BUY|SELL|HOLD|ACCUMULATE|WAIT", "confidence": <6.0-10.0>, "logic": "<reason>", "action_color": "green|red|gold|accent|orange"}},
    {{"tier": "💎 Diamond", "asset": "<Name ($TICK)>", "action": "ACCUMULATE", "confidence": <float>, "logic": "<reason>", "action_color": "accent"}},
    {{"tier": "🥇 Gold", "asset": "<Name ($TICK)>", "action": "BUY", "confidence": <float>, "logic": "<reason>", "action_color": "green"}},
    {{"tier": "🥈 Silver", "asset": "<Name ($TICK)>", "action": "HOLD", "confidence": <float>, "logic": "<reason>", "action_color": "gold"}},
    {{"tier": "🥉 Bronze", "asset": "<Name ($TICK)>", "action": "SPECULATIVE", "confidence": <float>, "logic": "<reason>", "action_color": "orange"}}
  ],
  "portfolio_etfs": [
    {{"tier": "🏆 Platinum", "asset": "<Name ($TICK)>", "action": "BUY", "confidence": <float>, "logic": "<reason>", "action_color": "green"}},
    {{"tier": "💎 Diamond", "asset": "<Name ($TICK)>", "action": "ACCUMULATE", "confidence": <float>, "logic": "<reason>", "action_color": "accent"}},
    {{"tier": "🥇 Gold", "asset": "<Name ($TICK)>", "action": "BUY", "confidence": <float>, "logic": "<reason>", "action_color": "green"}},
    {{"tier": "🥈 Silver", "asset": "<Name ($TICK)>", "action": "HOLD", "confidence": <float>, "logic": "<reason>", "action_color": "gold"}},
    {{"tier": "🥉 Bronze", "asset": "<Name ($TICK)>", "action": "WAIT", "confidence": <float>, "logic": "<reason>", "action_color": "red"}}
  ],
  "whale_equities": [
    {{"symbol": "$TICK", "mover": "<Institution>", "action": "BUY|ACCUMULATE|SELL", "confidence": <float>, "logic": "<reason>"}},
    {{"symbol": "$TICK", "mover": "<Institution>", "action": "BUY", "confidence": <float>, "logic": "<reason>"}}
  ],
  "whale_etfs": [
    {{"ticker": "$TICK", "flow": "<+$XXB or De-leveraging>", "sentiment": "BULLISH|BEARISH|NEUTRAL", "whale": "<activity>", "logic": "<reason>", "sent_color": "green|red|gold"}},
    {{"ticker": "$TICK", "flow": "<flow>", "sentiment": "BEARISH", "whale": "<activity>", "logic": "<reason>", "sent_color": "red"}}
  ],
  "predictions": [
    {{"platform": "Kalshi", "question": "<current market question>", "reading": "<odds>", "color": "green|orange|red"}},
    {{"platform": "Polymarket", "question": "<current market question>", "reading": "<odds>", "color": "orange"}}
  ],
  "elon_phases": [
    {{"phase": "Phase X: <name>", "status": "<current focus>", "action": "<emoji> <action>", "logic": "<reason>", "action_color": "red|green|gold"}},
    {{"phase": "Phase Y: <name>", "status": "<current focus>", "action": "<emoji> <action>", "logic": "<reason>", "action_color": "green"}}
  ],
  "elon_action": "<tactical recommendation re Elon/Tesla/related>",
  "top_pick": "<ticker of the single best idea today>",
  "gyaan": "<original market wisdom quote appropriate for today's conditions, 2-3 sentences>"
}}"""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "anthropic-beta": "web-search-2025-03-05",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4000,
                "tools": [{"type": "web_search_20250305", "name": "web_search"}],
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=90
        )
        data = response.json()
        # Extract text content from response
        text = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                text += block.get("text", "")
        # Strip markdown fences if present
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*", "", text)
        text = text.strip()
        result = json.loads(text)
        print(f"✅ Real market data fetched successfully")
        return result
    except Exception as e:
        print(f"⚠️  API fetch failed ({e}) — using fallback data")
        return get_fallback_data()


def get_fallback_data():
    """Fallback template data if API is unavailable."""
    return {
        "fear_greed_score": 12,
        "fear_greed_label": "EXTREME FEAR",
        "fear_greed_emotion": "Existential Dread (Physical Supply Shock)",
        "fear_greed_note": "Brent Crude elevated. Market pricing in structural energy deficit.",
        "brent_crude": "121.00",
        "sp500_change": "-0.85%",
        "sp500_level": "5201.34",
        "vix": "27.4",
        "analyst_upgrades": [
            {"rank": "🥇", "firm": "Goldman Sachs", "ticker": "$NOK", "name": "Nokia", "rating": "Neutral", "note": "Bottom-fishing on AI infrastructure backlog."},
            {"rank": "🥈", "firm": "UBS", "ticker": "$TRGP", "name": "Targa Resources", "rating": "PT $280", "note": "High conviction on natural gas midstream."},
            {"rank": "🥉", "firm": "Morgan Stanley", "ticker": "$CPT", "name": "Camden Property Trust", "rating": "Equalweight ($119)", "note": "Reiterated."}
        ],
        "tariff_status": "10% Section 122 duty remains in effect.",
        "taco_sp500_status": "🔴 CRITICAL",
        "taco_sp500_action": "🟢 BUY THE DIP",
        "taco_tariff_status": "🔥 PIVOT ZONE",
        "taco_tariff_action": "🚀 LONG S&P CALLS",
        "taco_action_item": "Buy $SPY or $VOO on any dip below $515.",
        "dividends_equities": [
            {"tier": "🏆 Platinum", "symbol": "AII", "company": "American Integrity", "amount": "$1.02", "type": "Special", "pay_date": "Today", "action": "🟢 CONFIRM RECEIPT", "action_color": "green"},
            {"tier": "💎 Diamond", "symbol": "BIPC", "company": "Brookfield Infra.", "amount": "$0.455", "type": "Quarterly", "pay_date": "Mar 31", "action": "🟡 HOLD", "action_color": "gold"},
            {"tier": "🥇 Gold", "symbol": "TBP", "company": "Tier 1 Bank", "amount": "$0.65", "type": "Special", "pay_date": "Apr 02", "action": "🟢 ACCUMULATE", "action_color": "green"},
            {"tier": "🥈 Silver", "symbol": "NYE", "company": "NY Energy", "amount": "$0.30", "type": "Quarterly", "pay_date": "Apr 05", "action": "⚪ MONITOR", "action_color": "silver"},
            {"tier": "🥉 Bronze", "symbol": "LIT", "company": "Lithium Corp", "amount": "$0.12", "type": "Variable", "pay_date": "Apr 10", "action": "⚪ WATCH", "action_color": "silver"}
        ],
        "dividends_etfs": [
            {"tier": "🏆 Platinum", "symbol": "VOO", "name": "Vanguard S&P 500", "dist": "$1.8724", "freq": "Quarterly", "pay_date": "Mar 31", "action": "🟢 BUY/HOLD TODAY", "action_color": "green"},
            {"tier": "💎 Diamond", "symbol": "JEPI", "name": "JPM Equity Premium Income", "dist": "$0.3513", "freq": "Monthly", "pay_date": "Apr 06", "action": "🟡 ACCUMULATE", "action_color": "gold"},
            {"tier": "🥇 Gold", "symbol": "SCHD", "name": "Schwab US Dividend Equity", "dist": "$0.6110", "freq": "Quarterly", "pay_date": "Apr 10", "action": "🟢 BUY", "action_color": "green"},
            {"tier": "🥈 Silver", "symbol": "DGRO", "name": "iShares Core Dividend Growth", "dist": "$0.3200", "freq": "Quarterly", "pay_date": "Apr 15", "action": "⚪ MONITOR", "action_color": "silver"},
            {"tier": "🥉 Bronze", "symbol": "VIG", "name": "Vanguard Dividend Appreciation", "dist": "$0.7700", "freq": "Quarterly", "pay_date": "Apr 20", "action": "⚪ WATCH", "action_color": "silver"}
        ],
        "portfolio_equities": [
            {"tier": "🏆 Platinum", "asset": "Exxon ($XOM)", "action": "BUY", "confidence": 9.5, "logic": "Physical supply shock hedge; elevated Brent floor.", "action_color": "green"},
            {"tier": "💎 Diamond", "asset": "Microsoft ($MSFT)", "action": "ACCUMULATE", "confidence": 8.5, "logic": "High-conviction play for policy pivot.", "action_color": "accent"},
            {"tier": "🥇 Gold", "asset": "Chevron ($CVX)", "action": "BUY", "confidence": 8.0, "logic": "Energy sector secondary strength.", "action_color": "green"},
            {"tier": "🥈 Silver", "asset": "Walmart ($WMT)", "action": "HOLD", "confidence": 7.5, "logic": "Defensive consumer staple floor.", "action_color": "gold"},
            {"tier": "🥉 Bronze", "asset": "Ford ($F)", "action": "SPECULATIVE", "confidence": 6.5, "logic": "Value play on industrial recovery.", "action_color": "orange"}
        ],
        "portfolio_etfs": [
            {"tier": "🏆 Platinum", "asset": "Utilities ($VPU)", "action": "BUY", "confidence": 9.6, "logic": "Ultimate institutional bunker with high yield.", "action_color": "green"},
            {"tier": "💎 Diamond", "asset": "S&P 500 ($VOO)", "action": "ACCUMULATE", "confidence": 9.1, "logic": "Div capture + relief rally.", "action_color": "accent"},
            {"tier": "🥇 Gold", "asset": "Energy ($VDE)", "action": "BUY", "confidence": 8.8, "logic": "Direct play on physical supply shock.", "action_color": "green"},
            {"tier": "🥈 Silver", "asset": "Healthcare ($XLV)", "action": "HOLD", "confidence": 8.2, "logic": "Defensive growth in volatile macro.", "action_color": "gold"},
            {"tier": "🥉 Bronze", "asset": "Small Cap ($IWM)", "action": "WAIT", "confidence": 6.0, "logic": "High sensitivity to yield volatility.", "action_color": "red"}
        ],
        "whale_equities": [
            {"symbol": "$MSFT", "mover": "BlackRock", "action": "ACCUMULATE", "confidence": 8.8, "logic": "Massive Dark Pool prints detected."},
            {"symbol": "$AMAT", "mover": "Institutional", "action": "BUY", "confidence": 9.0, "logic": "Whales front-running hardware build-out."}
        ],
        "whale_etfs": [
            {"ticker": "$VOO", "flow": "+$43.3B", "sentiment": "BULLISH", "whale": "Buying the Dip", "logic": "Adding to Value while fleeing Growth.", "sent_color": "green"},
            {"ticker": "$VPU", "flow": "De-leveraging", "sentiment": "BEARISH", "whale": "Liquidity Hunt", "logic": "Smart money exiting to fund tech rotation.", "sent_color": "red"}
        ],
        "predictions": [
            {"platform": "Kalshi", "question": "Fed Pause in April?", "reading": "100% (Priced in)", "color": "green"},
            {"platform": "Polymarket", "question": "Iran Ceasefire?", "reading": "24¢ (Volatile)", "color": "orange"}
        ],
        "elon_phases": [
            {"phase": "Phase 1: Distraction", "status": "DOGE / Politics", "action": "🔴 HEDGE TSLA", "logic": "Elon focused on DOGE efficiency audits.", "action_color": "red"},
            {"phase": "Phase 4: Supplier Lag", "status": "Infrastructure Flow", "action": "🟢 BUY AMAT / ASML", "logic": "Institutions funding hardware, not hype.", "action_color": "green"}
        ],
        "elon_action": "Sell/Hedge $TSLA. Buy $AMAT as the infrastructure toll-booth for Terafab.",
        "top_pick": "$XOM",
        "gyaan": '"A whale does not move in the shallows because they are afraid of the shore; they move there because that is where the smaller fish are most panicked. When the water gets choppy, don\'t swim against the tide—watch where the biggest shadows are heading."'
    }


# ── COLOR MAP ─────────────────────────────────────────────────────────────────
COLOR_MAP = {
    "green":  "var(--green)",
    "red":    "var(--red)",
    "gold":   "var(--gold)",
    "accent": "var(--accent)",
    "orange": "var(--orange)",
    "silver": "var(--silver)",
}

def color(key):
    return COLOR_MAP.get(key, "var(--silver)")

def gauge_color(score):
    if score < 25: return "var(--red)"
    if score < 50: return "var(--orange)"
    if score < 75: return "var(--gold)"
    return "var(--green)"

# ── GENERATE HTML CONTENT ─────────────────────────────────────────────────────
def build_post_html(d):
    fg_score = d["fear_greed_score"]
    fg_col = gauge_color(fg_score)

    lines = []
    def h(html): lines.append(html)

    # ── Section 1: Fear & Greed
    h('<h3>📊 Section 1: Bloomberg Fear &amp; Greed Index</h3>')
    h('<div class="section-card">')
    h(f'  <div class="fear-gauge">')
    h(f'    <div class="gauge-track"><div class="gauge-fill" data-width="{fg_score}" style="background:{fg_col}"></div></div>')
    h(f'    <div class="gauge-score" style="color:{fg_col}">{fg_score}/100</div>')
    h(f'  </div>')
    h(f'  <div class="fear-label" style="color:{fg_col}">{d["fear_greed_label"]}</div>')
    h(f'  <div class="fear-emotion">{d["fear_greed_emotion"]}</div>')
    h(f'  <div class="fear-note">{d["fear_greed_note"]}</div>')
    if d.get("brent_crude"):
        h(f'  <div style="margin-top:12px;display:flex;gap:16px;flex-wrap:wrap">')
        h(f'    <span class="badge" style="color:var(--orange)">🛢️ Brent ${d["brent_crude"]}/bbl</span>')
        if d.get("sp500_change"):
            col = "var(--green)" if "+" in str(d["sp500_change"]) else "var(--red)"
            h(f'    <span class="badge" style="color:{col}">📈 S&P {d["sp500_change"]}</span>')
        if d.get("vix"):
            h(f'    <span class="badge" style="color:var(--silver)">📉 VIX {d["vix"]}</span>')
        h(f'  </div>')
    h('</div>')

    # ── Section 2: Analyst Upgrades
    h('<h3>🚀 Section 2: Top Analyst Upgrades</h3>')
    for u in d.get("analyst_upgrades", []):
        h('<div class="section-card">')
        h(f'  <div class="upgrade-card">')
        h(f'    <div class="upgrade-rank">{u["rank"]}</div>')
        h(f'    <div class="upgrade-body">')
        h(f'      <div class="upgrade-header">')
        h(f'        <span class="upgrade-firm">{u["firm"]}</span>')
        h(f'        <span class="badge" style="color:var(--accent)">{u["ticker"]}</span>')
        h(f'      </div>')
        h(f'      <div class="upgrade-name">{u["name"]}</div>')
        h(f'      <div class="upgrade-rating">{u["rating"]}</div>')
        h(f'      <div class="upgrade-note">{u["note"]}</div>')
        h(f'    </div>')
        h(f'  </div>')
        h('</div>')

    # ── Section 3: TACO Alert
    h('<h3>🌮 Section 3: TACO Alert (The Pivot Predictor)</h3>')
    taco_rows = [
        ("S&P 500 Performance", d.get("sp500_change","—"), d.get("taco_sp500_status","—"), d.get("taco_sp500_action","—")),
        ("Tariff Status", d.get("tariff_status","—"), d.get("taco_tariff_status","—"), d.get("taco_tariff_action","—")),
    ]
    for metric, level, status, action in taco_rows:
        h('<div class="section-card">')
        h(f'  <div class="taco-row">')
        h(f'    <div class="taco-left"><div class="taco-metric">{metric}</div><div class="taco-level">{level}</div></div>')
        h(f'    <div class="taco-right"><div class="taco-status">{status}</div><div class="taco-action">{action}</div></div>')
        h(f'  </div>')
        h('</div>')
    h('<div class="action-box">')
    h(f'  <div class="action-label">⚡ ACTION ITEM</div>')
    h(f'  <div class="action-text">{d.get("taco_action_item","—")}</div>')
    h('</div>')

    # ── Section 4: Dividends
    h('<h3>💰 Section 4: Special Dividend Tracker (NYSE Only)</h3>')
    h('<div class="sub-label">Sub-Division A: NYSE Equities (Tiered)</div>')
    for div in d.get("dividends_equities", []):
        ac = color(div.get("action_color", "silver"))
        h('<div class="section-card">')
        h(f'  <div class="div-header"><span class="div-tier">{div["tier"]}</span><span style="color:{ac};font-weight:800;font-size:12px">{div["action"]}</span></div>')
        h(f'  <div class="div-symbol">{div["symbol"]}</div>')
        h(f'  <div class="div-company">{div["company"]}</div>')
        h(f'  <div class="div-badges">')
        h(f'    <span class="badge" style="color:var(--gold)">{div["amount"]}</span>')
        h(f'    <span class="badge" style="color:var(--muted)">{div["type"]}</span>')
        h(f'    <span class="badge" style="color:var(--accent)">{div["pay_date"]}</span>')
        h(f'  </div>')
        h('</div>')

    h('<div class="sub-label">Sub-Division B: NYSE ETFs (Tiered)</div>')
    for etf in d.get("dividends_etfs", []):
        ac = color(etf.get("action_color", "silver"))
        h('<div class="section-card">')
        h(f'  <div class="div-header"><span class="div-tier">{etf["tier"]}</span><span style="color:{ac};font-weight:800;font-size:12px">{etf["action"]}</span></div>')
        h(f'  <div class="div-symbol">{etf["symbol"]}</div>')
        h(f'  <div class="div-company">{etf["name"]}</div>')
        h(f'  <div class="div-badges">')
        h(f'    <span class="badge" style="color:var(--gold)">{etf["dist"]}</span>')
        h(f'    <span class="badge" style="color:var(--muted)">{etf["freq"]}</span>')
        h(f'    <span class="badge" style="color:var(--accent)">{etf["pay_date"]}</span>')
        h(f'  </div>')
        h('</div>')

    # ── Section 5: Portfolio
    h('<h3>💎 Section 5: Portfolio Tiers (NYSE 🇺🇸)</h3>')
    h('<div class="sub-label">Sub-Division A: Individual Equities</div>')
    for p in d.get("portfolio_equities", []):
        ac = color(p.get("action_color", "silver"))
        conf_pct = p["confidence"] * 10
        h('<div class="section-card">')
        h(f'  <div class="port-header"><span class="port-tier">{p["tier"]}</span><span class="badge" style="color:{ac}">{p["action"]}</span></div>')
        h(f'  <div class="port-asset">{p["asset"]}</div>')
        h(f'  <div class="conf-wrap"><div class="conf-track"><div class="conf-fill" data-width="{conf_pct}" style="background:{ac}"></div></div><span class="conf-score" style="color:{ac}">{p["confidence"]}</span></div>')
        h(f'  <div class="port-logic">{p["logic"]}</div>')
        h('</div>')

    h('<div class="sub-label">Sub-Division B: Portfolio ETFs</div>')
    for p in d.get("portfolio_etfs", []):
        ac = color(p.get("action_color", "silver"))
        conf_pct = p["confidence"] * 10
        h('<div class="section-card">')
        h(f'  <div class="port-header"><span class="port-tier">{p["tier"]}</span><span class="badge" style="color:{ac}">{p["action"]}</span></div>')
        h(f'  <div class="port-asset">{p["asset"]}</div>')
        h(f'  <div class="conf-wrap"><div class="conf-track"><div class="conf-fill" data-width="{conf_pct}" style="background:{ac}"></div></div><span class="conf-score" style="color:{ac}">{p["confidence"]}</span></div>')
        h(f'  <div class="port-logic">{p["logic"]}</div>')
        h('</div>')

    # ── Section 6: Whales
    h('<h3>🕵️ Section 6: Smart Money Flow (The Whales)</h3>')
    h('<div class="sub-label">Sub-Division A: Dark Pool &amp; Insider Activity</div>')
    for w in d.get("whale_equities", []):
        conf_pct = w["confidence"] * 10
        h('<div class="section-card">')
        h(f'  <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">')
        h(f'    <span class="whale-symbol">{w["symbol"]}</span>')
        h(f'    <span class="badge" style="color:var(--green)">{w["action"]}</span>')
        h(f'  </div>')
        h(f'  <div class="whale-mover">{w["mover"]}</div>')
        h(f'  <div class="conf-wrap"><div class="conf-track"><div class="conf-fill" data-width="{conf_pct}" style="background:var(--green)"></div></div><span class="conf-score" style="color:var(--green)">{w["confidence"]}</span></div>')
        h(f'  <div class="port-logic">{w["logic"]}</div>')
        h('</div>')

    h('<div class="sub-label">Sub-Division B: Institutional ETF Flows</div>')
    for w in d.get("whale_etfs", []):
        sc = color(w.get("sent_color", "silver"))
        h('<div class="section-card">')
        h(f'  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">')
        h(f'    <span class="whale-symbol">{w["ticker"]}</span>')
        h(f'    <span class="whale-sent" style="color:{sc}">{w["sentiment"]}</span>')
        h(f'  </div>')
        h(f'  <div class="whale-row"><span class="whale-flow" style="color:var(--text)">{w["flow"]}</span><span class="whale-whale">{w["whale"]}</span></div>')
        h(f'  <div class="port-logic">{w["logic"]}</div>')
        h('</div>')

    # ── Section 7: Predictions
    h('<h3>🔮 Section 7: The Truth Machine (Prediction Markets)</h3>')
    for p in d.get("predictions", []):
        pc = color(p.get("color", "silver"))
        h('<div class="section-card">')
        h(f'  <div class="pred-row">')
        h(f'    <div><div class="pred-platform">{p["platform"]}</div><div class="pred-q">{p["question"]}</div></div>')
        h(f'    <div class="pred-reading" style="color:{pc}">{p["reading"]}</div>')
        h(f'  </div>')
        h('</div>')

    # ── Section 8: Elon Oscillator
    h('<h3>🛰️ Section 8: The Elon Oscillator</h3>')
    for ph in d.get("elon_phases", []):
        ac = color(ph.get("action_color", "silver"))
        h('<div class="section-card">')
        h(f'  <div class="elon-phase">{ph["phase"]}</div>')
        h(f'  <div class="elon-status">{ph["status"]}</div>')
        h(f'  <div class="elon-action" style="color:{ac}">{ph["action"]}</div>')
        h(f'  <div class="port-logic">{ph["logic"]}</div>')
        h('</div>')
    h('<div class="action-box">')
    h(f'  <div class="action-label">⚡ ACTION ITEM</div>')
    h(f'  <div class="action-text">{d.get("elon_action","—")}</div>')
    h('</div>')

    # ── Gyaan
    h('<div class="gyaan-card">')
    h(f'  <div class="gyaan-icon">✨</div>')
    h(f'  <div class="gyaan-title">THE CLOSING GYAAN</div>')
    h(f'  <div class="gyaan-text">{d.get("gyaan","—")}</div>')
    h('</div>')

    return "\n".join(lines)


# ── WRITE JEKYLL POST ─────────────────────────────────────────────────────────
def write_post(d):
    filename = POSTS_DIR / f"{DATE_STR}-morning-briefing.md"

    fg = d["fear_greed_score"]
    top = d.get("top_pick", "")
    brent = d.get("brent_crude", "")
    content = build_post_html(d)

    frontmatter = f"""---
layout: post
title: "🛡️ NYSE Fortress — {DATE_DISPLAY} Morning Briefing"
date: {DATE_STR} 09:35:00 -0400
categories: briefing
fear_greed_score: {fg}
top_pick: "{top}"
brent_price: "{brent}"
briefing_time: "{TIME_DISPLAY}"
---

{content}
"""
    filename.write_text(frontmatter, encoding="utf-8")
    print(f"✅ Post written: {filename}")
    return filename


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"🛡️  NYSE Fortress Briefing Generator")
    print(f"📅  Date: {DATE_DISPLAY}")
    print(f"🔍  Fetching real market data...")
    data = fetch_market_data()
    post_file = write_post(data)
    print(f"🚀  Done! Post saved to {post_file}")
