# Shared TypeScript Schemas - Directory Index

**Complete type system for multimodal disaster-response and supply chain disruption detection**

## 📁 Files Overview

| File | Purpose | When to Use |
|------|---------|-------------|
| **[GETTING_STARTED.md](GETTING_STARTED.md)** | 5-minute quick start guide | **START HERE** - First time using these types |
| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | Quick reference & cheat sheet | Daily coding reference, common patterns |
| **[examples.ts](examples.ts)** | Complete real-world examples | Copy-paste templates, implementation guide |
| **[shared-schemas.ts](shared-schemas.ts)** | Core type definitions | Source of truth, understanding contracts |
| **[validation.ts](validation.ts)** | Validation & utility functions | Runtime validation, helper functions |
| **[index.ts](index.ts)** | Central export point | Import types into your code |
| **[README.md](README.md)** | Comprehensive documentation | Deep understanding, integration guide |
| **[TYPE_ARCHITECTURE.md](TYPE_ARCHITECTURE.md)** | Architecture diagrams | Understanding relationships, data flow |
| **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** | Implementation details | Project overview, statistics |
| **[package.json](package.json)** | Package configuration | npm/yarn setup |
| **[tsconfig.json](tsconfig.json)** | TypeScript configuration | Compiler settings |

## 🎯 Quick Navigation

### I want to...

#### **Get started quickly**
→ [GETTING_STARTED.md](GETTING_STARTED.md)

#### **Look up a type or pattern**
→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

#### **See real examples**
→ [examples.ts](examples.ts)

#### **Understand a specific type**
→ [shared-schemas.ts](shared-schemas.ts) (search for the type)

#### **Validate data at runtime**
→ [validation.ts](validation.ts)

#### **Import types in my code**
```typescript
import { FusedEvent, SeverityLevel } from './backend/types';
```

#### **Understand the architecture**
→ [TYPE_ARCHITECTURE.md](TYPE_ARCHITECTURE.md)

#### **Read full documentation**
→ [README.md](README.md)

