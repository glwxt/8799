# Context-direction review procedure (GLT V1.0, engineering v0.2.0)

Status: procedure document, 2026-11-21. It does **not** change the engine:
`glt.py` still returns `requires_context_review` for the 9 context
indicators and never auto-scores them. This procedure defines how a human
(Muse) review reaches a documented judgement for the daily briefing, and
how that judgement is recorded. Nothing in this document is written into
`observations.csv` as a score, and no numeric score is invented for a
context indicator.

## Why these 9 cannot be auto-scored

| indicator | why context-only |
|---|---|
| reserves | A falling reserve balance can mean QT drainage (tightening) or a TGA drawdown funding spending (neutral/ easing); the sign depends on what the other side of the balance sheet is doing. |
| tga | A rising TGA drains reserves (tightening), but the cause matters: tax receipts vs new debt issuance vs a debt-ceiling rebuild have different persistence. |
| on_rrp | Falling ON RRP can mean money moving into T-bills (bill supply absorbs liquidity, tightening) or back to bank reserves (easing); the destination decides. RRPONTSYD measures facility awards (mostly domestic, near zero in 2026); it is not the H.4.1 total, which is dominated by the foreign official repo pool. |
| fed_assets | QT pace is policy-set; a small weekly change is noise, a change in the announced runoff pace is the signal. |
| global_usd | No single series exists; it is a composite judgement over dollar funding conditions (cross-currency basis, offshore dollar rates). |
| us_10y_nominal | A rising nominal yield from real growth is benign; the same rise from inflation expectations or term premium is tightening. The split needs the real yield and breakevens. |
| usd_funding | Cross-currency basis and FRA-OIS spreads have no single canonical daily series in this build; direction needs at least two funding gauges agreeing. |
| safe_haven | Composite of gold, CHF, JPY and UST demand; no single series, and a gold rise can be central-bank buying rather than risk-off. |
| asia_equity_flow | Regional foreign flows (TW/HK/CN/JP/KR) cannot be summed into one number: different currencies, different reporting lags, different drivers. |

## Review steps (every daily briefing)

1. **Collect the evidence** for each context indicator: latest value, prior
   value, the counterpart series named above (e.g. TGA vs reserves,
   ON RRP vs T-bill issuance, nominal vs real yield), and the source URL.
   If a counterpart is unavailable, the indicator is recorded as
   `unreviewed` for that day, never guessed.
2. **Judge the direction** in words (tightening / neutral / easing /
   unreviewed) with one sentence of evidence. A direction is only recorded
   when the counterpart evidence points the same way; conflicting
   counterparts mean `unreviewed`.
3. **Record it** in that day's briefing verify file under a
   `context-review` section (indicator, value, counterpart, direction,
   evidence, source). The daily briefing may quote the direction in words;
   it must not present a context judgement as an engine score.
4. **Never** convert a reviewed direction into a 0-100 score for the
   engine, and never write it into `observations.csv`. If Vivi later
   approves scored context inputs, that needs a method change (V1.1) and
   an engine change, not a silent edit here.

## Worked examples (from the verified 2026-11-19/20 briefings)

- reserves: 2026-11-18 weekly average 2,979,656 (H.4.1), down from the
  prior week, while TGA stayed high at 916,613 and QT continued ->
  tightening.
- on_rrp: RRPONTSYD 2026-11-18 0.331 (billion USD); H.4.1 domestic
  Others 298 million -> facility usage at the floor, no further drainage
  from this channel -> neutral.
- us_10y_nominal: DGS10 2026-11-18 5.07% while DFII10 real yield was
  2.88% (near the top of its 1-year range) -> rise driven by real rates
  and term premium, not growth alone -> tightening.
- safe_haven: gold holding near highs with VIX 28.44 on 2026-11-19 and
  equities falling -> risk-off demand -> tightening for transmission.

## What is still missing

- global_usd, usd_funding, asia_equity_flow: no citable daily feed on
  file yet; they stay `unreviewed` until a feed is approved.
- Any change to this procedure needs Vivi's approval and a dated entry
  in the run log; the engine's `requires_context_review` behaviour is
  unchanged by this document.

## Engineering v0.2.2 clarification (2026-11-21)

The older notes above correctly define the **official V1.0 behavior**: the default engine remains qualitative-only for nine `context` indicators. The inability to publish a numeric L1 score is a consequence of the existing methodology, not a reason to fabricate a numeric replacement.

A separate, disabled-by-default `V1.1-proposal` research mode has been implemented to test a future, formally versioned methodology change. This is **NOT** GLT V1.1 approval or release. It is **NOT** used by the ChatGPT daily/weekly publishing tasks and cannot issue an official composite score. It requires an explicitly approved review matching the selected observation's date, exact raw value, published-at timestamp and source URL, plus reviewer, rationale, evidence URL and a `V1.1-proposal` version tag. No review from the future is valid in a historical as-of run. Invalid or missing reviews remain unscorable. A stricter production roll-out still requires separate attestation, signatures and retrospective methodology impact analysis.

Test opt-in: `python src/glt.py --method-version V1.1-proposal --asof 2026-11-21T08:00:00+08:00`. Official run: omit `--method-version` (defaults to `V1.0`). The official score remains blocked unless an approved formal methodology change is published.
