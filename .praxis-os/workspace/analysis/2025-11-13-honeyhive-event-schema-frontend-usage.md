# HoneyHive Event Zod Schema & Frontend Usage Analysis

**Date:** 2025-11-13  
**Analysis Type:** Multi-Repo Code Intelligence (Frontend + Backend + Core)  
**Goal:** Understand the complete flow from Zod schema definition to frontend rendering

---

## 📋 Executive Summary

**Key Finding:** HoneyHive uses a **flexible Zod schema** in the `@hive-kube/core` package that validates core event structure while allowing instrumentor-specific data patterns. The frontend dynamically renders this flexible data across multiple views (table, sideview, graph, thread, timeline).

**Schema Location:**
- **Core Schema:** `hive-kube/packages/core/src/schemas/events/honeyhive_event.schema.ts`
- **Ingestion Helper:** `hive-kube/kubernetes/ingestion_service/app/utils/schema_helper.ts`
- **Legacy Schema:** `hive-kube/kubernetes/ingestion_service/app/schemas/event_schema.js`

**Frontend Usage:**
- **Table View:** `hive-kube/kubernetes/frontend_service/src/partials/events/EventsTableComponent.tsx`
- **Row Rendering:** `hive-kube/kubernetes/frontend_service/src/partials/events/EventsTableItem.jsx`
- **Side View:** `hive-kube/kubernetes/frontend_service/src/partials/events/EventsSideView.tsx`

---

## 🔍 Part 1: The Zod Schema Deep Dive

### Core Schema Structure (HoneyHiveEventSchema)

**File:** `hive-kube/packages/core/src/schemas/events/honeyhive_event.schema.ts`

```typescript
export const HoneyHiveEventSchema = z
  .object({
    // ========== Core Identification ==========
    event_id: z.string().uuid(),
    event_type: ActualEventType,  // 'model' | 'tool' | 'chain' | 'session'
    event_name: z.string().optional(),

    // ========== Flexible Data Fields ==========
    inputs: z.record(z.unknown()).optional(),
    outputs: z.union([z.record(z.unknown()), z.array(z.record(z.unknown()))]).optional(),
    config: z.record(z.unknown()).nullable().optional(),
    metadata: z.record(z.unknown()).nullable().optional(),
    metrics: z.record(z.unknown()).nullable().optional(),
    feedback: z.record(z.unknown()).nullable().optional(),
    user_properties: z.record(z.unknown()).optional(),

    // ========== Error Handling ==========
    error: z.string().nullable().optional(),

    // ========== Relationships ==========
    parent_id: z.string().uuid().nullable().optional(),
    session_id: z.string().uuid().optional(),
    project_id: z.string().optional(),
    tenant: z.string().optional(),
    source: z.string().optional(),
    children_ids: z.array(z.string().uuid()).optional(),

    // ========== Timestamps ==========
    start_time: z.number().optional(),
    end_time: z.number().optional(),
    duration: z.number().optional(),
  })
  .passthrough(); // ⚠️ CRITICAL: Allow additional fields for forward compatibility
```

### Design Philosophy

**From Schema Comments:**
> Purpose: Validates core event structure while accepting flexible data patterns.
> This schema supports ALL instrumentors (Traceloop, OpenInference, OpenLit, Vercel AI)
> and custom user implementations.

**Key Design Principles:**
1. **Validate Structure** - Enforce event_type, event_id, relationships
2. **Allow Flexible Data** - inputs, outputs, config, metadata accept any shape
3. **Document Optimal Patterns** - Guide without enforcing

**Historical Context (from comments):**
- **PR #520:** Created strict discriminated union (too strict, rejected valid data)
- **This Fix:** Moved to core package with flexible validation
- **Addresses:** sunnybak's feedback about integrating into core package

---

### Event Types

**Defined in:** `event.filter.schema.ts`

```typescript
const ActualEventType = z.enum(['model', 'tool', 'chain', 'session']);
```

**Frontend Visual Mapping:**

| Type         | Icon        | Color                         | Use Case                      |
|-------------|-------------|-------------------------------|-------------------------------|
| `model`     | ✨ Sparkles | Blue (bg-blue-100)            | LLM completions               |
| `tool`      | 🔧 Wrench   | Red (bg-red-100)              | Function/tool calls           |
| `chain`     | 🔗 Link     | Neutral (bg-neutral-300)      | Multi-step workflows          |
| `session`   | 🌐 Network  | Purple (bg-purple-100)        | Session containers            |

