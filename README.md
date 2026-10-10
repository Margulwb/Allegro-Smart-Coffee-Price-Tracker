# Coffee Deal Observer

Local-first price monitoring and AI-assisted alert demo. The whole stack runs in WSL with
rootless Podman; it needs no paid cloud account. Offer data is synthetic until an authorized
source is connected. The AI only explains alerts and has no write, deployment, or purchasing
capabilities.

## Start on AlmaLinux WSL

Requirements: Podman 5+, Python 3.11+, and a working WSL network connection.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
cp .env.example .env
source .venv/bin/activate
podman compose up --build -d
```

The `dev` extra installs `podman-compose`, the provider used by `podman compose` when no
Compose plugin is bundled with Podman. Run these commands from the repository root.

- Grafana dashboard: <http://localhost:3000/d/coffee-deal-observer/coffee-deal-observer> (`admin` / password from `.env`)
- API docs: <http://localhost:8000/docs>
- VictoriaMetrics: <http://localhost:8428/vmui/>
- Alertmanager: <http://localhost:9093>

Grafana provisions the VictoriaMetrics datasource and Coffee Deal Observer dashboard on
startup. VictoriaMetrics scrapes the API every 15 seconds and retains data for 90 days. The
first graph appears after the first scrape. The demo offer has a fixed synthetic price, so
its plot will be flat until a real authorized data source is implemented.

The current local data volume was initialized with `admin` / `local-dev-only`. On a fresh
volume, use the password configured in `.env` (the example is intentionally local-only).

For a local Ollama model, set `OLLAMA_BASE_URL` and `OLLAMA_MODEL` in `.env`, then make the
model available to Ollama. To enable Discord, set `DISCORD_WEBHOOK_URL`. Do not put secrets
in Git. The sample Grafana password is only for local development; change it in `.env`.

Keep the named data volumes while stopping the stack:

```bash
podman compose down
```

Remove stored metrics and Grafana state only when you explicitly want a clean reset:

```bash
podman compose down -v
```

## Start automatically in WSL

The systemd user unit runs the whole Compose stack and keeps the named data volumes when
stopped. From WSL, install and enable it with:

```bash
sudo loginctl enable-linger mg
bash scripts/install-systemd-user-service.sh
```

Check it with `systemctl --user status coffee-observer.service`. Stop/start it with
`systemctl --user stop coffee-observer.service` and
`systemctl --user start coffee-observer.service`.

WSL does not start a distro just because Windows boots. To start AlmaLinux at Windows user
logon as well, run `scripts/register-wsl-autostart.ps1` once from PowerShell. It creates a
shortcut in the current user's Startup folder that starts the distro; linger then starts the
enabled user unit. This runs at user logon, not before anyone signs into Windows.

## Verify

```bash
.venv/bin/python -m ruff check app tests
.venv/bin/python -m pytest -q
podman compose ps
```
