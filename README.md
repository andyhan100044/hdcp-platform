# HDCP Platform - Production-Ready Web Application Template

A comprehensive, production-ready web application template featuring FastAPI (backend), Next.js 14 (frontend), and Strapi 5 (CMS) with multi-language support, security, and monitoring.

## 🚀 Features

### Core Technologies
- **Backend**: FastAPI with async/await, SQLAlchemy, Pydantic
- **Frontend**: Next.js 14 with TypeScript, React 18, Tailwind CSS
- **CMS**: Strapi 5 with multi-language support
- **Database**: PostgreSQL + TimescaleDB for time-series data
- **Cache/Broker**: Redis

### Production Features
- ✅ **Multi-language Support**: 8 languages (EN, ZH-CN, ES, FR, DE, JA, KO, AR) with RTL support
- ✅ **Security**: Rate limiting, CORS, CSRF protection, input validation, authentication
- ✅ **Performance**: Connection pooling, query optimization, Redis caching
- ✅ **Monitoring**: Prometheus, Grafana, health checks, metrics
- ✅ **Deployment**: Docker Compose, Nginx load balancer, SSL support
- ✅ **i18n**: Auto-detection, user preferences, SEO optimization

### Supported Scenarios
1. **Stock/Financial Data**: Stock price monitoring, indicators, alerts
2. **IoT/Sensor Data**: Sensor readings, device monitoring, alerts
3. **E-commerce**: Product tracking, price history, comparisons
4. **Carbon Credits/ESG**: Carbon projects, credit tracking, impact metrics

## 📁 Project Structure

```
hdcp-platform/
├── apps/                    # Application code
│   ├── api/                 # FastAPI backend
│   │   ├── app/
│   │   │   ├── models/     # SQLAlchemy models
│   │   │   ├── routers/    # API endpoints
│   │   │   ├── schemas/    # Pydantic schemas
│   │   │   └── services/   # Business logic
│   │   └── migrations/     # Database migrations
│   ├── web/                # Next.js frontend
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   ├── lib/          # Utilities and i18n
│   │   └── public/       # Static assets
│   └── cms/              # Strapi CMS
│       ├── config/       # Strapi configuration
│       └── src/          # CMS extensions
├── docs/                  # Documentation
├── monitoring/            # Monitoring configs
│   ├── prometheus/       # Prometheus configuration
│   └── grafana/          # Grafana dashboards
├── nginx/                # Nginx configuration
├── scripts/              # Utility scripts
└── skill/               # HDCP Project Generator Skill
    ├── SKILL.md         # Skill documentation
    ├── metadata.json    # Skill metadata
    ├── implementer.py   # Implementation engine
    └── *.md            # Prompt templates
```

## 🛠️ Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/andyhan100044/hdcp-platform.git
cd hdcp-platform
```

2. **Start with Docker (Recommended)**
```bash
# Copy environment template
cp .env.example .env

# Start all services
docker-compose up -d
```

3. **Manual Setup**

**Backend:**
```bash
cd apps/api
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd apps/web
npm install
npm run dev
```

**CMS:**
```bash
cd apps/cms
npm install
npm run develop
```

### Access Points
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **CMS Admin**: httplocalhost:1337/admin

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/hdcp
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret

# External APIs
# Add your API keys here
```

### Multi-Language Setup

Supported languages:
- English (EN)
- Chinese Simplified (ZH-CN)
- Spanish (ES)
- French (FR)
- German (DE)
- Japanese (JA)
- Korean (KO)
- Arabic (AR) - RTL support

## 🌍 Auto Translation Service

### Overview
HDCP Platform now includes an **enterprise-grade auto translation service** that uses DeepL + multiple LLM providers for high-quality, automated translations.

### Features
- ✅ **8 Languages**: Automatic translation for all supported languages
- ✅ **Quality Control**: DeepL + LLM (GPT-4, Claude, Gemini, ChatGLM) double review
- ✅ **Cost Effective**: 99.2% savings vs manual translation ($43 vs $5,340 per 1000 keys)
- ✅ **Arabic RTL**: Special support for right-to-left languages
- ✅ **Cultural Compliance**: Automatic filtering of sensitive content
- ✅ **Batch Processing**: Handle large content efficiently

### Quick Start
```bash
# Navigate to translation service
cd scripts/translation-service

# Install dependencies
npm install

# Configure API keys
export DEEPL_API_KEY="your-deepl-key"
export OPENAI_API_KEY="sk-your-openai-key"

# Run translation
npm run translate:v2

# Test providers
npm run test:llm
```

