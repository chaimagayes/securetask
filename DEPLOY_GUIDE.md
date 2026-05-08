# Deployment Guide — securetask.me

Repo: [Vishal150494/Task-Management-System](https://github.com/Vishal150494/Task-Management-System)

Stack: Flask + PostgreSQL + Gunicorn + Nginx + Certbot (Let's Encrypt) + Docker Compose, deployed to AWS EC2 via GitHub Actions CI/CD.

---

## Files in this package — copy ALL of them into your repo root

```text
Task-Management-System/
├── .github/
│   └── workflows/
│       └── deploy.yml       ← CI/CD pipeline (NEW)
├── nginx/
│   └── conf.d/
│       ├── default.conf     ← Nginx HTTP + ACME challenge (NEW)
│       └── ssl.conf         ← Nginx HTTPS + security headers (NEW)
├── docker-compose.yml       ← REPLACE existing docker-compose.yaml
├── Dockerfile               ← REPLACE existing Dockerfile (fixes bugs + adds gunicorn)
├── entrypoint.sh            ← NEW (runs migrations then starts gunicorn)
├── wsgi.py                  ← NEW (gunicorn entrypoint for your app factory)
└── .env.example             ← reference for the .env secret
```

Your `src/` folder and all application code stay exactly as they are.

---

## What was wrong in the original repo (already fixed in this package)

| File                   | Problem                                                           | Fix                      |
| ---------------------- | ----------------------------------------------------------------- | ------------------------ |
| `Dockerfile`           | CMD syntax bug; used Flask dev server (not production-safe)       | Rewrote to use gunicorn  |
| `docker-compose.yaml`  | `DATABSE_URI` typo; no Nginx/Certbot; no db healthcheck           | Replaced entirely        |
| (missing)              | No WSGI entrypoint for gunicorn to call the app factory           | Added `wsgi.py`          |
| (missing)              | No Nginx, no SSL, no CI/CD                                        | Added all of these       |

---

## Step 1 — Add your email to deploy.yml

Open `.github/workflows/deploy.yml` and replace this line:

```yaml
--email YOUR_EMAIL@example.com
```

with your real email address (used for Let's Encrypt SSL renewal notifications).

---

## Step 2 — Create your .env file

Copy `.env.example` to `.env` and fill in real values:

```bash
SECRET_KEY=<run: python3 -c "import secrets; print(secrets.token_hex(32))">
FLASK_ENV=production
POSTGRES_DB=securetask
POSTGRES_USER=securetask
POSTGRES_PASSWORD=<strong random password>
DATABASE_URI=postgresql://securetask:<your-password>@db:5432/securetask
GUNICORN_WORKERS=2
GUNICORN_THREADS=2
GUNICORN_TIMEOUT=60
```

> Important: this repo uses `DATABASE_URI` (not `DATABASE_URL`). Keep it exactly as above.

Save this file. You will paste the full contents as a GitHub secret in the next step.

---

## Step 3 — Add GitHub Secrets

Go to: your repo on GitHub → Settings → Secrets and variables → Actions → New repository secret.

Add these 4 secrets:

| Secret name   | Value                                              |
| ------------- | -------------------------------------------------- |
| `EC2_HOST`    | Your EC2 Elastic IP (e.g. `54.123.45.67`)          |
| `EC2_USER`    | `ubuntu` (for Ubuntu AMIs)                         |
| `EC2_SSH_KEY` | Full contents of your `.pem` private key file      |
| `ENV_FILE`    | Full contents of your `.env` file                  |

---

## Step 4 — Point your DNS to the EC2 server

In your domain registrar for `securetask.me`, add:

- **A record**: `securetask.me` → your EC2 Elastic IP
- **A record**: `www.securetask.me` → your EC2 Elastic IP

Wait for DNS to propagate (5–30 min). Check with:

```bash
nslookup securetask.me
```

DNS must resolve to your server BEFORE the first deploy — Certbot needs it to issue the SSL certificate.

---

## Step 5 — Make sure your EC2 security group allows these ports

| Port | Protocol | Purpose                              |
| ---- | -------- | ------------------------------------ |
| 22   | TCP      | SSH (for GitHub Actions to connect)  |
| 80   | TCP      | HTTP (needed for Let's Encrypt)      |
| 443  | TCP      | HTTPS                                |

---

## Step 6 — Push to main and watch it deploy

```bash
git add .
git commit -m "feat: add production deployment config"
git push origin main
```

Go to your repo's **Actions** tab on GitHub. The workflow will:

1. Build the Docker image and push it to GitHub Container Registry (GHCR)
2. SSH into your EC2 server
3. Clone the repo and write the `.env`
4. On **first deploy only**: automatically obtain the SSL certificate from Let's Encrypt
5. Start all services: app, db, nginx, certbot

---

## How the SSL bootstrap works (first deploy only)

On the first deploy, no certificate exists yet. The pipeline:

1. Temporarily removes `ssl.conf` so Nginx starts HTTP-only
2. Starts Nginx + App + DB
3. Runs Certbot to get a certificate using the HTTP-01 webroot challenge
4. Restores `ssl.conf` and reloads Nginx to enable HTTPS

All subsequent deploys skip this — the cert is already there and Certbot auto-renews every 12 hours.

---

## Verify it works

```bash
# Should redirect to HTTPS
curl -I http://securetask.me

# Should return 200
curl -I https://securetask.me

# Check certificate dates
echo | openssl s_client -connect securetask.me:443 2>/dev/null | openssl x509 -noout -dates
```

---

## Troubleshooting

**`flask db upgrade` fails on first start** — make sure `DATABASE_URI` in `.env` matches the postgres credentials exactly.

**Nginx exits immediately** — DNS is not pointing to your server yet. Fix DNS, delete the certbot volumes on the server, then re-run the workflow.

**GHCR package is private by default** — after the first push, go to your GitHub profile → Packages → your image → Change visibility to match your repo.

**Gunicorn can't find `wsgi:app`** — make sure `wsgi.py` is in the repo root (same level as `src/`).
