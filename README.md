# ⚡ FlashShop — Flask Ecommerce

A full-featured Flask ecommerce demo built with Flask, with **admin** and **user** roles.

## Features

- 🛍️ **Shoppers**: browse/search products, view product details, add to cart, update cart, checkout, view their orders.
- 🛠️ **Admins**: dashboard with stats (products / users / orders / revenue / low stock), full **CRUD for products** (create, read, update, delete).
- 👤 **Auth**: register + login/logout with roles (`admin` / regular user).

## Tech

- Flask + Flask-SQLAlchemy (SQLAlchemy ORM)
- Server-rendered Jinja2 templates + Bootstrap 5
- SQLite locally, any Postgres-compatible DB via `DATABASE_URL` (e.g. Vercel Postgres / Neon)

## Default admin

- username: `admin`
- password: `admin123` (override with `ADMIN_PASSWORD` env var)

## Run locally

```bash
python3 -m pip install -r requirements.txt
python main.py
```

Then open <http://127.0.0.1:5000>

- Admin: <http://127.0.0.1:5000/auth/login> → `admin` / `admin123`
- Register a normal user from the Register page.

## Deploy to Vercel

The repo is ready for Vercel (Flask runtime, single serverless function).

1. Push this folder to a Git repo.
2. `vercel` CLI: `vercel` → import project → set env vars:

| Variable | Example / default | Purpose |
|---|---|---|
| `DATABASE_URL` | `postgresql://user:pass@host/dbname` | Postgres for production (SQLite won't persist on Vercel). Use Vercel Postgres / Neon. |
| `SECRET_KEY` | any random string | Flask session secret. |
| `ADMIN_PASSWORD` | `admin123` | Admin login password. |

3. Deploy: `vercel --prod` (or `vercel deploy`).

Notes:

- The entrypoint is `main.py` (module-level `app = create_app()`) — the same pattern Vercel uses for zero-config Flask deploys.
- On Vercel the app runs as a single serverless function; it creates its tables and seeds the admin on boot.
- For production, use a persistent Postgres database via `DATABASE_URL` (SQLite is ephemeral there).

## Project layout

```
main.py            # Flask app factory + instance + local run
models.py          # SQLAlchemy models (User, Product, Order, OrderItem)
helpers.py         # login_required / admin_required / current user helpers
auth.py            # /auth routes (login, logout, register)
products.py        # /products + /admin CRUD blueprints
cart.py            # /cart routes (session cart)
orders.py          # /orders + /checkout (place order, stock decrease)
templates/         # Jinja2 templates (Bootstrap 5)
static/css/        # custom CSS
vercel.json        # Vercel function config
requirements.txt
```