---

### Flexible Data Fields Deep Dive

#### 1. **Inputs** (`z.record(z.unknown())`)

**Optimal Patterns (Model Events):**
```typescript
// Documented but NOT enforced
inputs: {
  chat_history: Message[],     // Conversation history
  functions: Function[]         // Available functions for tool calling
}
```

**Optimal Patterns (Tool Events):**
```typescript
inputs: {
  query?: string,
  parameters?: Record<string, unknown>
}
```

**Flexibility:** Accepts ANY shape - attribute mapper determines structure at ingestion time.

#### 2. **Outputs** (`z.union([z.record(...), z.array(...)])`)

**Optimal Patterns (Model Events):**
```typescript
outputs: {
  role: string,                 // 'assistant' | 'user' | 'system' | 'tool'
  content: string | null,       // Message content
  finish_reason: string,        // 'stop' | 'length' | 'tool_calls'
  tool_calls?: ToolCall[]       // Function calls made by model
}
```

**Optimal Patterns (Tool Events):**
```typescript
outputs: {
  response?: string,
  results?: unknown
}
```

**Critical Feature:** Outputs can be EITHER an object OR an array of objects (supports streaming/multiple responses).

#### 3. **Config** (`z.record(z.unknown()).nullable()`)

**Common Fields:**
```typescript
config: {
  provider?: string,      // 'openai' | 'anthropic' | 'cohere' | etc.
  model?: string,         // 'gpt-4' | 'claude-3' | etc.
  temperature?: number,
  max_tokens?: number,
  // ... any other LLM config
}
```

#### 4. **Metadata** (`z.record(z.unknown()).nullable()`)

**Common Fields:**
```typescript
metadata: {
  prompt_tokens?: number,
  completion_tokens?: number,
  response_model?: string,
  // ... instrumentor-specific telemetry
}
```

#### 5. **Metrics** (`z.record(z.unknown()).nullable()`)

**Common Fields:**
```typescript
metrics: {
  latency?: number,
  cost?: number,
  // ... custom computed metrics
}
```

#### 6. **Feedback** (`z.record(z.unknown()).nullable()`)

**Common Fields:**
```typescript
feedback: {
  rating?: number,
  comments?: string,
  ground_truth?: any
}
```

---

### Type Guards & Helpers

**Optimal Pattern Detection:**

```typescript
// Check if model inputs follow optimal pattern
export function hasOptimalModelInputs(inputs: any): boolean {
  return inputs?.chat_history && Array.isArray(inputs.chat_history);
}

// Check if model outputs follow optimal pattern
export function hasOptimalModelOutputs(outputs: any): boolean {
  return (
    typeof outputs?.role === 'string' &&
    (typeof outputs?.content === 'string' || outputs?.content === null)
  );
}

// Check if event has tool calls (OpenAI format)
export function hasToolCalls(data: any): boolean {
  return data?.tool_calls && Array.isArray(data.tool_calls) && data.tool_calls.length > 0;
}

// Check if event has function call (legacy OpenAI format)
export function hasFunctionCall(data: any): boolean {
  return data?.function_call && typeof data.function_call === 'object';
}
```

**Validation with Details:**

```typescript
export function validateHoneyHiveEventWithDetails(data: unknown): {
  success: boolean;
  data?: HoneyHiveEvent;
  error?: string;
  details?: any;
} {
  const result = HoneyHiveEventSchema.safeParse(data);
  // ... returns detailed error information for debugging
}
```

---

### Legacy Schema (Backward Compatibility)

**File:** `hive-kube/kubernetes/ingestion_service/app/schemas/event_schema.js`

**Legacy `eventSchema` (JavaScript):**

```javascript
const eventSchema = z.object({
  project_id: z.string(),
  session_id: uuidType,
  event_id: uuidType,
  parent_id: uuidType.optional().nullable(),
  children_ids: z.array(uuidType),
  event_type: z.string(),
  event_name: z.string(),
  config: z.record(z.unknown()).nullable(),
  inputs: z.record(z.unknown()),
  outputs: singleObjectSchema.or(z.array(singleObjectSchema)),
  error: z.string().optional().nullable(),
  source: z.string(),
  duration: z.number(),
  user_properties: z.record(z.unknown()),
  metrics: z.record(z.unknown()).nullable(),
  feedback: z.record(z.unknown()).nullable(),
  metadata: z.record(z.unknown()),
  tenant: z.string(),
  start_time: z.number(),
  end_time: z.number(),
});
```

