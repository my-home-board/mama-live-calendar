# LIVE SCHEDULE

One public `.ics` subscription calendar generated daily from configured official artist schedule pages.

## Setup
1. Upload all files and folders to a **public** GitHub repository (including `.github/workflows/update.yml`).
2. In **Settings > Pages**, select **Deploy from a branch**, branch **main**, folder **/docs**, then Save.
3. In **Actions > Update live calendar**, choose **Run workflow**. Confirm success and `docs/live.ics` exists.
4. Subscribe in Apple Calendar to `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/live.ics` (replace both placeholders). On iPhone: Calendar > Calendars > Add Calendar > Add Subscription Calendar.

## Artists
Edit `artists.json`. Set `enabled` to false to remove an artist from the generated feed. To add an artist with a different website structure, implement an adapter in `generate.py`; only `fanpla_schedule` is currently supported. The feed includes events from the current month through 12 months ahead, with past dates excluded.

## Important
- Calendar subscriptions are **read-only**, and Apple controls refresh delays.
- The scraper relies on the public HTML structure and may require maintenance if the source changes.
- Start time uses door opening when listed. End times are placeholders (3 hours), not verified performance end times.
- A failed scrape does not commit a new calendar; check GitHub Actions logs.
- This public calendar reveals the selected artists, not your personal iCloud account or private calendar.
