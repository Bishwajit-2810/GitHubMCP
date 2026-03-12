#!/usr/bin/env python3
"""Write exact, correct mermaid diagram definitions into each HTML file.

This replaces the unreliable algorithmic reconstruction with hardcoded
correct diagram syntax for every diagram across all docs_html pages.
"""

import re
from pathlib import Path

DOCS_DIR = Path("/home/bk/code/Project/GitHubMCP/docs_html")

# ── Diagram definitions ──────────────────────────────────────────────────────
# Each value is a dict mapping merChart_N → exact mermaid source.

DIAGRAMS: dict[str, dict[str, str]] = {
    "index.html": {
        "merChart_0": """\
graph TB
  User(["👤 User / Application"])
  subgraph Agents["🤖 Agent Layer (LangGraph)"]
    AG1["Research Agent"]
    AG2["Tool Agent"]
    AG3["Multi-Agent Orchestrator"]
  end
  subgraph Tools["🔌 Tool & Protocol Layer (MCP / FastMCP)"]
    MCP["MCP Server\\n(stdio / HTTP)"]
    FMCP["FastMCP Server\\n(Pythonic API)"]
    TOOL1["Weather Tool"]
    TOOL2["Search Tool"]
    TOOL3["GitHub Tool"]
  end
  subgraph RAG["📚 Knowledge Layer (RAG)"]
    EMB["Embeddings\\n(HuggingFace)"]
    CHROMA["ChromaDB\\n(Local Vector Store)"]
    PG["PGVector\\n(PostgreSQL)"]
  end
  subgraph LLM["⚡ LLM Layer (LangChain + Groq)"]
    LC["LangChain LCEL\\nChains & Prompts"]
    GROQ["Groq API\\nopenai/gpt-oss-120b"]
  end
  User --> AG3
  AG3 --> AG1 & AG2
  AG1 & AG2 --> LC
  AG1 & AG2 --> MCP & FMCP
  MCP --> TOOL1 & TOOL2
  FMCP --> TOOL3
  LC --> GROQ
  AG1 --> RAG
  RAG --> EMB
  EMB --> CHROMA & PG
  style User fill:#58a6ff,color:#000
  style Agents fill:#1c2128,stroke:#bc8cff
  style Tools fill:#1c2128,stroke:#3fb950
  style RAG fill:#1c2128,stroke:#e3b341
  style LLM fill:#1c2128,stroke:#58a6ff""",
    },
    "mcp.html": {
        "merChart_0": """\
flowchart LR
  subgraph Client["🖥️ MCP Client (your app)"]
    LLM["Groq LLM"]
    CS["ClientSession"]
  end
  subgraph Server["🔧 MCP Server"]
    T1["get_alerts()"]
    T2["get_forecast()"]
  end
  Client <-->|"JSON-RPC over stdio/HTTP"| Server
  LLM -->|"1. list_tools()"| CS
  CS -->|"2. calls on wire"| Server
  Server -->|"3. tool result"| CS
  CS -->|"4. result to LLM"| LLM
  style Client fill:#1c2128,stroke:#58a6ff
  style Server fill:#1c2128,stroke:#3fb950""",
        "merChart_1": """\
sequenceDiagram
  participant C as MCP Client
  participant S as MCP Server
  C->>S: initialize (capabilities)
  S-->>C: initialize result (server capabilities)
  C->>S: initialized (notification)
  Note over C,S: Connection established
  C->>S: tools/list
  S-->>C: list of available tools
  C->>S: tools/call name=get_forecast
  S-->>C: tool result content
  C->>S: close / disconnect""",
    },
    "langgraph.html": {
        "merChart_0": """\
flowchart TB
  User["👤 User Input"] --> Agent
  subgraph Agent["🤖 LangGraph Agent"]
    direction TB
    LLM["LLM\\n(decides action)"] -->|"tool call"| Tools["🔧 Tools\\n(execute action)"]
    Tools -->|"tool result"| LLM
    LLM -->|"final answer"| Done["✅ Final Response"]
  end
  Agent --> Response["📤 Response to User"]
  style Agent fill:#1c2128,stroke:#bc8cff
  style LLM fill:#21262d,stroke:#58a6ff
  style Tools fill:#21262d,stroke:#3fb950""",
        "merChart_1": """\
stateDiagram-v2
  [*] --> agent : User input
  agent --> tools : LLM calls a tool
  tools --> agent : Tool result returned
  agent --> [*] : LLM produces final answer
  note right of agent
    calls LLM with current state
  end note
  note right of tools
    executes the requested tool and appends result to state
  end note""",
        "merChart_2": """\
sequenceDiagram
  participant U as User
  participant A as Agent
  participant T as Tools
  U->>A: What is the weather in Paris?
  Note over A: Thought - I need weather data, I will call weather_api.
  A->>T: weather_api(city=Paris)
  T-->>A: Weather in Paris - 22 degrees C and sunny
  Note over A: Thought - I have the data, I can answer now.
  A-->>U: The weather in Paris is 22 degrees C and sunny.""",
        "merChart_3": """\
flowchart TB
  User["👤 User"] --> Supervisor
  subgraph Supervisor["🎯 Supervisor Agent"]
    direction LR
    SLLM["LLM decides\\nwhich agent to call"]
  end
  Supervisor -->|"weather task"| WA["🏤️ Weather Agent\\n+ weather_api tool"]
  Supervisor -->|"search task"| SA["🔍 Search Agent\\n+ google_search_api tool"]
  WA & SA -->|"result"| Supervisor
  Supervisor --> Out["📤 Final Answer"]
  style Supervisor fill:#1c2128,stroke:#bc8cff
  style WA fill:#1c2128,stroke:#3fb950
  style SA fill:#1c2128,stroke:#58a6ff""",
    },
    "multi_agent.html": {
        "merChart_0": """\
flowchart TB
  User["👤 User"] --> S
  subgraph S["🎯 Supervisor Agent"]
    SLLM["LLM reasons:\\nwhich agent handles this?"]
  end
  S -->|"needs weather"| WA
  S -->|"needs web search"| SA
  S -->|"needs math"| CA
  subgraph WA["🏤️ Weather Agent"]
    direction LR
    WLLM2["LLM"] --> WT["weather_api\\ntool"]
  end
  subgraph SA["🔍 Search Agent"]
    direction LR
    SLLM2["LLM"] --> ST["google_search_api\\ntool"]
  end
  subgraph CA["🔢 Calc Agent"]
    direction LR
    CLLM["LLM"] --> CT["calculator\\ntool"]
  end
  WA & SA & CA -->|"result"| S
  S --> User
  style S fill:#1c2128,stroke:#bc8cff
  style WA fill:#1c2128,stroke:#3fb950
  style SA fill:#1c2128,stroke:#58a6ff
  style CA fill:#1c2128,stroke:#e3b341""",
        "merChart_1": """\
stateDiagram-v2
  [*] --> supervisor : User input
  supervisor --> weather_agent : weather-related question
  supervisor --> search_agent : search/lookup question
  supervisor --> [*] : can answer directly
  weather_agent --> supervisor : result
  search_agent --> supervisor : result
  note right of supervisor
    LLM decides routing based on the question content
  end note""",
        "merChart_2": """\
flowchart TB
  U["👤 User"] --> MA
  subgraph MA["Multi-Agent Orchestrator (LangGraph)"]
    direction TB
    SUP["Supervisor LLM\\n(routes queries)"]
  end
  MA --> WA & SA & RA
  subgraph WA["Weather Agent"]
    direction LR
    WC["LangChain\\nChain"] --> WMCP["FastMCP\\nweather_api tool"]
  end
  subgraph SA["Search Agent"]
    direction LR
    SC["LangChain\\nChain"] --> SMCP["FastMCP\\nsearch tool"]
  end
  subgraph RA["RAG Agent"]
    direction LR
    RC["LangChain\\nChain"] --> CHROMA["ChromaDB\\nRetriever"]
  end
  WA & SA & RA -->|result| MA
  MA --> U
  GROQ["⚡ Groq\\nopenai/gpt-oss-120b"] -.->|"inference"| WC & SC & RC & SUP
  style MA fill:#1c2128,stroke:#bc8cff
  style WA fill:#1c2128,stroke:#3fb950
  style SA fill:#1c2128,stroke:#58a6ff
  style RA fill:#1c2128,stroke:#e3b341
  style GROQ fill:#21262d,stroke:#8b949e""",
    },
    "fastmcp.html": {
        "merChart_0": """\
flowchart LR
  subgraph Dev["👨‍💻 Developer writes"]
    F1["@mcp.tool\\ndef greet(name)"]
    F2["@mcp.resource\\ndef config()"]
    F3["@mcp.prompt\\ndef system_prompt()"]
  end
  subgraph FastMCP["⚡ FastMCP handles"]
    direction TB
    S["JSON-RPC schema\\ngeneration"]
    T["Transport\\n(stdio / HTTP / SSE)"]
    V["Input validation\\n& type coercion"]
  end
  subgraph Wire["🔌 Wire Protocol (MCP)"]
    W["tools/list\\ntools/call\\nresources/read\\nprompts/get"]
  end
  Dev --> FastMCP --> Wire
  style Dev fill:#1c2128,stroke:#3fb950
  style FastMCP fill:#1c2128,stroke:#e3b341
  style Wire fill:#1c2128,stroke:#58a6ff""",
    },
    "langchain.html": {
        "merChart_0": """\
flowchart LR
  A["📝 PromptTemplate\\n(formats user input)"] -->|"LangChain LCEL"| B["🤖 ChatGroq LLM\\n(generates response)"]
  B --> C["🔧 OutputParser\\n(formats output)"]
  style A fill:#1c2128,stroke:#58a6ff
  style B fill:#1c2128,stroke:#3fb950
  style C fill:#1c2128,stroke:#bc8cff""",
        "merChart_1": """\
flowchart LR
  IN["topic=AI"] --> PT
  PT["PromptTemplate\\n.from_messages(...)"] -->|"ChatPromptValue"| LLM
  LLM["ChatGroq\\n(model='...')"] -->|"AIMessage"| OP
  OP["StrOutputParser"] -->|"str"| OUT["AI is ..."]
  style IN fill:#21262d,stroke:#30363d
  style OUT fill:#21262d,stroke:#3fb950""",
        "merChart_2": """\
flowchart LR
  IN["topic=ML"] --> P1
  subgraph Chain1["Chain 1 - Expert explanation"]
    P1["ChatPromptTemplate\\n(expert)"] --> LLM1["ChatGroq"]
  end
  subgraph Chain2["Chain 2 - Simplification"]
    LLM1 --> P2["PromptTemplate\\n(simplify)"]
    P2 --> LLM2["ChatGroq"]
    LLM2 --> OP["StrOutputParser"]
  end
  OP --> OUT["Beginner-friendly\\nexplanation"]
  style Chain1 fill:#1c2128,stroke:#58a6ff
  style Chain2 fill:#1c2128,stroke:#3fb950""",
    },
    "rag.html": {
        "merChart_0": """\
flowchart TB
  subgraph Indexing["📥 Indexing (one-time setup)"]
    direction LR
    D["📄 Documents\\n(text chunks)"] --> E["Embedding\\nModel"] --> V["Vector Store\\n(ChromaDB / PGVector)"]
  end
  subgraph Querying["🔍 Query Time (every request)"]
    direction LR
    Q["❓ User Question"] --> QE["Embed\\nQuestion"] --> S["Similarity\\nSearch"]
    S -->|"Top-K docs"| P["Build Prompt\\nwith context"]
    P --> L["🤖 LLM\\n(ChatGroq)"]
    L --> A["✅ Answer\\n(grounded in docs)"]
  end
  V --> S
  style Indexing fill:#1c2128,stroke:#e3b341
  style Querying fill:#1c2128,stroke:#58a6ff""",
        "merChart_1": """\
graph LR
  A[Documents] --> B[Chunking] --> C[Embeddings] --> D[Vector Database] --> E[Retriever] --> F[LLM Prompt] --> G[Answer]
  style A fill:#21262d,stroke:#e3b341,color:#e6edf3
  style B fill:#21262d,stroke:#e3b341,color:#e6edf3
  style C fill:#21262d,stroke:#e3b341,color:#e6edf3
  style D fill:#21262d,stroke:#bc8cff,color:#e6edf3
  style E fill:#21262d,stroke:#58a6ff,color:#e6edf3
  style F fill:#21262d,stroke:#58a6ff,color:#e6edf3
  style G fill:#21262d,stroke:#3fb950,color:#e6edf3""",
        "merChart_2": """\
flowchart LR
  A["1️⃣ Load\\nDocuments"] --> B["2️⃣ Split into\\nChunks"]
  B --> C["3️⃣ Embed\\nEach Chunk"]
  C --> D["4️⃣ Store in\\nVector DB"]
  D --> E["5️⃣ Embed\\nUser Query"]
  E --> F["6️⃣ Similarity\\nSearch"]
  F --> G["7️⃣ Inject into\\nPrompt"]
  G --> H["8️⃣ LLM\\nGenerates Answer"]
  style A fill:#21262d,stroke:#e3b341
  style B fill:#21262d,stroke:#e3b341
  style C fill:#21262d,stroke:#e3b341
  style D fill:#21262d,stroke:#e3b341
  style E fill:#21262d,stroke:#58a6ff
  style F fill:#21262d,stroke:#58a6ff
  style G fill:#21262d,stroke:#58a6ff
  style H fill:#21262d,stroke:#3fb950""",
        "merChart_3": """\
graph LR
  A["Vector A - cat on sofa"] -->|"cos=0.97 very similar"| B["Vector B - kitten on couch"]
  A -->|"cos=0.12 unrelated"| C["Vector C - AI transforms tech"]
  B -->|"cos=0.14 unrelated"| C
  style A fill:#21262d,stroke:#58a6ff
  style B fill:#21262d,stroke:#3fb950
  style C fill:#21262d,stroke:#e3b341""",
        "merChart_4": """\
flowchart LR
  D["📄 Documents"] --> E["HuggingFace\\nEmbeddings"] --> C
  subgraph C["💾 ChromaDB (./chroma_db)"]
    direction TB
    I["Index\\n(HNSW)"]
    M["Metadata\\n(SQLite)"]
  end
  Q["❓ Query"] --> QE["Embed\\nQuery"] --> SS["Similarity\\nSearch"] --> R["Top-K\\nResults"]
  C --> SS
  style C fill:#1c2128,stroke:#e3b341""",
    },
    "fastApi.html": {
        "merChart_0": """\
sequenceDiagram
  participant C as Client
  participant MW as Middleware Stack
  participant R as Router
  participant D as Dependencies
  participant H as Handler
  participant DB as Database
  C->>MW: HTTP Request
  MW->>MW: CORS Check
  MW->>MW: Rate Limit / Auth Header Read
  MW->>R: Forwarded Request
  R->>R: Path Match
  R->>D: Resolve Dependencies
  D->>DB: get_db() open session
  DB-->>D: AsyncSession
  D->>D: get_current_user() decode JWT
  D-->>H: (db, current_user, ...)
  H->>DB: Query / Mutation via CRUD layer
  DB-->>H: ORM result
  H-->>R: return ORM object
  R-->>MW: Pydantic serialize to JSONResponse
  MW-->>C: Final HTTP Response""",
        "merChart_1": """\
flowchart TD
  A[Request In] --> B{Middleware}
  B --> C{Route Match?}
  C -- No --> E[404 Not Found]
  C -- Yes --> F{Dependencies OK?}
  F -- Auth Failed --> G[401 / 403]
  F -- Validation Error --> H[422 Unprocessable]
  F -- OK --> I[Handler Function]
  I --> J[CRUD Layer]
  J --> K[(Database)]
  K --> J
  J --> I
  I --> L{response_model}
  L --> M[Pydantic Serialize]
  M --> N[JSONResponse Out]""",
        "merChart_2": """\
flowchart LR
  subgraph Client
    A["POST /products\\n{name, sku, price}"]
    B["PATCH /products/1\\n{price: 249}"]
    C["PUT /products/1\\n{name, sku, price, stock}"]
  end
  subgraph Schemas
    D["ProductCreate\\nAll required"]
    E["ProductUpdate\\nAll Optional"]
  end
  subgraph Handler
    F["CRUD Layer\\n+ DB Session"]
  end
  subgraph Response
    G["ProductResponse\\nid, name, price\\ncreated_at, updated_at"]
  end
  A --> D --> F --> G
  B --> E --> F
  C --> D --> F""",
        "merChart_3": """\
flowchart LR
  subgraph RequestIn["Request In"]
    A["ProductCreate\\nname required\\nsku required\\nprice required\\ndescription optional\\nstock optional=0"]
    B["ProductUpdate\\nname Optional\\nprice Optional\\ndescription Optional\\nstock Optional\\nis_active Optional"]
  end
  subgraph ResponseOut["Response Out"]
    C["ProductResponse\\nid\\nname, sku, price\\ndescription, stock\\nis_active, owner_id\\ncreated_at, updated_at"]
  end
  A -->|POST / PUT| H[Handler]
  B -->|PATCH| H
  H --> C""",
        "merChart_4": """\
sequenceDiagram
  participant C as Client
  participant FW as FastAPI
  participant SC as ProductCreate
  participant CR as product_crud
  participant DB as PostgreSQL
  C->>FW: POST /products name=Headphones sku=WH1 price=299
  FW->>SC: Pydantic validates + coerces body
  SC-->>FW: typed ProductCreate obj or 422 if invalid
  FW->>CR: create_product(db, payload, owner_id)
  CR->>DB: INSERT INTO products RETURNING id
  DB-->>CR: Row with id=1 created_at updated_at
  CR->>CR: db.refresh(product) - loads all DB-set fields
  CR-->>FW: Product ORM object
  FW->>SC: Serialize via ProductResponse
  FW-->>C: 201 Created with id name and headphones data""",
        "merChart_5": """\
flowchart TD
  A["POST /products\\nJSON body"] --> B["FastAPI reads body"]
  B --> C{"Pydantic validates\\nProductCreate"}
  C -->|"field error"| D["422 Unprocessable\\nerrors list"]
  C -->|"valid"| E["Route handler called\\nwith typed payload obj"]
  E --> F["Check SKU duplicate\\nproduct_crud.get_by_sku()"]
  F -->|"exists"| G["409 Conflict\\nSKU already registered"]
  F -->|"unique"| H["product_crud.create_product(db, payload, owner_id)"]
  H --> I["Product from payload\\ndb.add(product)\\nawait db.flush()"]
  I --> J[("PostgreSQL\\nINSERT INTO products\\nRETURNING id")]
  J --> K["await db.refresh(product)\\nloads id, created_at, updated_at"]
  K --> L["return product ORM object"]
  L --> M["get_db() commits transaction\\nsession closes"]
  M --> N["FastAPI serializes via response_model=ProductResponse"]
  N --> O["201 JSON Response\\nid, name, sku, price..."]
  style D fill:#2a1020,stroke:#ff4d6a,color:#ff4d6a
  style G fill:#2a1020,stroke:#ff4d6a,color:#ff4d6a
  style O fill:#0a2a1a,stroke:#00e5a0,color:#00e5a0""",
        "merChart_6": """\
flowchart LR
  R[Request] --> MW3[RateLimitMiddleware]
  MW3 --> MW2[RequestLogMiddleware]
  MW2 --> MW1[CORSMiddleware]
  MW1 --> H[Handler]
  H --> MW1R[CORSMiddleware]
  MW1R --> MW2R[RequestLogMiddleware]
  MW2R --> MW3R[RateLimitMiddleware]
  MW3R --> Resp[Response]""",
        "merChart_7": """\
sequenceDiagram
  participant U as User
  participant API as FastAPI
  participant DB as Database
  U->>API: POST /auth/token email + password
  API->>DB: Lookup user by email
  DB-->>API: User record
  API->>API: verify_password(plain, hashed)
  API-->>U: access_token, refresh_token, token_type
  Note over U,API: Subsequent requests
  U->>API: GET /me Authorization Bearer token
  API->>API: decode_token() payload
  API->>DB: get_user(payload sub)
  DB-->>API: User obj
  API-->>U: UserResponse JSON""",
        "merChart_8": """\
flowchart TD
  A[JWT Token] --> B[decode_token]
  B --> C{payload.role}
  C -->|admin| D["✅ Full Access"]
  C -->|user| E{Resource Owner?}
  E -->|Yes| F["✅ Own Resources"]
  E -->|No| G["❌ 403 Forbidden"]
  C -->|guest| H["❌ Read-Only Public"]""",
        "merChart_9": """\
sequenceDiagram
  participant U as Browser
  participant API as FastAPI
  U->>API: GET /oauth2/authorize
  API-->>U: Redirect to Provider Google or GitHub
  U->>API: Callback with code=AUTH_CODE
  API->>API: Exchange code for access_token
  API->>API: Fetch user profile from provider
  API->>API: Find or create user in DB
  API-->>U: Set-Cookie session or Return JWT""",
        "merChart_10": """\
flowchart TD
  Q1{"Clear relationships\\nbetween data?"} -->|Yes| Q2{"Need ACID\\ntransactions?"}
  Q2 -->|Yes| PG[PostgreSQL + SQLAlchemy]
  Q2 -->|Partial| Q3{"Need full-text\\nsearch?"}
  Q3 -->|Yes| ES[Elasticsearch + PG]
  Q3 -->|No| PG
  Q1 -->|"No/Flexible schema"| Q4{"Document or\\nkey-value?"}
  Q4 -->|Documents| MG[MongoDB + Motor]
  Q4 -->|"Cache / Sessions"| RD[Redis]
  Q4 -->|"Time series"| TS[TimescaleDB]""",
        "merChart_11": """\
flowchart LR
  C[Client] --> N["Nginx / Caddy\\nReverse Proxy + TLS"]
  N --> G[Gunicorn Process Manager]
  G --> W1[Uvicorn Worker 1]
  G --> W2[Uvicorn Worker 2]
  G --> W3[Uvicorn Worker N]
  W1 --> DB[(PostgreSQL)]
  W1 --> R[(Redis)]""",
    },
}


def update_file(filename: str, diagrams: dict[str, str]) -> None:
    path = DOCS_DIR / filename
    if not path.exists():
        print(f"  {filename}: NOT FOUND, skipping")
        return

    content = path.read_text("utf-8")

    # Find the _diagrams block
    block_match = re.search(
        r"(        var _diagrams = \{)(.*?)(\s*        \};)",
        content,
        re.DOTALL,
    )
    if not block_match:
        print(f"  {filename}: no _diagrams block found, skipping")
        return

    # Build new block body
    lines = []
    for key, code in sorted(diagrams.items()):
        # Escape backtick and ${ for JS template literals
        safe_code = code.replace("`", "\\`").replace("${", "\\${")
        lines.append(f"      {key}: `{safe_code}`,")

    new_body = "\n" + "\n".join(lines) + "\n      "
    new_content = (
        content[: block_match.start(2)] + new_body + content[block_match.end(2) :]
    )

    path.write_text(new_content, "utf-8")
    print(f"  {filename}: wrote {len(diagrams)} diagram(s)")


if __name__ == "__main__":
    print("Writing correct mermaid diagram definitions...")
    for filename, diagrams in DIAGRAMS.items():
        update_file(filename, diagrams)
    print("Done.")
