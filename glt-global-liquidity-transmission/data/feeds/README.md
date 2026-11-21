# GLT machine-readable evidence feed

The workflow at `.github/workflows/glt-fred-staging.yml` is configured for **07:10 Asia/Taipei** daily, and may start later depending on GitHub Actions.

After a successfully executed workflow that has permission to push to `main`, it updates:
- [fred_latest.json](./fred_latest.json) — stable machine-readable collection metadata, six numeric source series where available, errors and timing
- [fred_latest.md](./fred_latest.md) — human-readable evidence overview

**These two files do not exist until the first successful workflow publication.**
Their presence is not proof that today's workflow ran: always inspect `data_retrieved_at_taipei`, `collection_status`, `success_count`, each `observation_date`, and each `release_timestamp_verified`. If yesterday's file is still present, report it as stale and never label it today's readings.

## Truth and safety boundary
- The snapshot is fetched from FRED graph CSV **current-vintage values**, not the original historical publication version.
- The raw CSVs remain in GitHub Actions artifacts for 30 days, together with `manifest.json`; checksums on the feed identify those files.
- `eligible_for_official_glt_score=false` and `input_to_official_glt_engine=false` are permanent by design.
- Six series downloaded successfully do NOT mean six out of 19 official GLT indicators are scored. The score-coverage requirement is calculated separately by the formal methodology.
- Even when a file has the current calendar date, the **observation date** of each series can be older because of market hours and weekly publication schedules.
- Never infer GLT/BTC-GT/GOLD-GT/EQUITY-GT signals directly from this feed without independent data and method review.
- Do not modify existing GLT V1.0 methodology or historical forecast logs.

## Delivery diagnostics
1. Examine [GitHub Actions](https://github.com/glwxt/8799/actions/workflows/glt-fred-staging.yml).
2. A failing workflow may still commit a `DEGRADED` manifest recording missing series; this is intentional.
3. A runner failure, missing GitHub Actions permission, or failed push can leave the last snapshot in place. The report must explicitly say "no new confirmed capture" in this case.
4. ChatGPT daily/weekly publishing tasks are independent from GitHub Actions. They should read this JSON **only if available**, verify source timestamps and status, and still fetch primary information independently. An Actions artifact is not automatically transferred into a ChatGPT task.

First full end-to-end execution and CI status still require confirmation. No historical values are fabricated in this directory.
