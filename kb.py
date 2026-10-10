import re
KB = [
 {"id": "KB-101", "intent": "delivery_delay", "text": "I'm sorry for the delay. If your order is more than 7 days late, I can arrange a reshipment or a refund."},
 {"id": "KB-102", "intent": "payment_failed", "text": "Failed payments are usually caused by a bank decline or an expired card. Please retry or update your card; your order is held for 24 hours."},
 {"id": "KB-103", "intent": "refund", "text": "Refunds are issued to the original payment method within 5-7 business days after the return is received. Returns are accepted within 30 days."},
 {"id": "KB-104", "intent": "cancel", "text": "You can cancel an order at no charge before it ships. Subscriptions end at the close of your billing cycle."},
 {"id": "KB-105", "intent": "account_access", "text": "Use 'Forgot password' to get a reset link. Accounts lock for 30 minutes after 5 failed attempts."},
 {"id": "KB-106", "intent": "technical", "text": "Please restart your device, check our service status page and make sure the app is up to date. If the outage continues, a ticket is created automatically."},
 {"id": "KB-107", "intent": "billing_dispute", "text": "Duplicate or incorrect charges are reviewed within 3 business days, and you are credited if the error is confirmed."},
]
def retrieve(intent, query):
    q = set(re.findall(r"\w{4,}", query.lower()))
    best, score = None, 0.0
    for d in KB:
        if d["intent"] != intent: continue
        ov = len(q & set(re.findall(r"\w{4,}", d["text"].lower())))
        s = 0.6 + 0.4 * min(1, ov / 2)
        if s > score: best, score = d, s
    return best, score
