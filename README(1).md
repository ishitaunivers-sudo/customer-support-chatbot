# SupportBot – confidence-gated customer support automation

```
message → language detect → intent (typo-tolerant) → sentiment tracker
        → KB retrieval + customer data → draft → tone/language rewrite (LLM)
        → confidence scorer ──≥ threshold──► reply
                             └─ < threshold / angry repeat / fraud / "human" ─► HandoffQueue (full packet)
proactive.scan(customers)  → outreach before complaints
FeedbackStore              → CSAT → sft.jsonl, review_queue.jsonl, threshold tuning
```

| Requirement | Module |
|---|---|
| Poor-grammar intent | `nlu.py` (repeat-char collapse, fuzzy vocab matching) |
| Empathy / tone adaptation | `nlu.SentimentTracker`, `bot.py` |
| Personalisation | `bot._resolve` (orders, payments) |
| Confidence → escalation | `bot.respond` (0.4 intent + 0.3 KB + 0.2 personal data + 0.1 sentiment − 0.2/repeat) |
| Live handoff | `handoff.py` (transcript, profile, intent, sentiment trend, suggested fix, priority) |
| Proactive outreach | `proactive.py` (delays, failed payments) |
| Multilingual | `nlu.detect_language`, localized templates, `AnthropicLLM` for full translation |
| Surveys + learning loop | `feedback.py` |

Run: `python demo.py` (no dependencies). For production LLM replies: `pip install anthropic`, set `ANTHROPIC_API_KEY`, `Bot(customers, llm=AnthropicLLM())`.

## Production roadmap
1. **Fine-tuning**: ingest historical tickets → redact PII → `intent`-labelled SFT; use `export_training()` output for continual updates; use `review_queue.jsonl` as preference negatives.
2. **Swap-ins**: heuristic `classify` → fine-tuned classifier/LLM with calibrated probabilities; `kb.retrieve` → vector search (RAG); `detect_language` → fastText/lingua.
3. **Infra**: FastAPI + WebSocket gateway, Redis session state, Postgres for tickets/feedback, queue (Kafka/SQS) for proactive events, CRM/ticketing connectors (Zendesk, Salesforce) at the handoff.
4. **Safeguards**: PII masking, audit logs, per-domain high-risk lists (banking: fraud, chargeback; telecom: porting), threshold calibration per intent against held-out data.
5. **Known limits of this core**: single-intent per message, keyword seeds, English KB (non-English replies need the LLM rewriter).
