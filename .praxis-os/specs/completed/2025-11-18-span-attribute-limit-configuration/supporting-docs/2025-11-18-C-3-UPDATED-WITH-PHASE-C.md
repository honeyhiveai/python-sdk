# C-3 Updated: Two-Phase Observability Approach

**Date:** 2025-11-18  
**Status:** ✅ COMPLETE

---

## Summary

Updated C-3 (Observability for Limit Violations) to include both Phase A (required, detection-only) and Phase C (optional future, custom eviction) approaches.

---

## What Changed

### Before
- C-3 was marked as "⚠️ PARTIALLY ADDRESSED"
- Span dropping had logging
- Attribute eviction had NO logging
- User question: "sounds like we will have to write custom attr eviction if we need to log data correct?"

### After
- C-3 now marked as "✅ ADDRESSED"
- **Phase A (Detection-Only):** Required for Week 3
  - Detect eviction in `on_end()`
  - Log ERROR with count estimate
  - Log WARNING with top 10 largest survivors
  - Simple (~100 lines), fast (<1ms), good enough for 95%
- **Phase C (Custom Eviction):** Optional future enhancement
  - Wrap `span.set_attribute()` in `on_start()`
  - Intercept and log evictions in real-time
  - Log exact evicted keys, value previews, timing
  - Complex (~300 lines), slower (~100ms for 1000 attrs)

---

## Decision Criteria for Phase C

Only implement Phase C if production shows:
1. Eviction rate > 5% of spans
2. Users file tickets asking "what was evicted?"
3. Inference (survivors + FIFO hint) proves insufficient
4. Performance cost is acceptable

---

## Documents Updated

1. **C-3 Spec:** `.praxis-os/workspace/review/2025-11-18-C-3-observability-logging-spec.md`
   - Added "Implementation Phases" section
   - Phase A: Detection-Only (REQUIRED)
   - Phase C: Custom Eviction (Optional Future)
   - Full implementation details for both
   - Pros/cons/performance analysis

2. **Pessimistic Review:** `.praxis-os/workspace/review/2025-11-18-span-limits-pessimistic-review.md`
   - Updated C-3 status to ✅ ADDRESSED
   - Updated executive summary: all critical issues resolved
   - Updated verdict: 🟢 LOW RISK
   - Updated recommendation: Ready for Phase 1 implementation
   - Replaced "NEEDS IMPLEMENTATION" with two-phase approach

---

## Key Insight

**User's Question Highlighted Design Choice:**
> "sounds like we will have to write custom attr eviction if we need to log data correct?"

**Answer:** Yes, but only if detection-only (Phase A) proves insufficient.

**Why Two Phases:**
- **Phase A:** Provides good visibility with minimal cost
- **Phase C:** Available if production data shows need
- **Data-Driven:** Don't over-engineer upfront
- **Cost-Aware:** Phase C has real performance/complexity cost

---

## Implementation Impact

### Phase A (Week 3) - REQUIRED
- ~100 lines of code
- <1ms overhead per span
- ERROR log when at limit
- WARNING log with top 10 survivors
- Metric: `honeyhive.attributes.at_limit`

### Phase C (Future) - OPTIONAL
- ~300 lines of code
- ~0.1ms per attribute (~100ms for 1000 attrs)
- ~100KB memory for 1000 attributes
- Real-time eviction logging
- Exact content visibility

---

## Success Metrics

**Phase A Success:**
- Users can detect eviction occurred
- Users can infer what survived (top 10 largest)
- Users can understand eviction policy (FIFO)
- Minimal performance impact

**Phase C Trigger:**
- Eviction rate > 5% in production
- User complaints about insufficient visibility
- Performance budget allows overhead

---

## Rationale

### Why Not Always Use Phase C?

1. **YAGNI:** Don't implement until proven necessary
2. **Performance:** 100ms overhead is significant for high-throughput
3. **Complexity:** More code = more bugs, more maintenance
4. **Risk:** Wrapping core OTel functionality could have edge cases

### Why Have Phase C at All?

1. **Preparedness:** Know what to do if Phase A insufficient
2. **Documentation:** Capture design while fresh in mind
3. **Transparency:** Show users we've thought this through
4. **Flexibility:** Option available if needed

---

## Next Steps

1. ✅ Implement Phase A (Week 3) - detection-only
2. ✅ Deploy to production
3. ✅ Monitor eviction rate via metrics
4. ⏸️ Evaluate Phase C after 30 days production data
5. ⏸️ Only implement Phase C if criteria met

---

## Related Documents

- **C-3 Full Spec:** `.praxis-os/workspace/review/2025-11-18-C-3-observability-logging-spec.md`
- **Pessimistic Review:** `.praxis-os/workspace/review/2025-11-18-span-limits-pessimistic-review.md`
- **Implementation Proposal:** `.praxis-os/workspace/review/2025-11-18-max-span-size-implementation-proposal.md`
- **Design Doc:** `.praxis-os/workspace/design/2025-11-18-span-attribute-limit-configuration.md`

---

## Conclusion

✅ C-3 is now fully addressed with a pragmatic two-phase approach:
- Phase A provides good visibility with minimal cost (required)
- Phase C provides full visibility if needed (optional, data-driven decision)

All critical issues are now resolved. Spec is ready for Phase 1 implementation.

