┌─────────────────────────────────────────────────────────────────┐
│                    EATELLECT AGENTIC WORKFLOW                   │
└─────────────────────────────────────────────────────────────────┘

                         ┌──────────┐
                         │  START   │
                         └────┬─────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │ 1. BARCODE          │
                    │    EXTRACTOR        │
                    │                     │
                    │ • Scan image        │
                    │ • Extract barcode   │
                    │ • Fetch from API    │
                    └──────────┬──────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │ 2. CLASSIFIER       │
                    │                     │
                    │ • Check data        │
                    │ • Determine type    │
                    └──────────┬──────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
              Has Data?            No Data?
                    │                   │
                    ▼                   ▼
        ┌─────────────────────┐    ┌────────┐
        │ 3. DATA EXTRACTION  │    │  END   │
        │                     │    └────────┘
        │ • Extract nutrition │
        │ • Calculate score   │
        │ • Find allergens    │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ 4. LLM ANALYSIS     │
        │                     │
        │ • Generate insights │
        │ • Health assessment │
        │ • Benefits/concerns │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ 5. RECOMMENDATIONS  │
        │                     │
        │ • Generate tips     │
        │ • Consumption guide │
        │ • Alternatives      │
        └──────────┬──────────┘
                   │
                   ▼
               ┌────────┐
               │  END   │
               └────────┘