**Key Differences from HoneyHiveEventSchema:**
1. **More Required Fields:** `project_id`, `session_id`, `children_ids`, `event_type`, etc. are REQUIRED
2. **No `.passthrough()`:** Strict field validation
3. **Used in Ingestion Service:** Legacy validation for existing flows

---

## 🎨 Part 2: Frontend Usage Deep Dive

### Frontend Event Data Interface

**File:** `frontend_service/src/partials/events/EventsTableComponent.tsx`

```typescript
interface EventData {
  _id: string;
  event_id: string;
  session_id: string;
  start_time: string | number;
  end_time: string | number;
  event_type: string;
  event_name: string;
  error?: any;
  inputs?: any;          // ⚠️ ANY - accepts flexible shape
  outputs?: any;         // ⚠️ ANY - accepts flexible shape
  source?: string;
  duration?: number;
  metadata?: any;        // ⚠️ ANY - accepts flexible shape
  metrics?: any;         // ⚠️ ANY - accepts flexible shape
  feedback?: any;        // ⚠️ ANY - accepts flexible shape
  [key: string]: any;    // ⚠️ Index signature for dynamic properties
}
```

**Critical Insight:** Frontend uses `any` types for flexible fields, matching the Zod schema's `z.record(z.unknown())` philosophy.

---

### 1. Table View Rendering

**File:** `EventsTableComponent.tsx`

#### Column Structure

```typescript
interface Column {
  name: string;           // Display name
  selector: string;       // Dot-notation path (e.g., "metadata.prompt_tokens")
  sortable: boolean;
  width: string;
  isFilterColumn?: boolean;
}
```

#### Base Columns

```typescript
const baseColumns: Column[] = [
  { name: 'Type', selector: 'event_type', sortable: true, width: '80px' },
  { name: 'Event Name', selector: 'event_name', sortable: true, width: '200px' },
  { name: 'Status', selector: 'error', sortable: true, width: '100px' },
  { name: 'Inputs', selector: 'inputs', sortable: true, width: '400px' },
  { name: 'Outputs', selector: 'outputs', sortable: true, width: '400px' },
  { name: 'Timestamp', selector: 'start_time', sortable: true, width: '180px' },
  { name: 'Source', selector: 'source', sortable: true, width: '150px' },
  { name: 'Latency', selector: 'duration', sortable: true, width: '120px' },
];
```

#### Dynamic Column Generation

**Function:** `getImmediateSubColumnsOfObject()`

**Purpose:** Dynamically create columns for nested object properties (e.g., `metadata.prompt_tokens`).

**Algorithm:**
```typescript
const getImmediateSubColumnsOfObject = (
  objectList: EventData[],
  key: string,           // e.g., 'metadata'
  width: string,
): Column[] => {
  const uniqueSubKeys = new Set<string>();
  
  // Collect all unique subkeys across all events
  objectList.forEach((object) => {
    if (object[key]) {
      Object.keys(object[key]).forEach((subKey) => {
        uniqueSubKeys.add(subKey);
      });
    }
  });
  
  // Sort and map to column objects
  return Array.from(uniqueSubKeys)
    .sort((a, b) => a.localeCompare(b))
    .map((subKey) => ({
      name: `${key}.${subKey}`,         // e.g., "metadata.prompt_tokens"
      selector: `${key}.${subKey}`,     // Dot notation for value extraction
      sortable: true,
      width,
    }));
};
```

**Example:**
```javascript
// Given events with:
// event1.metadata = { prompt_tokens: 10, model: 'gpt-4' }
// event2.metadata = { prompt_tokens: 20, completion_tokens: 5 }

// Generates columns:
[
  { name: 'metadata.completion_tokens', selector: 'metadata.completion_tokens', ... },
  { name: 'metadata.model', selector: 'metadata.model', ... },
  { name: 'metadata.prompt_tokens', selector: 'metadata.prompt_tokens', ... }
]
```

**Critical Feature:** Handles the schema's flexible `z.record(z.unknown())` fields by discovering columns at runtime!

