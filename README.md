# ai-fitness-coach-286a94

AI-powered fitness coach app for busy professionals aged 25-45. It combines biometric onboarding, adaptive workout generation, nutrition planning, progress logging, and subscription-aware coaching flows.

## Apps

- `frontend/` — Next.js marketing and product UI.
- `backend/` — FastAPI service with SQLite persistence for profiles, plans, logs, dashboard summaries, and Stripe webhooks.

## Local development

```bash
cd frontend && npm install && npm run dev
```

```bash
cd backend && uvicorn main:app --reload
```

Backend auth accepts bearer tokens. For local development, use `Authorization: Bearer dev_<user_id>` to address one test profile without external auth setup.
