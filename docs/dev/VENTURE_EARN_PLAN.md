# AI-assisted income — ways, plan, strategy

**Not autonomous money.** A **repeatable system** you chair; Jarvis + agents execute git-safe and low-risk steps. Covenant: [PARTNERSHIP.md](../PARTNERSHIP.md) · loop design: [BUSINESS_OPERATOR.md](../BUSINESS_OPERATOR.md).

---

## 1. Objective function

Maximize **legitimate net profit per hour of your attention**, subject to:

- Minimum quality and refund risk you accept  
- Legal/compliance (no spam, no stolen IP, no fake reviews)  
- **Human confirm** on: payments, ads, contracts, bulk email, account creation  

Store in Soul: `venture_constraints`, `work_priority_week`.

---

## 2. Ways AI can help you earn (15 paths)

Rate: **Automation** = how much AI can run without you · **Capital** = cash to start · **Jarvis fit** = how well the repo supports it today.

| # | Way | What you sell | Automation | Capital | Jarvis fit now |
|---|-----|---------------|------------|---------|----------------|
| **1** | **Time arbitrage** | Your job/freelance; AI speeds delivery | Medium | Low | ✅ devloop, drafts, admin plugins |
| **2** | **Micro-SaaS** | Small B2B tool ($19–99/mo) | Medium | Low–Med | Build via agents; Playwright later |
| **3** | **Digital templates** | Notion, Excel, Figma, code kits | High (create) | Low | Builder agents + store you run |
| **4** | **API wrapper** | Niche API on top of public data | Medium | Low | Python plugins pattern |
| **5** | **Browser extension** | One painful workflow fixed | Medium | Low | Web + Phase 3 tools |
| **6** | **Paid newsletter / guide** | Expertise + AI polish | High (draft) | Low | Growth drafts; you publish |
| **7** | **Automation retainers** | n8n/Zapier-style flows for SMBs | Medium | Low | n8n ADR; Hands boring-money |
| **8** | **Dev services productized** | Fixed-scope “setup Jarvis / HA / brain” | Low | Low | You + this repo as proof |
| **9** | **Affiliate / honest reviews** | Tools you use | Medium | Low | Scout research; **disclose** |
| **10** | **Marketplace plugins** | Jarvis Phase 6 SDK extensions | Medium | Low | After SDK exit |
| **11** | **Content + ads** | YouTube/site + AdSense | Low–Med | Low | AI scripts; you film/host |
| **12** | **Data reports** | Industry PDFs from public data | High | Low | Analyst + R/Python subprocess |
| **13** | **Waitlist → pre-sell** | Validate before build | High | Low | Venture experiment template |
| **14** | **Portfolio of SKUs** | Many small products | Medium | Med | CEO loop + kill rules |
| **15** | **License your robots** | Plugins others install | Medium | Low | Phase 6 + your IP |

**Poor fits (avoid as “AI keeps earning”):** crypto bots, ad fraud, mass cold outreach, trademark squatting, fully unattended ad spend.

---

## 3. Strategy: three portfolios

Run **three buckets** so one channel doesn’t starve the others:

