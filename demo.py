from supportbot import Bot, Conversation, scan, FeedbackStore
from supportbot.feedback import build_survey
CUSTOMERS = {
 "C1": {"name": "Asha", "tier": "gold", "lang": "en", "orders": [{"id": "A-1042", "item": "Headphones", "status": "delayed", "eta": "2026-10-08", "new_eta": "2026-10-14"}], "payments": []},
 "C2": {"name": "Luis", "tier": "std", "lang": "es", "orders": [{"id": "B-7", "item": "Zapatillas", "status": "shipped", "eta": "2026-10-12"}], "payments": [{"amount": "$59", "card": "4417", "status": "failed"}]},
}
bot, fb = Bot(CUSTOMERS), FeedbackStore("feedback.jsonl")
print("== PROACTIVE ==")
for o in scan(CUSTOMERS, "2026-10-10"): print(f"[{o['customer']}/{o['lang']}] {o['message']}")
def chat(cid, msgs, csat, **kw):
    conv = Conversation(cid); print(f"\n== {cid} ==")
    for m in msgs:
        r = bot.respond(conv, m)
        print(f"U: {m}\nB: {r['text']}\n   [intent={r['intent']} conf={r['confidence']} escalated={r['escalated']} {r['reason'] or ''}]")
    fb.record(conv, csat, **kw); return conv
chat("C1", ["wher is my ordr?? its sooo laate"], 5)
chat("C1", ["THIS IS RIDICULOUS!! my package is still late, worst service", "still late!! useless, i hate this"], 2)
chat("C2", ["hola, mi pedido no llegó y mi pago falló"], 4)
c = chat("C1", ["i think someone made unauthorized charges, this is fraud"], 3, agent_resolution="I've blocked the card and opened a fraud case.")
print("\nHANDOFF PACKET:\n", bot.queue.dump(bot.queue.queue[-1])[:900], "...")
print("\nSURVEY:", build_survey(c)["questions"][0])
print("EXPORT:", fb.export_training(), "| tuned threshold:", fb.tune_threshold(bot.threshold))
