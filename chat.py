from supportbot import Bot, Conversation

CUSTOMERS = {
 "C1": {"name": "Asha", "tier": "gold", "lang": "en",
        "orders": [{"id": "A-1042", "item": "Headphones", "status": "delayed", "eta": "2026-10-08", "new_eta": "2026-10-14"}],
        "payments": []},
 "C2": {"name": "Luis", "tier": "std", "lang": "es",
        "orders": [{"id": "B-7", "item": "Zapatillas", "status": "shipped", "eta": "2026-10-12"}],
        "payments": [{"amount": "$59", "card": "4417", "status": "failed"}]},
}

bot = Bot(CUSTOMERS)
cid = input("Customer ID (C1 ya C2): ").strip() or "C1"
conv = Conversation(cid)
print("Type karo. Band karne ke liye 'exit' likho.\n")

while True:
    msg = input("You: ")
    if msg.lower() == "exit":
        break
    r = bot.respond(conv, msg)
    print(f"Bot: {r['text']}")
    print(f"     [intent={r['intent']} confidence={r['confidence']} escalated={r['escalated']}]\n")
