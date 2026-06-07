# agentic-supply-chain-azure-foundry
Multi-agent supply-chain workflow in Azure AI Foundry — orchestrator + 4 specialized agents, with responsible-AI design notes.

# Agentic Supply Chain Workflow — Microsoft Azure AI Foundry

A working **multi-agent system** built in Microsoft Azure AI Foundry: an orchestrator agent coordinating four specialized worker agents to automate an end-to-end supply-chain workflow — **Bill of Materials extraction → inventory check → supplier sourcing → purchase order generation** — with failure handling and human-in-the-loop stops.

Built entirely through configuration and prompt engineering (no application code), this project demonstrates orchestration patterns, grounding, and responsible-AI design that transfer directly to regulated software development lifecycles.

---

## Architecture

```
                          USER REQUEST
                               │
                               ▼
                  ┌────────────────────────────┐
                  │     ORCHESTRATOR AGENT      │
                  │     (GPT-4.1, temp = 1)     │
                  │  Fixed sequence + Halt logic│
                  └─────────────┬───────────────┘
        ┌───────────────┬───────┴───────┬────────────────┐
        ▼               ▼               ▼                ▼
  ┌───────────┐   ┌────────────┐  ┌────────────┐  ┌──────────────┐
  │ BOM Agent │ → │ Inventory  │→ │ Supplier   │→ │ Purchase     │
  │ 4.1-mini  │   │ 4.1-mini   │  │ Analysis   │  │ Order        │
  │ temp 0    │   │ temp 0     │  │ 4.1, temp  │  │ 4.1-mini     │
  │           │   │ + AI Search│  │ 0.7 + docs │  │ + Code Interp│
  │ sales kit │   │ (inventory)│  │ (suppliers)│  │ (date.py)    │
  └───────────┘   └────────────┘  └────────────┘  └──────────────┘
   extracts BOM   finds shortages   sources         generates POs
                                    suppliers        w/ real date

  Each agent's structured JSON output feeds the next.
  Orchestrator HALTS the chain if any worker returns "Halt".
```

---

## The Agents

| Agent | Model | Temp | Role | Grounding / Tool |
|-------|-------|------|------|------------------|
| **Orchestrator** | GPT-4.1 | 1 | Routes the request through workers in fixed order; halts on failure | Connected agents |
| **BOM Extraction** | GPT-4.1-mini | 0 | Parses an unstructured sales-kit PDF into a structured Bill of Materials (JSON) | File search (sales kits) |
| **Inventory Evaluation** | GPT-4.1-mini | 0 | Checks each material against warehouse stock; computes shortages | Azure AI Search index |
| **Supplier Analysis** | GPT-4.1 | 0.7 | Matches shorted materials to approved suppliers; recommends on price/risk | File search (supplier matrix) |
| **Purchase Order** | GPT-4.1-mini | 0 | Generates formatted POs with the real current date | Code Interpreter (date.py) |

---

## Model Selection (Cost-Aware)

Models were assigned deliberately, matching capability to task complexity:

- **GPT-4.1-mini** for deterministic, well-scoped steps (extraction, lookups, formatting) — cheaper and sufficient.
- **GPT-4.1** only where genuine reasoning is required (orchestration routing/halt decisions; multi-factor supplier analysis weighing price *and* risk).

This is intentional FinOps: don't pay frontier-model rates for work a smaller model does well.

---

## Key Engineering Lessons

**1. Don't make a probabilistic model do a deterministic job.**
Early on, the inventory agent hallucinated stock counts and the supplier agent invented vendors that didn't exist. The fix wasn't a better prompt — it was recognizing that exact lookups belong in a **query**, and facts (like today's date) belong in **code**. The LLM was kept on the messy, unstructured work (parsing documents, reasoning) where it earns its keep.

**2. Put the LLM only on the unstructured side of the data boundary.**
- Unstructured (sales-kit PDFs, supplier docs) → LLM extraction & analysis ✅
- Structured/exact (stock quantity, current date) → deterministic query / code ✅

**3. RAG suits large unstructured corpora; small/structured reference data belongs in context.**
File-search over a small tabular supplier matrix fragmented the table and produced hallucinations. Providing the data in full context (or via a deterministic query) restored accuracy.

**4. Grounding rules matter.** Every data-reading agent was instructed to use only tool-returned values, never invent, and treat "not found" as zero — turning silent failures into safe, visible ones.

**5. Anti-fragile orchestration.** The orchestrator halts the entire chain the moment a worker returns "Halt" (e.g., a sales kit isn't found) — observable, predictable, and safe to stop.

---

## Testing

The workflow was validated end-to-end across multiple product kits, plus partial-workflow and individual-agent tests:

- **Full run:** orchestrator invokes BOM → Inventory → Supplier → Purchase Order in sequence, outputting both raw JSON per step and a human-readable summary.
- **Halt run:** a nonexistent kit triggers "Halt" at the BOM step; the chain stops cleanly.
- **Partial runs:** each agent tested individually with provided context (CoT / ReAct patterns).

---

## Why This Matters

This was a supply-chain example, but the patterns — orchestration, structured hand-offs, deterministic tools for facts, and human-in-the-loop accountability — map directly to **regulated software development lifecycles (SaMD / MedTech)**, where AI can accelerate every phase but a named human must stay accountable for every decision. In regulated environments, the boundary between *probabilistic* and *deterministic* isn't an optimization — it's the line between **auditable** and **unshippable**.

---

## Stack

- **Microsoft Azure AI Foundry** (Agent Service, classic Connected Agents)
- **Azure OpenAI** — GPT-4.1, GPT-4.1-mini
- **Azure AI Search** (inventory index + indexer)
- **Azure Table Storage** (inventory data source)
- **Code Interpreter** (Python, for deterministic date insertion)

---

*Built as a hands-on validation of agentic workflow patterns for regulated product development.*

