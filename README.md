# UPSC Blog – AI-Powered IAS Preparation Platform

A production-ready, fully decoupled UPSC preparation platform with a Django REST API backend and Next.js (App Router) frontend. Features AI-powered answer evaluation, semantic RAG search, automated MCQ generation, and a time-bound subscription engine with Razorpay + Stripe.

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Next.js (SSR)  │────▶│  Django REST API  │────▶│  PostgreSQL     │
│  Port 3000      │     │  Port 8000        │     │  (AWS RDS)      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │      │
                    ┌─────────┘      └─────────┐
                    ▼                          ▼
            ┌──────────────┐          ┌──────────────┐
            │  Redis       │          │  Qdrant      │
            │  (Celery)    │          │  (Vectors)   │
            └──────────────┘          └──────────────┘
                    │
          ┌─────────┴──────────┐
          ▼                    ▼
  ┌──────────────┐    ┌──────────────┐
  │ Celery Worker│    │ Celery Beat  │
  │ (AI Tasks)   │    │ (Scheduler)  │
  └──────────────┘    └──────────────┘
```

## Content Access Matrix

| Layer | Content | Access |
|-------|---------|--------|
| **Free** | Prelims MCQs, Current Affairs, Mains articles, GS Paper categorization | Public + Authenticated |
| **Premium** | AI Answer Evaluator, Semantic RAG Search, Personalized recommendations | Active Subscribers Only (₹500 / 90 days) |

## Tech Stack

- **Backend**: Django 5.1, DRF, SimpleJWT (HttpOnly cookies), Celery, Redis
- **Frontend**: Next.js 14 (App Router), TypeScript, TailwindCSS
- **Database**: PostgreSQL 16 (AWS RDS)
- **Vector Store**: Qdrant (self-hosted on ECS/Fargate)
- **AI**: OpenAI GPT-4o, Claude 3.5 Sonnet, text-embedding-3-small
- **Payments**: Razorpay (UPI/Cards) + Stripe (International)
- **Infrastructure**: AWS ECS Fargate, ALB, S3 + CloudFront, Terraform

---

## Project Structure

```
├── backend/
│   ├── config/                  # Django settings, URLs, WSGI/ASGI, Celery
│   ├── apps/
│   │   ├── accounts/            # Custom User, JWT auth, profile
│   │   ├── blog/                # BlogPost, MCQ, categories, GS papers
│   │   ├── subscriptions/       # Subscription model, IsActiveSubscriber
│   │   ├── payments/            # Razorpay/Stripe order + webhook views
│   │   └── ai_features/         # AI views, serializers, Celery tasks
│   ├── services/
│   │   ├── ai/                  # syllabus_tagger, answer_evaluator, mcq_generator, rag_engine
│   │   └── payments/            # razorpay_service, stripe_service
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router pages
│   │   │   ├── auth/            # Login, Signup
│   │   │   ├── blog/            # Blog list, [slug] detail (SSG)
│   │   │   ├── quiz/            # Daily MCQ quiz
│   │   │   ├── pricing/         # Subscription plans + payment
│   │   │   └── premium/         # AI Evaluator, Semantic Search
│   │   ├── components/          # Navbar, Footer, reusable UI
│   │   ├── services/            # API client wrappers
│   │   ├── lib/                 # Axios instance with interceptors
│   │   └── types/               # TypeScript interfaces
│   ├── Dockerfile
│   └── package.json
├── infrastructure/
│   └── terraform/               # AWS VPC, ECS, RDS, S3, CloudFront IaC
├── docker-compose.yml           # Local dev orchestration
└── README.md
```

---

## Local Development Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 16 (or use Docker)
- Redis 7 (or use Docker)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/sujeet12047624/sujeet-96.git
cd sujeet-96

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Edit .env files with your API keys (OpenAI, Anthropic, Razorpay, Stripe)

# Start all services
docker-compose up --build

# In a separate terminal, run migrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin/
- **Qdrant Dashboard**: http://localhost:6333/dashboard

### Option 2: Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your database credentials and API keys

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver 0.0.0.0:8000
```

#### Celery Workers

```bash
# In a separate terminal (with venv activated)
cd backend

# Start Celery worker
celery -A config.celery worker -l info

# Start Celery Beat scheduler (separate terminal)
celery -A config.celery beat -l info
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment
cp .env.example .env.local

# Start development server
npm run dev
```

---

## Database Migrations

```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Load seed data (if available)
python manage.py loaddata seed_data.json
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/signup/` | Register new user | Public |
| POST | `/api/auth/login/` | Login (sets HttpOnly cookies) | Public |
| POST | `/api/auth/logout/` | Logout (blacklists token) | Required |
| POST | `/api/auth/token/refresh/` | Rotate refresh token | Public |
| GET/PATCH | `/api/auth/profile/` | User profile | Required |

### Blog (Free)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/blog/posts/` | List posts (filterable) | Public |
| GET | `/api/blog/posts/{slug}/` | Post detail | Public |
| POST | `/api/blog/posts/create/` | Create post (admin) | Admin |
| GET | `/api/blog/quiz/?date=YYYY-MM-DD` | Daily MCQ quiz | Public |
| GET | `/api/blog/categories/` | Available categories | Public |

