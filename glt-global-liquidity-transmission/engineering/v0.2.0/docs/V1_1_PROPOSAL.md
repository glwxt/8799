# GLT V1.1 contextual-scoring proposal — NOT ACTIVE

**Status:** Research proposal, 2026-11-21. No change to approved GLT V1.0.

## Why this exists
In GLT V1.0, all five L1 indicators have a context-dependent interpretation. The existing `docs/CONTEXT_REVIEW.md` requires directional narrative only and explicitly prohibits converting a qualitative decision to a 0-100 score without a formal version change. Therefore the current official engine correctly refuses to invent L1 numerical scores. This was incorrectly described as solely a code bug; the actual issue is a missing formally approved normalization protocol.

## Proposed change, isolated for audit
An optional `--method-version V1.1-proposal` research mode accepts explicitly approved contextual scores only when raw observation date, raw value, release timestamp and source exactly match. Each score records reviewer, review timestamp, evidence URL, rationale and proposed version. The prototype refuses future approvals and does not publish an official GLT composite. The normal V1.0 daily and weekly tasks do not invoke this mode.

## Before any formal approval
1. Define *ex ante* scoring rubrics for reserves, TGA, ON RRP, balance sheet, global USD funding, 10-year nominal yields, dollar funding pressure, safe-haven proxies and Asia equity flows; include counterpart evidence for balance-sheet double-counting and currency normalization.
2. Independently review/approve representative dated examples, including both easing and tightening regimes. A score is not merely a subjective number written after seeing returns.
3. Test rolling normalization, missing-data behavior, regime changes, confidence and inter-reviewer agreement on point-in-time source vintages.
4. Backtest V1.0 qualitative vs proposed V1.1 numerical states, record change in historical coverage and predictive performance; do not overwrite any archived forecast.
5. Issue approved V1.1 change log and a dated future activation boundary; provide signed audit trail and controlled write permissions.
6. Only then update the publication task instructions to opt into the new method.

## Current outcomes
- Official **GLT V1.0**: qualitative context review remains; L1 numeric score can remain unpublished. This is more reliable than a fabricated score.
- Experimental **V1.1-proposal**: can exercise the human-approved numeric path in isolation, never labeled official.
- The system can still publish a qualitative daily/weekly monitoring report with full provenance and data gaps.

Method scores never represent asset upside probabilities.
