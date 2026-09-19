# CFB Deep Run

Deployment-ready FastAPI web app for Railway.

## User experience
Open the site, enter two college football team names, and press **RUN DEEP ANALYSIS**. The app automatically uses the configured season and runs 50,000 simulations.

## Required Railway variable
`CFBD_API_KEY` — your CollegeFootballData API key.

Optional:
- `CFB_SEASON=2026`
- `SIMULATIONS=50000`

Railway uses `railway.json` / `Procfile` to start the app and `/health` for health checks.

The app does not invent unavailable injury information. If no trained model bundle is present, it labels the transparent fallback model as uncalibrated.
