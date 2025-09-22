# Archive - Original Framework Files

## 📚 **ARCHIVED FILES**

This directory contains the original framework files that were replaced by the new modular framework in `../v2/`.

### **Files Moved to Archive**
- `framework-execution-guide.md` (504 lines) - Original execution guide
- `unit-test-analysis.md` (429 lines) - Original unit test analysis phases
- `integration-test-analysis.md` (423 lines) - Original integration test analysis phases
- `unit-test-generation.md` (223 lines) - Original unit test generation patterns
- `integration-test-generation.md` (153 lines) - Original integration test generation patterns
- `unit-test-quality.md` (295 lines) - Original unit test quality enforcement
- `integration-test-quality.md` (383 lines) - Original integration test quality enforcement
- `phase-0-setup.md` (237 lines) - Original phase 0 setup

**Total Archived:** ~2,500 lines

---

## 🎯 **WHY ARCHIVED**

### **Problem with Original Framework**
- **Too Large**: 2,500+ lines across 9 files caused AI consumption issues
- **Cognitive Overload**: 500+ line files difficult for AI to process efficiently
- **Poor Navigation**: Critical information buried in verbose documents
- **Context Window Waste**: Large files consumed significant AI context space

### **Solution: New Modular Framework**
- **68% Size Reduction**: 2,500 → 790 lines total
- **Focused Files**: 60-200 lines each with single responsibilities
- **Better AI Consumption**: Direct access to needed information
- **Preserved Quality**: Same rigor, better organization

---

## 🔄 **MIGRATION MAPPING**

### **Where Content Moved**
| Archived File | New Location | Purpose |
|---------------|-------------|---------|
| `framework-execution-guide.md` | `../v2/framework-core.md` | Core rules and commitments |
| | `../v2/phase-checklist.md` | Step-by-step execution |
| | `../v2/enforcement-responses.md` | Violation detection |
| `unit-test-analysis.md` | `../v2/paths/unit-path.md` | Unit test guidance |
| `integration-test-analysis.md` | `../v2/paths/integration-path.md` | Integration test guidance |
| `*-generation.md` files | Integrated into path files | Generation patterns |
| `*-quality.md` files | Integrated into path files | Quality enforcement |
| `phase-0-setup.md` | `../v2/phase-checklist.md` | Setup requirements |

---

## 📖 **USAGE**

### **For Reference Only**
These files are preserved for:
- **Historical reference** - Understanding framework evolution
- **Content verification** - Ensuring nothing was lost in migration
- **Backup purposes** - Fallback if needed during transition

### **Active Development**
**Use the new modular framework in `../v2/` for all active development:**
- Start with `../v2/framework-core.md`
- Follow `../v2/phase-checklist.md`
- Use appropriate path file: `../v2/paths/unit-path.md` or `../v2/paths/integration-path.md`

---

## 🚨 **IMPORTANT**

**These archived files are NOT maintained and may become outdated.**

**Always use the new modular framework in `../v2/` for current test generation work.**