---

### 2. Row Rendering (Table Item)

**File:** `EventsTableItem.jsx`

#### Value Extraction (Dot Notation)

```javascript
function getValueFromObject(obj, key) {
  return key.split('.').reduce((o, i) => (o && o[i] !== undefined ? o[i] : null), obj);
}
```

**Example:**
```javascript
// key = "metadata.prompt_tokens"
// obj = { metadata: { prompt_tokens: 100 } }
// result = 100

// key = "metadata.missing_field"
// obj = { metadata: { prompt_tokens: 100 } }
// result = null
```

#### Special Rendering Logic

**1. Event Type Rendering:**

```javascript
function displayType(type) {
  const typeColors = {
    model: 'bg-blue-100 text-blue-700',
    tool: 'bg-red-100 text-red-700',
    chain: 'bg-neutral-300 text-black',
    session: 'bg-purple-100 text-purple-700',
  };

  const icons = {
    model: Sparkles,      // Lucide icon
    tool: Wrench,
    chain: Link,
    session: Network,
  };

  // Render colored badge with icon
  return (
    <div className={`p-2 inline-flex items-center justify-center rounded ${colorClass}`}>
      <Icon size={16} color={iconColor} />
    </div>
  );
}
```

**2. Status Rendering:**

```javascript
function displayStatus(error) {
  if (!error) {
    return <div className="bg-emerald-100 text-emerald-700">Success</div>;
  } else {
    return <div className="bg-red-100 text-red-700">Error</div>;
  }
}
```

**3. Inputs/Outputs Rendering:**

```javascript
// Truncate to 150 characters and stringify
if (column.selector.includes('outputs') || column.selector.includes('inputs')) {
  value = displayOutput(JSON.stringify(value));
}

function displayOutput(output) {
  if (output.length > 150) {
    return output.substring(0, 150) + '...';
  }
  return output;
}
```

**Critical Insight:** Inputs and outputs are **stringified** for table display (limited detail), full detail shown in side view.

---

### 3. Side View (Detailed Event View)

**File:** `EventsSideView.tsx`

#### Side View Components

**1. Event Header:**
- Event ID (copyable)
- Event type icon + name
- Timestamp
- Navigation (prev/next event)
- Actions (share, export, add to dataset/queue)

**2. Collapsible Sections:**

```typescript
const SideviewDropdownWrapper = ({ label, children, defaultOpen, icon }) => {
  // Collapsible section with icon + label
  // Used for: Inputs, Outputs, Config, Metadata, Metrics, Feedback, etc.
};
```

**3. Specialized Components:**

- **`<SideviewInput>`** - Renders `event.inputs` (flexible shape)
- **`<SideviewOutput>`** - Renders `event.outputs` (flexible shape)
- **`<SideviewDropdown>`** - Generic collapsible section for config/metadata
- **`<SideviewDropdownMetrics>`** - Renders `event.metrics` with special handling
- **`<FeedbackInputPanel>`** - Renders `event.feedback` (editable)
- **`<SideviewEventJSON>`** - Raw JSON view of entire event

**4. Session Views (if session event):**
- **Tree View** - Hierarchical tree of events
- **Timeline View** - Temporal sequence
- **Graph View** - Visual DAG of event relationships
- **Thread View** - Chat-style conversation view
- **Summary View** - Aggregated metrics/info

#### Example Side View Structure

```typescript
<EventsSideView event={currentEvent}>
  {/* Header */}
  <EventHeader eventId={event.event_id} eventType={event.event_type} />
  
  {/* Collapsible Sections */}
  <SideviewDropdownWrapper label="Inputs" icon={<Braces />}>
    <SideviewInput inputs={event.inputs} />  {/* Handles ANY shape */}
  </SideviewDropdownWrapper>
  
  <SideviewDropdownWrapper label="Outputs" icon={<MessageSquare />}>
    <SideviewOutput outputs={event.outputs} />  {/* Handles ANY shape */}
  </SideviewDropdownWrapper>
  
  <SideviewDropdownWrapper label="Config" icon={<Layers />}>
    <SideviewDropdown data={event.config} />  {/* Handles ANY shape */}
  </SideviewDropdownWrapper>
  
  <SideviewDropdownWrapper label="Metadata" icon={<Braces />}>
    <SideviewDropdown data={event.metadata} />  {/* Handles ANY shape */}
  </SideviewDropdownWrapper>
  
  <SideviewDropdownWrapper label="Metrics" icon={<Clock />}>
    <SideviewDropdownMetrics metrics={event.metrics} />  {/* Handles ANY shape */}
  </SideviewDropdownWrapper>
  
  <SideviewDropdownWrapper label="Feedback" icon={<Users />}>
    <FeedbackInputPanel feedback={event.feedback} />  {/* Editable */}
  </SideviewDropdownWrapper>
  
  {/* Raw JSON View */}
  <SideviewEventJSON event={event} />
</EventsSideView>
```