### Supported LLM Providers
| Provider | Quality | Speed | Cost | Best For |
|----------|---------|-------|------|----------|
| **Claude** | 9.5/10 | 8/10 | Medium | Enterprise, Arabic |
| **GPT-4** | 9.0/10 | 9/10 | Medium | General purpose |
| **ChatGLM** | 8.0/10 | 9/10 | Low | Chinese projects |
| **Gemini** | 8.0/10 | 8/10 | Low | Cost-effective |

### Documentation
- **Skill**: `skill/translation-skill.md` - Claude Code skill for translation
- **Quick Start**: `scripts/translation-service/QUICK_CONFIG.md` - 5-minute setup
- **LLM Guide**: `scripts/translation-service/LLM_PROVIDER_GUIDE.md` - Provider comparison
- **Full Docs**: `scripts/translation-service/README.md` - Complete documentation

### Example Output
```
✅ Translation complete!
📊 Total: 1092 translations
✅ Auto-approved: 945 (86.5%)
⚠️ Manual review: 147 (13.5%)
📄 Report: translation-quality-report-v2.md
```

## 📊 Monitoring

### Health Checks
- **API Health**: `/health`
- **Readiness**: `/health/ready`
- **Liveness**: `/health/live`
- **Metrics**: `/health/metrics`

### Prometheus Metrics
- Request latency
- Error rates
- Database connections
- Cache hit rates

### Grafana Dashboards
Pre-configured dashboards for:
- API performance
- Database metrics
- Application logs
- Business metrics

## 🛡️ Security

### Implemented Security Layers
1. **Rate Limiting**: IP and user-based limits
2. **CORS**: Configured for production
3. **CSRF Protection**: Token-based
4. **Input Validation**: Pydantic schemas
5. **Authentication**: JWT + API keys
6. **Security Headers**: CSP, HSTS, XSS protection
7. **Audit Logging**: Request/response tracking

## ⚡ Performance

### Optimizations
- **Database**: Connection pooling (QueuePool)
- **Queries**: N+1 problem eliminated
- **Caching**: Redis with TTL
- **Frontend**: Code splitting, lazy loading
- **API**: Async/await throughout

## 🔌 Project Generator Skill

This repository includes the **HDCP Project Generator Skill** for rapidly generating new HDCP-based projects from Product Requirements Documents (PRDs).

### Usage

```bash
# Invoke the skill
/skill superpowers:hdcp-project-generator

# Parameters:
--prd_path=docs/my-prd.md
--scenario=stock|iot|ecommerce|carbon
--features=authentication,real-time,i18n
```

### What Gets Generated
- ✅ SQLAlchemy models from PRD entities
- ✅ FastAPI endpoints with CRUD operations
- ✅ React components with TypeScript
- ✅ Pydantic validation schemas
- ✅ Complete deployment configuration
- ✅ Documentation

See `skill/SKILL.md` for detailed usage instructions.

## 📝 Documentation

- **NEWBIE_GUIDE.md** - Complete setup guide
- **QUICK_START.md** - Quick start instructions
- **DEPLOYMENT_ARCHITECTURE.md** - Production deployment
- **I18N_IMPLEMENTATION.md** - Multi-language setup
- **TEMPLATE_COMPLETE.md** - Complete feature list

## 🧪 Testing

```bash
# Run all tests
docker-compose -f docker-compose.test.yml up

# Or manually
cd apps/api && pytest
cd apps/web && npm test
```

## 🚀 Deployment

### Production Deployment

```bash
# Full stack deployment
docker-compose -f deploy/docker-compose.full.yml up -d

# With monitoring
docker-compose -f deploy/docker-compose.monitoring.yml up -d
```

### Kubernetes

See `docs/KUBERNETES.md` for Kubernetes deployment instructions.

## 📦 What's Included

### Backend (FastAPI)
- SQLAlchemy models with relationships
- Pydantic schemas for validation
- Async database operations
- JWT authentication
- API documentation (Swagger/OpenAPI)
- Health checks and metrics
- Background tasks (Celery)

### Frontend (Next.js 14)
- TypeScript throughout
- Tailwind CSS styling
- Multi-language support
- Responsive design
- Server-side rendering
- API integration
- Form handling

### CMS (Strapi 5)
- Content management
- Multi-language content
- Custom fields
- Role-based permissions
- GraphQL API
- File upload

### Infrastructure
- Docker containers
- Nginx load balancer
- SSL/TLS support
- Monitoring stack
- Log aggregation
- Health checks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 👤 Author

**HDCP Team**

---

## 🌟 Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review the examples

## 🔄 Version History

### v3.0.0 (Current)
- Complete i18n implementation (8 languages)
- Security middleware stack
- Performance optimizations
- Monitoring integration
- Project generator skill

### v2.0.0
- Added Strapi CMS
- Multi-language support
- Security enhancements

### v1.0.0
- Initial release
- FastAPI + Next.js foundation

---

**Built with ❤️ using FastAPI, Next.js, and Strapi**