| Bucket | Purpose | Target share of effort |
|--------|---------|------------------------|
| **A — Cash now** | Freelance/job leverage (#1) | 50% until runway safe |
| **B — Assets** | Micro-SaaS, templates, APIs (#2–5, #10) | 35% |
| **C — Bets** | Waitlists, new niches (#13–14) | 15% |

AI **CEO draft** allocates *your* weekly hours across A/B/C — you approve.

---

## 4. The repeating money loop (every SKU)

```text
SCOUT → ANALYST (proceed?) → EXPERIMENT (budget, timebox)
  → BUILD → LAUNCH → MEASURE (revenue, CAC, conversion)
  → KILL | SCALE | ITERATE → back to SCOUT
```

**Kill rules (example):** ₹10k or 7 days; if signups &lt; 20 and conversion &lt; 1% → `killed` unless you override.

Task packet template: [BUSINESS_OPERATOR.md](../BUSINESS_OPERATOR.md) § Layer 7.

---

## 5. Phased plan (90 days → 12 months)

### Days 1–30 — Foundation

| Week | You | AI / Jarvis |
|------|-----|-------------|
| 1 | Set `venture_constraints` + pick **one niche** (boring B2B preferred) | Soul memory; no product code |
| 2 | Pick **way #2 or #13** (micro-SaaS or waitlist) | Scout brief from reviews you paste |
| 3 | Launch landing + analytics | Builder: page in repo or Carrd; measure |
| 4 | CEO review: kill or build MVP | One `devloop` or `VENTURE-001` issue |

**Exit:** One experiment with **numbers**, not vibes.

### Days 31–90 — One winner + cash bucket

| Goal | Action |
|------|--------|
| Double down | Scale marketing **only** if CAC &lt; ⅓ first-month revenue |
| Asset #2 | Start template or API only if experiment #1 &gt; break-even or killed cleanly |
| Jarvis product | Keep Phase 2–3 on **separate board** — don’t mix with SKU repos unless intentional |

### Months 4–12 — Portfolio mode

| Milestone | Target |
|-----------|--------|
| Live SKUs | 3–7 small products |
| MRR mix | e.g. ₹30k–2L/mo total (your numbers) |
| Kill rate | ≥50% of experiments killed fast |
| Jarvis | Phase 3 plugins for **your** ops (#7 boring money) |
| Venture OS | LangGraph CEO (**136+**) only if A bucket stable |

---

## 6. Number of “engines” (how many ways at once)

| Profile | Concurrent experiments | Concurrent income ways |
|---------|------------------------|-------------------------|
| **Solo, nights/weekends** | **1** active build + **1** waitlist | **2** max (#1 job + #1 asset) |
| **Solo, full-time** | **2** builds + **2** waitlists | **3** (#1 + #2 + #13) |
| **With agents** | +1 builder lane via `devloop` | Same caps — **you** still CEO |

More than **3** active ways without metrics → usually dilution, not compounding.

---

## 7. What to wire in Jarvis (technical plan)

| Priority | Capability | Issue / doc lane |
|----------|------------|------------------|
| 1 | Metrics memory (`venture_metrics_snapshot`) | Soul / Phase 3 |
| 2 | `opportunity_brief.json` + Analyst score | Venture plugin |
| 3 | `docs/venture/experiments/*.md` task packets | Same as devloop |
| 4 | Playwright smoke + landing checks | **115+**, OSS arsenal |
| 5 | Stripe/read-only revenue ingest | New issue, confirm keys |
| 6 | LangGraph CEO subgraph | **136**, `AI-COMPANY/` only |

**Do not** wire Stripe payouts or ad APIs without `confirm_always`.

---

## 8. Weekly CEO checklist (15 min)

1. Revenue and cost last 7 days (even a spreadsheet).  
2. Which SKU had best **profit / hour**?  
3. Kill one loser or pause one bet.  
4. One Scout input (Reddit/App Store paste — legal sources only).  
5. One task packet for Builder (`devloop say` or venture issue).  
6. Update `work_priority_week` in Soul.

---

## 9. Success metrics (not vanity)

| Metric | Use |
|--------|-----|
| Net profit / week | CEO allocation |
| Conversion % | Kill/scale |
| CAC | Stop bad channels |
| Your hours / SKU | Quit low leverage |
| Support tickets / sale | Quality constraint |

---

## 10. One sentence

**You achieve ongoing income by running a portfolio of small, measured bets with fast kills — AI scouts, builds, and drafts; you own deploy, spend, and law — Jarvis is the loop OS, not the bank account.**

---

## Related

[STARK_TIMELINE.md](STARK_TIMELINE.md) · [OSS_ARSENAL.md](OSS_ARSENAL.md) · [AI-COMPANY/STACK.md](../../AI-COMPANY/STACK.md)
