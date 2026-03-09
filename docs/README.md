# Documentation Folder

## Purpose
Additional project documentation beyond root-level docs (README, ARCHITECTURE, etc.)

## What Belongs Here

**API Documentation:**
- OpenAPI/Swagger specifications
- Endpoint documentation
- Request/response examples

**Deployment Guides:**
- Docker deployment
- Cloud platform setup (AWS, GCP, Azure)
- Environment configuration
- CI/CD pipeline docs

**Development Guides:**
- Local setup troubleshooting
- Database migration guides
- Testing strategies

**Architecture Diagrams:**
- Mermaid diagrams
- System flow charts
- Database schemas

## Examples

```
docs/
├── api/
│   ├── openapi.yaml
│   └── endpoints.md
├── deployment/
│   ├── docker-setup.md
│   └── aws-deployment.md
└── development/
    └── testing-guide.md
```

## What Does NOT Belong Here
- Source code (use appropriate module folders)
- Configuration files (use `/config`)
- Build artifacts
- Temporary notes (use session notes or comments in code)
