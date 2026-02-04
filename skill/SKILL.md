---
name: hdcp-project-generator
description: Use when rapidly generating production-ready websites from Product Requirements Documents using HDCP platform template
---

# HDCP Project Generator

## Overview
Automatically generate complete HDCP-based web applications (FastAPI + Next.js + Strapi) from Product Requirements Documents in minutes, not days.

## When to Use

**Use when:**
- Need to create new HDCP platform websites quickly
- Have a PRD with clear entity definitions (Entity: Name, fields, types)
- Want production-ready code with best practices built-in
- Standard business scenarios: stock tracking, IoT monitoring, e-commerce, carbon credits

**Not for:**
- Complex custom architectures outside HDCP
- PRDs without clear entity definitions
- One-off scripts or utilities

## Quick Usage

```bash
# Invoke the skill
/skill superpowers:hdcp-project-generator

# Required parameters
--prd_path=docs/my-prd.md
--scenario=stock|iot|ecommerce|carbon

# Optional parameters
--features=authentication,real-time,i18n
--output_path=my-project
```

## What Gets Generated

**Backend:**
- SQLAlchemy models for all entities
- FastAPI routers with CRUD endpoints
- Pydantic schemas for validation
- Database migrations (Alembic)

**Frontend:**
- Next.js 14 app with TypeScript
- React components with Tailwind CSS
- Multi-language support (8 languages)
- Responsive dashboard layouts

**Infrastructure:**
- Docker deployment configs
- Nginx load balancer
- Monitoring (Prometheus, Grafana)
- Health checks and metrics

**Documentation:**
- Setup and deployment guides
- API documentation
- Generated project docs

## Workflow

1. **Parse PRD** - Extract entities, fields, relationships
2. **Copy Template** - Initialize HDCP platform structure
3. **Generate Models** - Create SQLAlchemy models
4. **Generate APIs** - Build FastAPI endpoints
5. **Generate UI** - Create React components
6. **Configure** - Update settings and docs

See `implementer-prompt.md` for detailed implementation steps.

## Supported Scenarios

| Scenario | Entities | Components |
|----------|----------|-----------|
| **stock** | StockPrice, Indicator, Alert | StockChart, PriceTicker |
| **iot** | Sensor, Reading, Alert | SensorMap, LiveDashboard |
| **ecommerce** | Product, Price, Alert | ProductCard, ComparisonTable |
| **carbon** | Project, Credit, Impact | ProjectMap, ImpactDashboard |

## Example PRD

```markdown
## Entity: Stock
- symbol: String - Stock ticker symbol
- price: DECIMAL - Current price
- volume: BigInteger - Trading volume
- timestamp: DateTime - Price timestamp

## Features
- Real-time price updates
- Price alerts
- Multi-language support
```

Result: Complete stock tracking platform in ~5 minutes.

## See Also

- `implementer-prompt.md` - Detailed generation workflow
- `spec-reviewer-prompt.md` - PRD compliance checklist
- `code-quality-reviewer-prompt.md` - Code quality standards
- `metadata.json` - Full input/output specifications