---

### How Frontend Handles Flexible Data

**Problem:** Zod schema allows `z.record(z.unknown())` - any shape.

**Solution:** Dynamic rendering strategies:

#### 1. **Dynamic Column Discovery** (Table)
- Scan all events in current page
- Extract unique keys from flexible fields (`metadata`, `metrics`, `user_properties`)
- Generate columns dynamically
- Re-discover columns when data changes

#### 2. **Recursive Object Rendering** (Side View)
- `<SideviewDropdown>` recursively renders arbitrary nested objects
- Handles primitives, objects, arrays, null values
- JSON stringify as fallback for unknown types

#### 3. **Type-Specific Components** (Specialized)
- `<SideviewInput>` - Knows about optimal patterns (chat_history, functions)
- `<SideviewOutput>` - Handles role/content/tool_calls patterns
- Falls back to generic rendering if patterns not detected

#### 4. **Raw JSON Fallback**
- Always provide `<SideviewEventJSON>` for full data access
- Users can inspect any field regardless of frontend rendering

---

## 🔄 Part 3: Data Flow (Schema → Frontend)

### Complete Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│ 1. SDK/Instrumentor sends event                                      │
│    - OpenTelemetry span (from Traceloop, OpenInference, etc.)       │
│    - HoneyHive SDK direct event                                      │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 2. Ingestion Service receives event                                  │
│    File: ingestion_service/app/utils/schema_helper.ts               │
│    - validateHoneyHiveEvent(data) → HoneyHiveEventSchema.parse()   │
│    - Flexible validation: accepts any inputs/outputs shape          │
│    - Attribute mapper processes instrumentor-specific patterns      │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 3. Backend Service stores event                                      │
│    - MongoDB document                                                 │
│    - Preserves ALL flexible fields as-is                            │
│    - No data loss from unknown fields (.passthrough() in schema)    │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 4. Frontend fetches events                                           │
│    File: frontend_service/src/api/requests/index.ts                 │
│    - GET /events?project_id=...&filters=...                         │
│    - Returns array of EventData (flexible fields as `any`)          │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 5. Frontend Table View renders                                       │
│    File: EventsTableComponent.tsx                                    │
│    - Scans ALL events to discover dynamic columns                   │
│    - Generates columns for metadata.*, metrics.*, etc.              │
│    - Renders truncated inputs/outputs (150 chars)                   │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 6. User clicks event → Side View opens                              │
│    File: EventsSideView.tsx                                          │
│    - Renders full inputs (SideviewInput - flexible shape)           │
│    - Renders full outputs (SideviewOutput - flexible shape)         │
│    - Renders config, metadata, metrics, feedback (SideviewDropdown) │
│    - Provides raw JSON view (SideviewEventJSON)                     │
│    - Special views for sessions (Tree, Timeline, Graph, Thread)     │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Part 4: Critical Insights

### 1. Schema Flexibility = Frontend Complexity

**Tradeoff:**
- **Pros:** Supports ALL instrumentors (Traceloop, OpenInference, custom)
- **Cons:** Frontend must handle ANY shape dynamically

**Frontend Strategy:**
- Dynamic column discovery (table)
- Recursive rendering (side view)
- Type-specific components for optimal patterns
- JSON fallback for unknown data

### 2. Optimal Patterns vs. Validation

**Schema Approach:**
- **Validate:** Core structure (event_id, event_type, relationships)
- **Document:** Optimal patterns for inputs/outputs (chat_history, role/content)
- **Don't Enforce:** Flexible fields can have any shape

**Frontend Approach:**
- **Detect:** Use type guards (`hasOptimalModelInputs`, `hasOptimalModelOutputs`)
- **Render:** Use specialized components when patterns detected
- **Fallback:** Generic rendering when patterns not detected

