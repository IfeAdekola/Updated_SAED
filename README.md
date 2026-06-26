# SAED IMS — Skills Acquisition and Entrepreneurship Development Information Management System

A full-stack web application for managing NYSC SAED programs, trainer-corps member connections, course enrollment, and fast track learning content.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, React Router, Lucide React icons, plain CSS |
| Backend | Django 6, Django REST Framework, SQLite (dev), session auth |
| API | REST, JSON, multipart/form-data for file uploads |

## Project Structure

```
Updated_SAED/
├── saed-frontend/        React SPA
│   ├── src/
│   │   ├── components/   Shared UI components
│   │   ├── pages/        Page-level components (auth, admin, dashboard, etc.)
│   │   ├── hooks/        Custom React hooks
│   │   ├── lib/          API wrapper, auth context
│   │   ├── constants/    Validators, skill areas, messages
│   │   ├── data/         Nigerian states/LGAs, activities
│   │   └── styles.css    Global styles
│   ├── public/           Static assets
│   └── package.json
│
├── saed-backend/         Django REST API
│   ├── config/           Settings, root URL config
│   ├── saed/
│   │   ├── views/        API views (auth, programs, trainers, etc.)
│   │   ├── models.py     Profile, Program, Application, Course, etc.
│   │   ├── urls.py       API routes
│   │   ├── admin.py      Django admin
│   │   └── management/   Seed and migration commands
│   ├── requirements.txt
│   └── manage.py
│
└── README.md             This file
```

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- npm

### Backend

```bash
cd saed-backend
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_saed          # optional: load demo data
python manage.py runserver 8002     # http://127.0.0.1:8002/api/
```

### Frontend

```bash
cd saed-frontend
npm install
npm start                           # http://localhost:3002
```

The frontend proxies `/api` requests to `http://127.0.0.1:8002` during development.

## Demo Accounts

Created by `python manage.py seed_saed`:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@saed.test | password123 |
| Trainer | trainer@saed.test | password123 |
| Corps Member | member@saed.test | password123 |

## Features

- **Corps Members**: Browse programs, apply, track applications, connect with trainers, select skill interests, fast track learning
- **Trainers**: Manage assigned programs, review applications, create courses, upload fast track videos, view connected corps members
- **Admins (SAED)**: Create/edit programs, manage users, authorize trainers, review applications
- **Admins (DUNIS)**: Manage payments, fast track access, trainer authorization, complaints
- **Public**: Program browsing, camp activities, opportunities, password reset

## Roles

| Role | Key Permissions |
|------|----------------|
| `corps_member` | Apply to programs, view own applications, connect with trainers |
| `trainer` | Manage assigned programs, review applications, create courses |
| `saed_admin` | Full program/user management, create admin accounts |
| `dunis_admin` | Payment management, fast track access, complaints |

## Deployment

See [saed-backend/documentation.md](saed-backend/documentation.md) and [saed-frontend/documentation.md](saed-frontend/documentation.md) for detailed setup, API reference, and production notes.
