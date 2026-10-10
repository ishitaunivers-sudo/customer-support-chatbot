import uuid
from .nlu import detect_language, classify, SentimentTracker
from .kb import retrieve
from .llm import TemplateLLM
from .handoff import HandoffQueue

EMPATHY = {
 "en": "I'm really sorry for the trouble - I understand how frustrating this is. ",
 "es": "Lamento mucho el inconveniente, entiendo lo frustrante que es. ",
 "fr": "Je suis vraiment désolé pour ce désagrément, je comprends votre frustration. ",
 "de": "Es tut mir wirklich leid, ich verstehe Ihren Ärger. ",
 "hi": "Asuvidha ke liye khed hai, main aapki pareshani samajhta hoon. ",
}
HANDOFF = {
 "en": "I'm connecting you with a specialist now. They'll see our whole conversation, so you won't need to repeat anything.",
 "es": "Le paso con un especialista; verá toda la conversación, no tendrá que repetir nada.",
 "fr": "Je vous mets en relation avec un spécialiste; il verra toute la conversation.",
 "de": "Ich verbinde Sie mit einem Spezialisten; er sieht den gesamten Verlauf.",
 "hi": "Main aapko specialist se jod raha hoon; unhe poori baatcheet dikhegi.",
}
ALWAYS_ESCALATE = {"human_request", "high_risk"}

class Conversation:
    def __init__(self, customer_id):
        self.id, self.customer_id = uuid.uuid4().hex[:8], customer_id
        self.turns, self.sentiment, self.lang = [], SentimentTracker(), "en"
        self.last_intent, self.escalated, self.intent_log = None, False, []

class Bot:
    def __init__(self, customers, llm=None, queue=None, threshold=0.55):
        self.customers, self.llm, self.queue, self.threshold = customers, llm or TemplateLLM(), queue or HandoffQueue(), threshold

    def _resolve(self, intent, cust, doc):
        """Draft an answer from KB + customer data. Returns (text, personalised?)."""
        if not doc: return "", False
        name, text, personal = cust.get("name", ""), doc["text"], False
        orders = cust.get("orders", [])
        if intent == "delivery_delay" and orders:
            o = next((x for x in orders if x["status"] != "delivered"), orders[-1])
            text = f"{name}, your order {o['id']} ({o['item']}) is '{o['status']}', ETA {o.get('new_eta', o.get('eta','unknown'))}. " + text
            personal = True
        elif intent == "payment_failed" and cust.get("payments"):
            p = cust["payments"][-1]
            text = f"{name}, your payment of {p['amount']} on card ending {p['card']} shows '{p['status']}'. " + text
            personal = True
        elif intent == "refund" and orders:
            text = f"{name}, I can start a return for {orders[-1]['item']}. " + text; personal = True
        return text, personal

    def respond(self, conv, text):
        lang = detect_language(text, conv.lang); conv.lang = lang
        s = conv.sentiment.update(text)
        intent, ic = classify(text)
        if intent == "unknown" and conv.last_intent: intent, ic = conv.last_intent, 0.5  # follow-up
        repeats = conv.intent_log.count(intent)
        conv.intent_log.append(intent); conv.last_intent = intent
        cust = self.customers.get(conv.customer_id, {})
        doc, ks = retrieve(intent, text)
        draft, personal = self._resolve(intent, cust, doc)

        conf = 0.4 * ic + 0.3 * ks + 0.2 * personal + 0.1 * (conv.sentiment.ema > -0.5) - 0.2 * repeats
        conf = max(0.0, min(1.0, conf))
        reason = ("customer_request" if intent == "human_request" else "high_risk" if intent == "high_risk"
                  else "low_confidence" if conf < self.threshold
                  else "angry_repeat" if s < -0.7 and repeats >= 1 else None)

        conv.turns.append({"role": "customer", "text": text, "lang": lang, "sentiment": round(s, 2)})
        if reason:
            conv.escalated = True
            msg = (EMPATHY[lang] if s < -0.3 else "") + HANDOFF.get(lang, HANDOFF["en"])
            packet = self.queue.submit(conv, reason, draft or "No confident answer; triage manually.", {"id": conv.customer_id, **cust})
        else:
            tone = "empathetic" if s < -0.3 else "warm" if s > 0.3 else "neutral"
            msg = (EMPATHY.get(lang, EMPATHY["en"]) if tone == "empathetic" else "") + self.llm.rewrite(draft, lang, tone)
            packet = None
        conv.turns.append({"role": "bot", "text": msg, "confidence": round(conf, 2), "intent": intent})
        return {"text": msg, "intent": intent, "confidence": round(conf, 2), "escalated": bool(reason), "reason": reason, "handoff": packet}
