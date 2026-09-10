# Koyeb Backend Deployment — Copy-Paste Values

## Before you start

Both files are committed and pushed:
- `Dockerfile` (repo root) — builds the backend as the `backend.main:app` package
- `.gitignore` excludes `.env`, so secrets stay local

## Steps (Koyeb dashboard)

1. Go to **https://app.koyeb.com** → sign in with GitHub (Koyeb free tier needs **no credit card**)
2. **Create App** → connect your GitHub account → select the **RepoGuide** repo
3. Koyeb detects the `Dockerfile` automatically. Set:
   - **Service name**: `repoguide-backend`
   - **Instance type**: **Free** (512 MB / 0.1 vCPU)
   - **Ports**: HTTP `8000`
4. In **Environment variables**, add these 4 (values from your local `.env`):

```
DATABASE_URL=postgresql+asyncpg://postgres.rluwjoextivwwtpzibqe:GreatRepoguide@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres
GEMINI_API_KEY=<from .env>
JINA_API_KEY=<from .env>
JWT_SECRET=<from .env>
```

5. **Deploy** → wait for the build (~3-5 min, installing torch is the slow part)

## After deploy

1. Open the Koyeb app URL (form: `https://<service>-<app>.koyeb.app`)
2. Verify: `GET /` returns `{"message": "RepoGuide running"}`
3. That URL becomes the frontend's `NEXT_PUBLIC_API_BASE_URL` on Vercel

## Notes

- First request after deploy downloads the embedding model (~90 MB) — allow a few seconds.
- Koyeb free is always-on (no idle spin-down like Render), so no cold-start delays.
- If the build fails, scroll the build log: torch/python-version wheel issues will show there.