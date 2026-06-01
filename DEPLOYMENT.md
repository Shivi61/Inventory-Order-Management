# Deployment Guide

This walks through publishing the backend image to Docker Hub and deploying the
app on free hosting: **Render** (backend + PostgreSQL) and **Vercel** (frontend).
Netlify and Railway are noted as alternatives.

You'll need accounts on: GitHub, Docker Hub, Render, and Vercel.

---

## 0. Push the code to GitHub

```bash
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main
```

---

## 1. Publish the backend image to Docker Hub

Replace `<dockerhub-user>` with your Docker Hub username.

```bash
docker login

# Build the backend image
docker build -t <dockerhub-user>/inventory-backend:latest ./backend

# Push it
docker push <dockerhub-user>/inventory-backend:latest
```

Your image link will be:
`https://hub.docker.com/r/<dockerhub-user>/inventory-backend`

---

## 2. Deploy the backend on Render

Render can build the Docker image straight from the repo using `render.yaml`.

1. Go to the Render dashboard → **New → Blueprint**.
2. Connect your GitHub repo. Render reads `render.yaml` and proposes a web
   service (`inventory-backend`) plus a free PostgreSQL database (`inventory-db`).
3. Click **Apply**. Render creates the database and injects `DATABASE_URL`
   automatically (via `fromDatabase` in the blueprint).
4. After the first deploy, set the `CORS_ORIGINS` env var to your frontend URL
   (you'll get it in step 3). For now you can leave it; we'll come back.
5. Wait for the service to go live. Confirm the health check:
   `https://inventory-backend-xxxx.onrender.com/health` → `{"status":"ok"}`
   and the docs at `/docs`.

> **Note:** the free Render database is fine for a demo. The free web service
> sleeps after inactivity, so the first request after idle is slow.

**Alternative — Railway:** New Project → Deploy from GitHub → add a PostgreSQL
plugin → set the backend service root to `/backend` (Dockerfile detected) →
copy the database URL into a `DATABASE_URL` variable.

---

## 3. Deploy the frontend on Vercel

1. Go to Vercel → **Add New → Project** → import the GitHub repo.
2. Set **Root Directory** to `frontend`.
3. Framework preset: **Vite**. Build command `npm run build`, output `dist`
   (Vercel detects these).
4. Add an environment variable:
   - `VITE_API_URL` = your live backend URL from step 2
     (e.g. `https://inventory-backend-xxxx.onrender.com`)
5. Deploy. You'll get a URL like `https://<project>.vercel.app`.

**Alternative — Netlify:** New site from Git → base directory `frontend`,
build `npm run build`, publish `frontend/dist`, and add the `VITE_API_URL`
environment variable.

---

## 4. Connect the two

1. Go back to the backend on Render and set:
   - `CORS_ORIGINS` = your Vercel URL (e.g. `https://<project>.vercel.app`)
   - You can list more than one, comma-separated.
2. Redeploy the backend so the new CORS setting takes effect.

---

## 5. Verify the live app

- Open the Vercel frontend URL.
- Add a product, add a customer, create an order.
- Confirm the order reduces stock and the dashboard updates.
- Check the browser console/network tab — requests should hit your Render URL
  with no CORS errors.

---

## Submission checklist

- [ ] GitHub repo link (frontend + backend)
- [ ] Docker Hub image link: `https://hub.docker.com/r/<dockerhub-user>/inventory-backend`
- [ ] Live frontend URL (Vercel/Netlify)
- [ ] Live backend URL (Render/Railway), e.g. `.../docs`
