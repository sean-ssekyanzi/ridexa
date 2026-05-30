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
│   ├── domain/              # Pure domain layer (models, use cases, events, ports)
│   ├── application/         # Application services and use case orchestration
│   ├── infrastructure/      # Framework adapters, DI container, HTTP handlers, DB and payment adapters
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

## Architecture

Ridexa uses a layered architecture with strong separation between domain logic and infrastructure.

- **Domain layer**: pure business rules, domain models, use cases, events, and repository ports.
- **Application layer**: service classes that orchestrate use cases and dispatch domain events.
- **Infrastructure layer**: FastAPI handlers, dependency injection, database repositories, payment adapters, and event dispatcher implementation.
- **Dependency injection**: centralized in `src/infrastructure/container.py`, injecting repositories, services, handlers, and the domain event dispatcher across layers.
- **Domain events**: user registration and subscription activation/cancellation emit events through a dispatcher, enabling loose coupling and extensibility.