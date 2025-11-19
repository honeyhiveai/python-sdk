# Workspace Cleanup Plan
**Date:** 2025-11-13  
**Files to organize:** 139 temporary markdown/text files at project root

## Categorization Strategy

### **analysis/** - Deep investigations & research
- Architecture analyses
- Cost/pricing analyses  
- Customer/backend investigations
- Code archaeology reports
- Comparison studies

### **scratch/** - Session tracking & status
- Validation summaries
- Bug reports  
- Progress tracking
- Completion summaries
- Test results
- Fix summaries

### **design/** - Plans & strategies
- Migration plans
- Testing strategies
- Release process docs

### **Keep at root** (legitimate docs)
- CHANGELOG.md
- README.md
- RELEASE_PROCESS.md (if formal)
- ENVIRONMENT_VARIABLES.md (if formal docs)

## Files to Move

### → analysis/
- *_ANALYSIS.md
- *_INVESTIGATION*.md
- *_ARCHAEOLOGY*.md
- *_COMPARISON*.md
- *_ARCHITECTURE*.md
- *_JOURNEY.md
- PRAXIS_OS_*.md

### → scratch/
- *_SUMMARY.md
- *_STATUS.md  
- *_PROGRESS*.md
- *_VALIDATION*.md
- *_COMPLETE*.md
- *_FIXED.md
- *_FIX_*.md
- *_BUG*.md
- *_REGRESSION.md
- *_RESULTS.md
- *_NOTES.md
- *_REPORT.md (unless analysis)
- BUILD_*.md
- SESSION_*.md
- COMMIT_MESSAGE.txt
- debug_output.log
- *.log files

### → design/
- *_PLAN.md
- *_STRATEGY.md
- MIGRATION_*.md (plans)
- INTEGRATION_TEST_PLAN.md

## Execution

Move files in batches, preserving git history where needed.

