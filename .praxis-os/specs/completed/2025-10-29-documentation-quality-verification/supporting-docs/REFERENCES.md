# Document References

## Referenced Documents

### DESIGN.md
**Path:** `../ DESIGN.md`  
**Purpose:** High-level design document outlining the initiative's purpose, scope, phases, and success criteria. Defines the "shift left" prevention strategy with pre-commit hooks as primary defense.

### Advanced Configuration Documentation (Buggy File)
**Path:** `../../../../docs/tutorials/advanced-configuration.rst`  
**Purpose:** The documentation file that contained the critical bug - incorrectly showing `session_name` and `metadata` as `SessionConfig` fields. This file was corrected as part of the initiative's discovery.

### Tracer Configuration Models
**Path:** `../../../../src/honeyhive/config/models/tracer.py`  
**Purpose:** Source of truth for `TracerConfig` and `SessionConfig` Pydantic models. Used to verify correct field usage and identify documentation errors.

### RST Documentation Workflow Standard
**Path:** `../../../standards/documentation/rst-documentation-workflow.md`  
**Purpose:** Newly created standard for writing RST documentation, including proper title underlines, bullet list formatting, and pre-writing discovery workflow. Addresses the root cause of formatting errors.

### Standards README
**Path:** `../../../standards/README.md`  
**Purpose:** Main index for Agent OS standards, updated to include the RST Documentation Workflow as a mandatory starting point for RST writing tasks.

### Strands Integration Documentation
**Path:** `../../../../docs/how-to/integrations/strands.rst`  
**Purpose:** Recently created documentation that went through the full RST workflow, demonstrating the end-to-end documentation process including discovery, writing, validation, and deployment.

---

**Processing Mode:** Referenced (files remain in their original locations)  
**Document Count:** 6  
**Note:** All referenced files are in the same repository and remain accessible.

