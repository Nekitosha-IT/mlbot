# Nekitosha AutoFarm — free multi-user foundation

## Included
- Responsive website in web/: rules, army templates, settings, registration/login when API is connected, and local demo mode.
- Cloudflare Worker API in worker/src/index.js: accounts, private settings, rules, army templates, Agent pairing and activity.
- Cloudflare D1 schema in worker/schema.sql.
- Windows companion in agent/: MyLands.exe process selector, one-time pairing, heartbeat and configuration sync.
- GitHub Pages workflow in .github/workflows/pages.yml.
- One-click Windows Cloudflare setup: SETUP-CLOUDFLARE.bat.

## Honest feature status
This is a working website/configuration/API foundation. The live in-game map parser and automatic mission engine have not been implemented yet. The Windows Agent currently detects MyLands.exe and synchronizes settings; it does not inject DLLs, inspect or modify process memory, intercept authenticated game traffic or send game missions. It is not yet a completed auto-farming bot.

## Free website
After one-time Pages enablement, the free address is:
https://nekitosha-it.github.io/mlbot/

A custom .app domain is not free and must be registered/owned separately. It is not required to test the product.

## One-time GitHub Pages setting
1. Open https://github.com/Nekitosha-IT/mlbot/settings/pages
2. Under **Build and deployment**, select **Source: GitHub Actions** and save.
3. Open the Actions tab and run **Deploy Nekitosha AutoFarm** once. Later pushes to web/ publish automatically.

This one-time action must be done by the repository owner: GitHub's default GITHUB_TOKEN cannot create the first Pages site. The workflow is already included.

## Deploy the free API and database
1. Download/clone this repository to Windows.
2. Install Node.js LTS from https://nodejs.org/.
3. Run SETUP-CLOUDFLARE.bat from the repository folder.
4. Sign into your free Cloudflare account in the browser window.
5. The script creates D1, applies worker/schema.sql, deploys the Worker, and writes its URL into web/config.js.
6. If using a Git clone, the script can commit/push the two changed config files. Otherwise upload worker/wrangler.toml and web/config.js to GitHub with GitHub Desktop or the website.
7. After web/config.js is updated in main, GitHub Pages redeploys and the site changes from local demo to multi-user login mode.

The Worker API uses the free Cloudflare Workers and D1 tiers, within their quotas. Check current Cloudflare quotas as usage grows.

## Run the Windows Agent
1. Install Python 3.11+.
2. Run agent/run-agent.bat.
3. Sign into the website → Windows Agent → create a six-digit pairing code.
4. Enter the Worker URL and code in Agent, select MyLands.exe and connect.

## Security before public launch
The API uses PBKDF2 password hashing, hashed session/Agent tokens, one-time pairing codes with a 10-minute expiry, and per-user data queries. Before inviting the public, add email verification, rate limiting/Turnstile, password reset, account deletion, backups, Privacy Policy, Terms of Service and support contact. Never request Steam passwords, cookies, auth tickets or session IDs.
