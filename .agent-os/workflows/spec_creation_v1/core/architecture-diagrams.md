# Architecture Diagram Templates

ASCII diagram templates for documenting system architecture in specs.md.

---

## Layered Architecture

```
┌──────────────────────────────────┐
│     Presentation Layer           │
│   (UI Components, Controllers)   │
└────────────┬─────────────────────┘
             │
┌────────────▼─────────────────────┐
│     Application Layer            │
│  (Business Logic, Use Cases)     │
└────────────┬─────────────────────┘
             │
┌────────────▼─────────────────────┐
│     Domain Layer                 │
│   (Domain Models, Rules)         │
└────────────┬─────────────────────┘
             │
┌────────────▼─────────────────────┐
│     Infrastructure Layer         │
│  (Database, External Services)   │
└──────────────────────────────────┘
```

---

## Microservices Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                         │
│   (Web Frontend / API Clients / Mobile Apps)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │      API Gateway / Router      │
         │    (Authentication, Routing)   │
         └───────────┬───────────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
     ▼               ▼               ▼
┌─────────┐    ┌──────────┐    ┌──────────┐
│Service A│    │Service B │    │Service C │
│{Purpose}│    │{Purpose} │    │{Purpose} │
└────┬────┘    └────┬─────┘    └────┬─────┘
     │              │               │
     └──────────────┼───────────────┘
                    │
                    ▼
         ┌───────────────────────┐
         │    Data Layer          │
         │  (Database, Cache)     │
         └───────────────────────┘
```

---

## Client-Server Architecture

```
┌────────────────┐
│     Client     │
│   (Browser)    │
└───────┬────────┘
        │ HTTP/HTTPS
        ▼
┌───────────────────┐
│   Load Balancer   │
└───────┬───────────┘
        │
   ┌────┴────┐
   │         │
   ▼         ▼
┌──────┐  ┌──────┐
│Server│  │Server│
│  1   │  │  2   │
└───┬──┘  └───┬──┘
    │         │
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │Database │
    └─────────┘
```

---

## Data Flow Diagram

```
User Request
     │
     ▼
[Authentication] → [Validation] → [Business Logic]
                                        │
                                        ▼
                                  [Data Access]
                                        │
                                        ▼
                                   [Database]
                                        │
                                        ▼
                                   [Response]
                                        │
                                        ▼
                                      User
```

---

## Event-Driven Architecture

```
┌─────────┐
│Producer │
│Service A│
└────┬────┘
     │ publish
     ▼
┌────────────┐
│Event Queue │
│  (Kafka)   │
└────┬───┬───┘
     │   │ subscribe
     │   └─────────────┐
     ▼                 ▼
┌──────────┐    ┌──────────┐
│Consumer  │    │Consumer  │
│Service B │    │Service C │
└──────────┘    └──────────┘
```

---

## Deployment Architecture

```
┌─────────────────────────────────────┐
│         Load Balancer               │
│      (SSL Termination)              │
└──────────┬──────────┬───────────────┘
           │          │
  ┌────────▼──┐  ┌───▼────────┐
  │ App       │  │ App        │
  │ Instance  │  │ Instance   │
  │    1      │  │    2       │
  └─────┬─────┘  └─────┬──────┘
        │              │
        └──────┬───────┘
               │
      ┌────────▼────────┐
      │   Database      │
      │  (Primary +     │
      │   Replicas)     │
      └─────────────────┘
```

---

## Component Interaction Diagram

```
Component A  →  [Method Call]  →  Component B
                    │
                    ▼
               [Validation]
                    │
                    ▼
Component B  →  [Data Query]  →  Data Layer
                    │
                    ▼
               [Response]
                    │
                    ▼
Component B  →  [Return]  →  Component A
```

---

## Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────┐
│    User     │1      N│   Resource   │
│             ├────────>│              │
│ - id        │  owns  │ - id         │
│ - email     │        │ - name       │
└─────────────┘        │ - owner_id   │
                       └──────┬───────┘
                              │
                              │1
                              │
                              │N
                       ┌──────▼────────┐
                       │ ResourceTag   │
                       │               │
                       │ - resource_id │
                       │ - tag         │
                       └───────────────┘
```

---

## Hexagonal (Ports & Adapters) Architecture

```
        ┌─────────────────────────┐
        │   External Interfaces   │
        │  (UI, API, CLI, Tests)  │
        └───────────┬─────────────┘
                    │ Ports
        ┌───────────▼─────────────┐
        │    Application Core     │
        │   (Business Logic)      │
        └───────────┬─────────────┘
                    │ Ports
        ┌───────────▼─────────────┐
        │       Adapters          │
        │ (DB, Queue, External)   │
        └─────────────────────────┘
```

---

## Usage Guidelines

1. **Choose appropriate diagram** for your architecture pattern
2. **Customize labels** to match your components
3. **Add description** explaining key components
4. **Document data flow** using arrows
5. **Keep diagrams simple** - one concept per diagram
