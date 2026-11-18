# Nekitosha AutoFarm — multi-user foundation

A free-tier web dashboard and Windows companion Agent for My Lands Steam.

## Included
- Responsive web cabinet with a local demo mode.
- Multi-user Cloudflare Worker API: registration, login, private user settings, rules, army templates, agent pairing and activity.
- Cloudflare D1 schema. Every record is scoped to its owner.
- Windows Agent: process selector for MyLands.exe, one-time pairing, heartbeat and config synchronization.
- GitHub Actions workflow for GitHub Pages.

## Honest feature status
This release is a working account/configuration foundation. It does not yet parse live game state or automatically send missions. The Windows Agent only detects the MyLands.exe process and exchanges the user's own settings with the server. It does not inject DLLs, read/write process memory, intercept authenticated game traffic or send game commands. Do not confuse the current prototype with a completed auto-farming engine.

## Free URLs
- GitHub Pages: https://nekitosha-it.github.io/mlbot/
- Cloudflare Worker API: created when you deploy the worker.
- A custom .app domain is not free. You must already own/register it and configure DNS. The GitHub Pages URL is free.

## 1. Publish the website
1. In GitHub open Settings → Pages.
2. Under Build and deployment select **GitHub Actions**.
3. The workflow `.github/workflows/pages.yml` deploys the `web/` folder after a push to main.

## 2. Deploy API and D1 database using free Cloudflare tiers
1. Create a free Cloudflare account.
2. Install Node.js LTS and run:
   ```powershell
   npm install -g wrangler
   wrangler login
   cd worker
   wrangler d1 create nekitosha-mlbot
   ```
3. Copy the returned database ID into `worker/wrangler.toml`.
4. Create the schema and deploy:
   ```powershell
   wrangler d1 execute nekitosha-mlbot --remote --file=./schema.sql
   wrangler deploy
   ```
5. Copy the Worker URL into `web/config.js` as `API_BASE`, then commit the change.
6. Set Worker variable `ALLOWED_ORIGINS` to `https://nekitosha-it.github.io` (comma-separated if using a custom domain).

## 3. Run the Windows Agent
1. Install Python 3.11+.
2. Run in the `agent/` folder:
   ```powershell
   py -3.11 -m pip install -r requirements.txt
   py -3.11 agent.py
   ```
3. Sign in on the site → Windows Agent → create a one-time pairing code.
4. Enter the Worker URL and pairing code in the Agent, select MyLands.exe and connect.

## Security before opening to the public
The API uses PBKDF2 password hashing, hashed session and Agent tokens, one-use pairing codes and user-scoped queries. Before public launch, add email verification, anti-abuse rate limiting/Turnstile, account deletion, backups, Privacy Policy, Terms of Service and support contact. Never ask users for Steam passwords, cookies or session tickets.