### 3. Forward Compatibility via `.passthrough()`

**Critical Feature:**

```typescript
export const HoneyHiveEventSchema = z.object({ ... }).passthrough();
```

**Why:**
- New instrumentors can add new fields without breaking validation
- New attributes (e.g., `gen_ai.agent.name` in Pydantic AI v3) pass through
- Frontend discovers new fields dynamically (column generation)

**Without `.passthrough()`:**
- Validation would REJECT events with unknown fields
- Would require schema updates for every new instrumentor
- PR #520 issue: strict schema rejected valid data

### 4. Legacy Schema vs. HoneyHiveEventSchema

**When Legacy Schema is Used:**
- `validateEventSchema()` - ingestion_service internal validation
- Stricter validation (more required fields)
- Does NOT have `.passthrough()`

**When HoneyHiveEventSchema is Used:**
- `validateHoneyHiveEvent()` - primary validation
- Flexible validation (fewer required fields)
- HAS `.passthrough()` for forward compatibility

**Migration Status:** Transitioning from legacy to HoneyHive schema (per PR #520 follow-up).

### 5. Data Preservation Guarantee

**Critical Contract:**
- **Ingestion:** Schema validates structure, preserves ALL data (even unknown fields)
- **Backend:** Stores ALL fields as-is (MongoDB document)
- **Frontend:** Renders ALL fields dynamically (column discovery + JSON view)

**Result:** No data loss through the entire pipeline, even for unknown/future fields.

---

## 📊 Part 5: Field Usage Matrix

### Which Fields Does Frontend Actually Use?

| Field             | Table View | Side View Header | Side View Detail | Tree View | Graph View | Timeline View | Thread View |
|-------------------|------------|------------------|------------------|-----------|------------|---------------|-------------|
| `event_id`        | ✅         | ✅               | ✅               | ✅        | ✅         | ✅            | ✅          |
| `event_type`      | ✅         | ✅               | ✅               | ✅        | ✅         | ✅            | ❌          |
| `event_name`      | ✅         | ✅               | ✅               | ✅        | ✅         | ✅            | ✅          |
| `start_time`      | ✅         | ✅               | ✅               | ❌        | ❌         | ✅            | ✅          |
| `end_time`        | ✅         | ✅               | ✅               | ❌        | ❌         | ✅            | ✅          |
| `duration`        | ✅         | ✅               | ✅               | ✅        | ✅         | ✅            | ❌          |
| `error`           | ✅         | ✅               | ✅               | ✅        | ✅         | ❌            | ✅          |
| `inputs`          | ✅ (trunc) | ❌               | ✅ (full)        | ❌        | ❌         | ❌            | ✅ (if msg) |
| `outputs`         | ✅ (trunc) | ❌               | ✅ (full)        | ❌        | ❌         | ❌            | ✅ (if msg) |
| `config`          | ❌         | ❌               | ✅               | ❌        | ❌         | ❌            | ❌          |
| `metadata`        | ✅ (cols)  | ❌               | ✅               | ❌        | ❌         | ❌            | ❌          |
| `metrics`         | ✅ (cols)  | ❌               | ✅               | ❌        | ❌         | ❌            | ❌          |
| `feedback`        | ❌         | ❌               | ✅ (editable)    | ❌        | ❌         | ❌            | ❌          |
| `user_properties` | ✅ (cols)  | ❌               | ✅               | ❌        | ❌         | ❌            | ❌          |
| `session_id`      | ❌         | ✅               | ✅               | ✅        | ✅         | ✅            | ✅          |
| `parent_id`       | ❌         | ❌               | ✅               | ✅        | ✅         | ✅            | ✅          |
| `children_ids`    | ❌         | ❌               | ❌               | ✅        | ✅         | ✅            | ✅          |

**Legend:**
- ✅ = Used/rendered
- ❌ = Not used/rendered
- ✅ (trunc) = Used but truncated (150 chars)
- ✅ (full) = Full rendering with detail
- ✅ (cols) = Dynamic column generation from nested keys

---

## 🚀 Part 6: Implications for SDK Development

### 1. What SDK Must Provide

**Required Fields (Hard Validation):**
```python
event = {
    "event_id": str(uuid.uuid4()),              # REQUIRED - UUID
    "event_type": "model" | "tool" | "chain",   # REQUIRED - Must be valid enum
}
```

**Strongly Recommended (Frontend Depends On):**
```python
event = {
    "event_name": "openai_chat_completion",     # Table + Side View display
    "start_time": 1699564800000,                # Timestamp display + Timeline
    "end_time": 1699564805000,                  # Timestamp display + Timeline
    "duration": 5000,                           # Latency display
    "error": "Error message" | None,            # Status badge rendering
    "session_id": str(uuid.uuid4()),            # Session grouping
    "parent_id": str(uuid.uuid4()) | None,      # Tree/Graph relationships
}
```

**Flexible Fields (Any Shape Accepted):**
```python
event = {
    "inputs": { ... },       # ANY shape - SDK decides structure
    "outputs": { ... },      # ANY shape - SDK decides structure
    "config": { ... },       # ANY shape - model/tool config
    "metadata": { ... },     # ANY shape - telemetry data
    "metrics": { ... },      # ANY shape - computed metrics
    "feedback": { ... },     # ANY shape - user feedback
}
```

### 2. Optimal Patterns for Best UX

**Model Events (LLM Completions):**

```python
# SDK should produce this shape for optimal frontend rendering
event = {
    "event_type": "model",
    "event_name": "openai_chat_completion",
    "inputs": {
        "chat_history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ],
        "functions": [  # If tool calling
            {
                "name": "get_weather",
                "description": "Get current weather",
                "parameters": { ... }
            }
        ]
    },
    "outputs": {
        "role": "assistant",
        "content": "The weather is sunny!",
        "finish_reason": "stop",  # or "tool_calls"
        "tool_calls": [  # If model called tools
            {
                "id": "call_abc123",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "NYC"}'
                }
            }
        ]
    },
    "config": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 150
    },
    "metadata": {
        "prompt_tokens": 50,
        "completion_tokens": 20,
        "total_tokens": 70
    },
    "metrics": {
        "cost_usd": 0.0042,
        "latency_ms": 1250
    }
}
```

**Tool Events (Function Calls):**

```python
event = {
    "event_type": "tool",
    "event_name": "get_weather",
    "inputs": {
        "query": "Get weather for NYC",
        "parameters": {
            "location": "NYC",
            "units": "celsius"
        }
    },
    "outputs": {
        "response": "Currently 22°C and sunny",
        "results": {
            "temperature": 22,
            "condition": "sunny"
        }
    },
    "config": {
        "tool_name": "get_weather",
        "timeout_ms": 5000
    },
    "metadata": {
        "api_endpoint": "https://api.weather.com/v1"
    }
}
```

### 3. What Breaks Frontend vs. What Doesn't

**❌ BREAKS Frontend:**
```python
# Missing event_id (hard validation failure)
event = { "event_type": "model" }  # ERROR: Missing event_id

# Invalid event_type (hard validation failure)
event = { "event_id": "...", "event_type": "invalid" }  # ERROR: Not in enum

# Invalid UUID format (validation failure)
event = { "event_id": "not-a-uuid", "event_type": "model" }  # ERROR: Invalid UUID
```

**✅ WORKS (Degrades Gracefully):**
```python
# Missing event_name (side view shows event_id instead)
event = { "event_id": "...", "event_type": "model" }

# Missing timestamps (timeline view unavailable, but table/side view work)
event = { "event_id": "...", "event_type": "model" }

# Unusual inputs shape (renders as JSON, dynamic columns generated)
event = {
    "event_id": "...",
    "event_type": "model",
    "inputs": {
        "my_custom_field": "value",
        "another_custom_field": 42
    }
}

# Unknown top-level fields (preserved by .passthrough(), shown in JSON view)
event = {
    "event_id": "...",
    "event_type": "model",
    "my_new_instrumentor_field": "value"  # ✅ Preserved and shown
}
```

### 4. Dynamic Column Discovery Considerations

**Frontend scans ALL events in current page to discover columns.**

**Implications:**
- **Consistent Naming:** Use same key names across events (`metadata.prompt_tokens`, not sometimes `metadata.tokens_prompt`)
- **Avoid Explosion:** Too many unique keys = too many columns = poor UX
- **Nested Structure:** Frontend only discovers immediate children (e.g., `metadata.prompt_tokens`, not `metadata.usage.prompt_tokens`)

**Example Problem:**

```python
# BAD: Inconsistent naming
event1 = { "metadata": { "prompt_tokens": 50 } }
event2 = { "metadata": { "tokens_prompt": 50 } }  # Creates 2 columns!

# GOOD: Consistent naming
event1 = { "metadata": { "prompt_tokens": 50 } }
event2 = { "metadata": { "prompt_tokens": 60 } }  # Shares 1 column
```

**Recommendation:** SDK should normalize attribute names to match established patterns (e.g., GenAI Semantic Conventions).

---

## 📝 Part 7: Summary & Recommendations

### Key Takeaways

1. **Schema is Flexible by Design**
   - Core structure validated (event_id, event_type, relationships)
   - Data fields flexible (inputs, outputs, config, metadata, metrics, feedback)
   - `.passthrough()` preserves unknown fields for forward compatibility

2. **Frontend Handles Flexibility Dynamically**
   - Table: Dynamic column discovery from flexible fields
   - Side View: Recursive rendering + type-specific components
   - JSON View: Fallback for all data

3. **Optimal Patterns Improve UX**
   - Model events: `inputs.chat_history`, `outputs.role/content/tool_calls`
   - Tool events: `inputs.query/parameters`, `outputs.response/results`
   - Config: `provider`, `model`, `temperature`, etc.
   - Metadata: Token counts, response model, etc.

4. **Data Preservation Guarantee**
   - Ingestion validates structure, preserves all data
   - Backend stores all fields as-is
   - Frontend renders all fields (columns + side view + JSON)

### Recommendations for Python SDK

1. **Produce Optimal Patterns When Possible**
   - Use `inputs.chat_history` for model inputs (Message[])
   - Use `outputs.role/content` for model outputs
   - Use `config.provider/model/temperature` for LLM config
   - Use `metadata.prompt_tokens/completion_tokens` for telemetry

2. **Be Consistent**
   - Use same key names across events
   - Follow GenAI Semantic Conventions when applicable
   - Avoid key name variations (e.g., `prompt_tokens` vs. `tokens_prompt`)

3. **Provide Rich Metadata**
   - Token counts (prompt_tokens, completion_tokens)
   - Cost (cost_usd)
   - Latency (duration or metrics.latency_ms)
   - Model info (provider, model, response_model)

4. **Use Proper Data Types**
   - Timestamps: Numbers (milliseconds since epoch)
   - UUIDs: Valid UUID strings
   - Durations: Numbers (milliseconds)
   - Event type: Valid enum ('model', 'tool', 'chain', 'session')

5. **Don't Over-Nest**
   - Frontend discovers immediate children only
   - `metadata.prompt_tokens` ✅
   - `metadata.usage.prompt_tokens` ❌ (won't create column)

6. **Test Against Schema**
   - Use `HoneyHiveEventSchema.safeParse()` in SDK tests
   - Validate that events pass schema validation
   - Verify optimal patterns are detected by type guards

---

## 🔗 References

### Source Files Analyzed

**Core Schema:**
- `hive-kube/packages/core/src/schemas/events/honeyhive_event.schema.ts`
- `hive-kube/packages/core/src/schemas/events/index.ts`
- `hive-kube/packages/core/src/schemas/events/event.filter.schema.ts`

**Ingestion:**
- `hive-kube/kubernetes/ingestion_service/app/utils/schema_helper.ts`
- `hive-kube/kubernetes/ingestion_service/app/schemas/event_schema.js`

**Frontend:**
- `hive-kube/kubernetes/frontend_service/src/partials/events/EventsTableComponent.tsx`
- `hive-kube/kubernetes/frontend_service/src/partials/events/EventsTableItem.jsx`
- `hive-kube/kubernetes/frontend_service/src/partials/events/EventsSideView.tsx`
- `hive-kube/kubernetes/frontend_service/src/utils/sideview/SideviewInput.tsx`
- `hive-kube/kubernetes/frontend_service/src/utils/sideview/SideviewOutput.tsx`
- `hive-kube/kubernetes/frontend_service/src/utils/sideview/SideviewDropdown.tsx`

### Related PRs

- **PR #520:** Created strict discriminated union (too strict, caused issues)
- **Follow-up:** Moved to core package with flexible validation + `.passthrough()`

---

**Analysis Complete!** 🎉