### Subscriptions
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/subscriptions/plans/` | Available plans | Public |
| GET | `/api/subscriptions/me/` | User subscription | Required |
| GET | `/api/subscriptions/transactions/` | Transaction history | Required |

### Payments
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/payments/razorpay/create-order/` | Create Razorpay order | Required |
| POST | `/api/payments/stripe/create-session/` | Create Stripe session | Required |
| POST | `/api/payments/webhook/razorpay/` | Razorpay webhook | Public (verified) |
| POST | `/api/payments/webhook/stripe/` | Stripe webhook | Public (verified) |

### AI Features (Premium)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/ai/evaluate/` | Mains answer evaluation (streaming) | Premium |
| POST | `/api/ai/search/` | Semantic RAG search | Premium |
| GET | `/api/ai/health/` | AI service health check | Public |

---

## Payment Integration Testing

### Razorpay Test Mode

```bash
# Use Razorpay test keys from https://dashboard.razorpay.com/app/keys
# Test card: 4111 1111 1111 1111 (any future expiry, any CVV)
# Test UPI: success@razorpay

# For webhook testing, use Razorpay's webhook test suite:
# Dashboard → Webhooks → Test Webhook
```

### Stripe Test Mode

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe  # macOS
# or download from https://stripe.com/docs/stripe-cli

# Login to Stripe
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/api/payments/webhook/stripe/

# Trigger a test payment
stripe trigger checkout.session.completed

# Test card: 4242 4242 4242 4242 (any future expiry, any CVV, any ZIP)
```

---

## AI Features Configuration

### Required API Keys

1. **OpenAI** (`OPENAI_API_KEY`): For GPT-4o syllabus tagging, MCQ generation, and embeddings
2. **Anthropic** (`ANTHROPIC_API_KEY`): For Claude 3.5 Sonnet answer evaluation
3. **Qdrant**: Self-hosted vector store (included in docker-compose)

### Ingesting Documents

```python
# Django management shell
python manage.py shell

from services.ai.rag_engine import RAGEngine
engine = RAGEngine()

# Ingest a PDF
engine.ingest_pdf("/path/to/ncert.pdf", {"title": "NCERT History", "subject": "gs1"})

# Ingest text
engine.ingest_text("Article content...", {"title": "Article Title", "category": "mains"})
```

---

## Production Deployment (AWS)

### Prerequisites

- AWS CLI configured with appropriate IAM permissions
- Terraform >= 1.5 installed
- Docker installed for building images

### Step 1: Provision Infrastructure

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Plan (review changes)
terraform plan -var="db_username=admin" -var="db_password=YOUR_SECURE_PASSWORD"

# Apply
terraform apply -var="db_username=admin" -var="db_password=YOUR_SECURE_PASSWORD"
```

### Step 2: Build & Push Docker Images

```bash
# Get ECR login
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-south-1.amazonaws.com

# Build and push backend
cd backend
docker build -t upsc-blog-backend .
docker tag upsc-blog-backend:latest <account-id>.dkr.ecr.ap-south-1.amazonaws.com/upsc-blog-backend:latest
docker push <account-id>.dkr.ecr.ap-south-1.amazonaws.com/upsc-blog-backend:latest

# Build and push frontend
cd ../frontend
docker build -t upsc-blog-frontend .
docker tag upsc-blog-frontend:latest <account-id>.dkr.ecr.ap-south-1.amazonaws.com/upsc-blog-frontend:latest
docker push <account-id>.dkr.ecr.ap-south-1.amazonaws.com/upsc-blog-frontend:latest
```

### Step 3: Update SSM Parameters

```bash
# Store secrets in AWS SSM Parameter Store
aws ssm put-parameter --name "/upsc-blog/production/django-secret-key" --value "YOUR_KEY" --type SecureString --overwrite
aws ssm put-parameter --name "/upsc-blog/production/db-password" --value "YOUR_DB_PASSWORD" --type SecureString --overwrite
aws ssm put-parameter --name "/upsc-blog/production/openai-api-key" --value "sk-..." --type SecureString --overwrite
aws ssm put-parameter --name "/upsc-blog/production/razorpay-key-secret" --value "..." --type SecureString --overwrite
```

### Step 4: Run Migrations

```bash
# Execute migration via ECS exec
aws ecs execute-command \
  --cluster upsc-blog-cluster \
  --task <task-id> \
  --container backend \
  --interactive \
  --command "python manage.py migrate"
```

### Step 5: Verify Deployment

```bash
# Check ALB DNS
terraform output alb_dns_name

# Verify backend health
curl https://<alb-dns>/api/ai/health/

# Verify frontend
curl https://<alb-dns>/
```

---

## Rate Limiting

| Endpoint Type | Rate Limit | Scope |
|--------------|------------|-------|
| Global API | 60 req/min | Per user |
| Auth (login/signup) | 5 req/min | Per IP |
| Premium AI | Active subscription required | 403 if expired |

---

## Subscription Model

- **Plan**: Premium Access Tier
- **Price**: ₹500
- **Duration**: 90 days (strict)
- **Validation**: `IsActiveSubscriber` permission class checks `timezone.now() <= subscription.end_date` on every premium endpoint hit
- **Webhooks**: Idempotent with cryptographic signature verification

---

## License

MIT License. See [LICENSE](LICENSE) for details.