#### **See project statistics**
→ [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

## 📊 Key Statistics

- **Total Lines**: 3,565+ (code + documentation)
- **TypeScript Code**: 2,111 lines
- **Documentation**: 1,454 lines
- **Core Types**: 17 main types
- **Enumerations**: 5 comprehensive enums
- **Validation Functions**: 20+ functions
- **Utility Functions**: 15+ helpers
- **Examples**: Complete real-world scenario

## 🏗️ Type Categories

### Input Layer
- `IncidentInputRequest` - API entry point
- `TextSignal` - Text reports, social media
- `VisionSignal` - Imagery, video
- `QuantSignal` - Sensor data, IoT

### Processing Layer
- `ExtractedObservation` - Intermediate analysis
- `FusedEvent` - Primary output
- `DisruptionAssessment` - Impact analysis

### Output Layer
- `AlertRecommendation` - Decision support
- `MapFeaturePayload` - Map visualization
- `DashboardSummary` - Situational awareness
- `FinalApiResponse` - Complete response

### Supporting Types
- `LocationReference` - Geographic data
- `TimeReference` - Temporal data
- `SourceDescriptor` - Source metadata
- `TraceContext` - Request tracking
- `AppError` - Error handling

## 🚀 Common Workflows

### 1. First Time Setup
```
START → GETTING_STARTED.md
     → Try examples from examples.ts
     → Read QUICK_REFERENCE.md
     → Start coding!
```

### 2. Daily Development
```
Need a type? → QUICK_REFERENCE.md
Need validation? → validation.ts
Stuck? → examples.ts
Deep dive? → shared-schemas.ts
```

### 3. Understanding Architecture
```
TYPE_ARCHITECTURE.md → See relationships
README.md → Full context
IMPLEMENTATION_SUMMARY.md → Project details
```

## 📖 Recommended Reading Order

### For New Developers
1. **[GETTING_STARTED.md](GETTING_STARTED.md)** - 5 minutes
2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - 10 minutes
3. **[examples.ts](examples.ts)** - 15 minutes (study the examples)
4. Start coding with types!

### For Technical Leads
1. **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Overview
2. **[TYPE_ARCHITECTURE.md](TYPE_ARCHITECTURE.md)** - Architecture
3. **[README.md](README.md)** - Full documentation
4. **[shared-schemas.ts](shared-schemas.ts)** - Implementation details

### For Integration Work
1. **[README.md](README.md)** - Integration section
2. **[examples.ts](examples.ts)** - Real-world patterns
3. **[validation.ts](validation.ts)** - Validation utilities
4. **[shared-schemas.ts](shared-schemas.ts)** - Type contracts

## 🔍 Search Tips

### Find a type definition
```bash
grep -n "interface FusedEvent" shared-schemas.ts
```

### Find all uses of a type
```bash
grep -n "FusedEvent" *.ts
```

### Find validation for a specific field
```bash
grep -n "isValidConfidence" validation.ts
```

### Find examples of a pattern
```bash
grep -n "TextSignal\|VisionSignal" examples.ts
```

## 📚 External Resources

### Related Documentation
- Project README: `../../README.md`
- Architecture: `../../ARCHITECTURE.md`
- Tech Stack: `../../TECH_STACK.md`

### Frontend Integration
- Frontend Types: `../../frontend/src/types/event.ts`

### Backend Integration
- API Routes: `../../backend/api/routes/`
- Services: `../../backend/services/`

## 🆘 Troubleshooting

### Types not recognized in IDE?
1. Check TypeScript version (need 5.0+)
2. Restart TypeScript server
3. Check tsconfig.json paths

### Import errors?
```typescript
// ✅ Correct
import { FusedEvent } from './backend/types';

// ❌ Wrong
import { FusedEvent } from './backend/types/shared-schemas';
```

### Validation not working?
```typescript
// ✅ Import validation utilities
import { validateSignal } from './backend/types';

// Run validation
const result = validateSignal(data);
if (!result.valid) {
  console.error(result.errors);
}
```

### Need help?
1. Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for common patterns
2. Look at [examples.ts](examples.ts) for working code
3. Read [README.md](README.md) for detailed docs
4. Review [TYPE_ARCHITECTURE.md](TYPE_ARCHITECTURE.md) for architecture

## ✅ Quality Checklist

- ✅ Zero TypeScript errors
- ✅ All types documented with JSDoc
- ✅ Comprehensive examples provided
- ✅ Validation utilities implemented
- ✅ Architecture diagrams created
- ✅ Quick reference guide available
- ✅ Getting started guide written
- ✅ Production-ready design

## 🎓 Learning Path

### Beginner (Day 1)
- [ ] Read GETTING_STARTED.md
- [ ] Try importing a type
- [ ] Copy an example from examples.ts
- [ ] Use QUICK_REFERENCE.md as you code

### Intermediate (Week 1)
- [ ] Read full README.md
- [ ] Implement validation in your API
- [ ] Create custom map features
- [ ] Build a dashboard component

### Advanced (Week 2+)
- [ ] Study TYPE_ARCHITECTURE.md
- [ ] Optimize confidence thresholds
- [ ] Add custom validation rules
- [ ] Contribute improvements

## 🔄 Version Info

**Version**: 1.0.0  
**Created**: March 9, 2026  
**Status**: Production Ready  
**TypeScript**: 5.0+  
**Maintenance**: Active

## 📝 Notes

- All files use TypeScript strict mode
- Validation utilities are optional but recommended
- Examples use realistic data based on actual scenarios
- Types are implementation-agnostic (work with any backend/frontend)

---

**Need help?** Start with [GETTING_STARTED.md](GETTING_STARTED.md)  
**Ready to code?** Import from [index.ts](index.ts)  
**Want details?** Read [README.md](README.md)

