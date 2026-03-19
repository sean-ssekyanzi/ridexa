# Ridexa

A full-stack movie streaming web app built with **FastAPI** (backend) and **React + Vite** (frontend), deployed on Render with a PostgreSQL database.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Features](#features)
- [Environment Variables](#environment-variables)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Database Schema](#database-schema)
- [Frontend Pages & Components](#frontend-pages--components)
- [Payment Integration](#payment-integration)
- [Deployment](#deployment)

---

## Overview

Ridexa lets users browse movies, search, save favourites, and stream titles in-app via embedded players. Authenticated premium users get access to the IMDb Top 100 sidebar, a full movie grid, and an ad-reduced streaming experience. Non-premium users are redirected to the subscription page.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, React Router v7 |
| Backend | FastAPI, SQLAlchemy (async), Alembic |
| Database | PostgreSQL (Render managed) |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Payments | Stripe (card), PayPal, MTN MoMo |
| Movie Data | TMDB API |
| Video Player | vidsrc.icu embed |
| Deployment | Render (backend + DB), Docker Compose (local) |

---

## Project Structure

```
ridexa/
├── main.py                  # FastAPI app, all routes
├── src/
│   ├── config.py            # App config (env vars)
│   └── db/
│       ├── connection.py    # Async SQLAlchemy engine + session
│       ├── models.py        # User, Subscription ORM models
│       ├── schemas.py       # Pydantic schemas
│       └── services.py      # DB helpers, auth, JWT
├── migrations/              # Alembic migrations
│   └── versions/
├── Frontend/frontend/
│   ├── src/
│   │   ├── App.jsx          # Routes
│   │   ├── config.js        # Backend base URL (env var)
│   │   ├── components/
│   │   │   ├── NavBar.jsx       # Top nav with avatar dropdown
│   │   │   ├── MovieCard.jsx    # Movie tile, opens modal on click
│   │   │   ├── MovieModal.jsx   # In-app video player modal
│   │   │   └── PaymentModal.jsx # PayPal / Visa / MTN MoMo tabs
│   │   ├── pages/
│   │   │   ├── Home.jsx         # Public movie grid + search
│   │   │   ├── Protected.jsx    # Auth-gated grid + IMDb Top 100 sidebar
│   │   │   ├── Favorites.jsx    # Saved favourites
│   │   │   ├── Login.jsx        # Login form
│   │   │   ├── RegistrationPage.jsx
│   │   │   └── PremiumPage.jsx  # Subscription pricing page
│   │   ├── hooks/
│   │   │   └── usePremium.js    # Fetches /me, returns isPremium bool
│   │   ├── contexts/
│   │   │   └── MovieContext.jsx # Favourites state (localStorage)
│   │   └── servcs/
│   │       └── mapi.js          # TMDB API helpers
│   └── Dockerfile
├── compose.yml              # Docker Compose (app + db + frontend)
├── Dockerfile               # Backend Docker image
├── pyproject.toml
└── requirements.txt
```

---

## Features

### Public
- Browse popular movies from TMDB
- Search movies by title
- View movie details, trailer link

### Authenticated + Premium (`/protected`)
- Requires both valid JWT and `is_premium = true` — non-premium users redirected to `/premium`, unauthenticated to `/login`
- Full movie grid with search
- IMDb Top 100 sidebar — click any title to open the in-app player
- In-app video player (vidsrc.icu embed) with:
  - Backdrop thumbnail preview
  - Watch Now / Trailer buttons
  - YouTube trailer link
  - Quality selector: 480p / 720p / 1080p (remounts iframe via `iframeKey` to switch quality)
  - Fullscreen button
  - Controls overlay on hover
- Ad-reduced streaming experience

### Premium Subscription
- Unlocked via Stripe, PayPal, or MTN MoMo ($4.99/month)

### Favourites
- Add/remove movies from favourites
- Persisted in localStorage via React context

---

## Environment Variables

### Backend (`.env`)

```env
# Database
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=mydatabase
PORT=10000

# JWT
SECRET_KEY=your_secret_key

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...

# PayPal
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_SECRET=your_paypal_secret

# MTN MoMo
MOMO_SUBSCRIPTION_KEY=your_mtn_subscription_key
MOMO_API_USER=your_uuid
MOMO_API_KEY=your_mtn_api_key
MOMO_ENVIRONMENT=production   # or sandbox

# Frontend URL (for Stripe redirect)
FRONTEND_URL=https://ridexa-frntend.onrender.com
```

### Frontend (`Frontend/frontend/.env`)

```env
VITE_BACKEND_URL=https://app-image6-latest.onrender.com
VITE_PAYPAL_CLIENT_ID=your_paypal_client_id
```

---

## Getting Started

### Local with Docker Compose

```bash
git clone <repo>
cd ridexa
cp .env.example .env   # fill in your values
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173

### Local without Docker

**Backend:**
```bash
uv run fastapi dev
```

**Frontend:**
```bash
cd Frontend/frontend
npm install
npm run dev
```

### Database Migrations

```bash
# Generate a new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head
```

---

## API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | — | Health check |
| POST | `/register` | — | Register new user |
| POST | `/token` | — | Login, returns JWT |
| GET | `/verify-token/{token}` | — | Validate a JWT |
| GET | `/me` | JWT | Get current user + premium status |
| GET | `/users/` | — | List all users |
| POST | `/create-checkout-session` | JWT | Create Stripe Checkout session |
| POST | `/webhook` | Stripe sig | Stripe payment webhook |
| POST | `/paypal-confirm` | JWT | Confirm PayPal order + activate premium |
| POST | `/momo-pay` | JWT | Initiate MTN MoMo payment + activate premium |

---

## Database Schema

### `users`

| Column | Type | Notes |
|---|---|---|
| id | int PK | auto increment |
| username | string | unique |
| hashed_password | string | bcrypt |
| is_premium | bool | default false |

### `subscriptions`

| Column | Type | Notes |
|---|---|---|
| id | int PK | auto increment |
| user_id | int FK | → users.id, unique |
| stripe_customer_id | string | nullable |
| stripe_subscription_id | string | nullable |
| status | string | `active` or `cancelled` |
| started_at | datetime | subscription start |
| expires_at | datetime | nullable |

---

## Frontend Pages & Components

### Pages

| Route | Page | Auth Required |
|---|---|---|
| `/` | Home | No |
| `/login` | Login | No |
| `/register` | RegistrationPage | No |
| `/favorites` | Favorites | No |
| `/protected` | Protected | Yes (+ Premium) |
| `/premium` | PremiumPage | Yes |

### Key Components

**NavBar** — shows Home, Favorites links. When logged in shows avatar bubble (first letter, gold circle) with dropdown: My Movies (premium) or Go Premium 👑 (non-premium), and Logout. Premium status fetched from `GET /me`.

**MovieCard** — poster tile. Click opens `MovieModal`. Heart button toggles favourite.

**MovieModal** — full in-app player. Shows backdrop, Watch Now / Trailer buttons. On play: embeds vidsrc.icu iframe. Quality switching (480p/720p/1080p) remounts iframe via `iframeKey` state. Fullscreen button and hover-reveal controls overlay included.

**PaymentModal** — 3-tab payment sheet: PayPal button, Visa/card form (redirects to Stripe Checkout), MTN MoMo phone input.

**usePremium** — hook that calls `GET /me` and returns `isPremium` boolean used to enable ad-reduced embed.

---

## Payment Integration

### Stripe (Visa / Card)
1. User clicks Subscribe Now → PaymentModal opens → Card tab
2. Frontend calls `POST /create-checkout-session` → gets Stripe URL
3. User redirected to Stripe Checkout
4. On success Stripe calls `POST /webhook` → `is_premium = True` + `Subscription` row created
5. On cancellation webhook sets `status = cancelled`, `is_premium = False`

### PayPal
1. User clicks PayPal tab → PayPal button rendered via `@paypal/react-paypal-js`
2. On approval frontend calls `POST /paypal-confirm` with `order_id`
3. Backend verifies order with PayPal API → activates premium

### MTN MoMo
1. User enters phone number → `POST /momo-pay`
2. Backend calls MTN Collections API (`requesttopay`)
3. User receives payment prompt on their phone
4. On `202` response premium is activated

---

## Deployment

Both services are deployed on **Render**.

| Service | URL |
|---|---|
| Backend | https://app-image6-latest.onrender.com |
| Frontend | https://ridexa-frntend.onrender.com |
| Database | Render PostgreSQL (Oregon) |

### Re-deploy after changes
Push to your connected GitHub branch — Render auto-deploys on push.

### Stripe Webhook
Register `https://app-image6-latest.onrender.com/webhook` in your Stripe dashboard under Developers → Webhooks. Listen for:
- `checkout.session.completed`
- `customer.subscription.deleted`
