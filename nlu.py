"""Language detection, noisy-text intent classification, sentiment tracking."""
import re, difflib, math

STOP = {
 "en": {"the","is","my","and","not","i","to","it","was","has","have","order","where"},
 "es": {"el","la","mi","y","no","es","pedido","que","de","llegó","hola","donde"},
 "fr": {"le","la","mon","et","pas","est","commande","je","de","où","n'est"},
 "de": {"der","die","das","mein","und","nicht","ist","bestellung","ich","wo"},
 "hi": {"mera","nahi","hai","kyun","abhi","kab","kya","mujhe","paisa"},
}
SCRIPTS = {"hi": r"[\u0900-\u097F]", "ar": r"[\u0600-\u06FF]", "zh": r"[\u4E00-\u9FFF]", "ru": r"[\u0400-\u04FF]"}

def detect_language(text, default="en"):
    for lang, rx in SCRIPTS.items():
        if re.search(rx, text): return lang
    toks = set(re.findall(r"[\w']+", text.lower()))
    best = max(STOP, key=lambda l: len(toks & STOP[l]))
    return best if toks & STOP[best] else default

INTENTS = {  # multilingual keyword seeds; fuzzy-matched so typos still hit
 "delivery_delay": "where status delivery delivered late delay shipped shipping tracking package parcel arrive arrived pedido llegó retraso livraison commande lieferung bestellung",
 "payment_failed": "payment paid charged declined failed card transaction pago tarjeta paiement zahlung paisa",
 "refund": "refund return money back exchange reembolso remboursement erstattung",
 "cancel": "cancel cancellation unsubscribe terminate cancelar annuler kündigen",
 "account_access": "login password locked account otp access reset sign",
 "technical": "error bug crash broken working internet network signal outage slow app",
 "billing_dispute": "bill invoice overcharged charge dispute double duplicate",
 "human_request": "human agent person representative manager supervisor",
 "high_risk": "fraud scam stolen lawyer legal sue court police unauthorized chargeback",
}
VOCAB = {w: i for i, ws in INTENTS.items() for w in ws.split()}

def normalize(text):
    text = re.sub(r"(.)\1{2,}", r"\1\1", text.lower())  # "sloooow" -> "sloow"
    toks = re.findall(r"[\w']+", text)
    out = []
    for t in toks:
        if t in VOCAB or len(t) < 4: out.append(t); continue
        m = difflib.get_close_matches(t, VOCAB, n=1, cutoff=0.8)
        out.append(m[0] if m else t)
    return out

def classify(text):
    """-> (intent, confidence in 0..1)"""
    scores = {}
    for t in normalize(text):
        if t in VOCAB: scores[VOCAB[t]] = scores.get(VOCAB[t], 0) + 1
    if not scores: return "unknown", 0.1
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    top, n = ranked[0]
    conf = min(1.0, 0.5 + 0.25 * n)
    if len(ranked) > 1 and ranked[1][1] == n: conf *= 0.7  # ambiguous
    return top, conf

NEG = set("angry terrible worst useless scam furious unacceptable late broken hate waste ridiculous horrible never fraud pathetic rubbish disgusting".split())
POS = set("thanks thank great good perfect happy love resolved awesome appreciate".split())

class SentimentTracker:
    """Per-message score in [-1,1] plus smoothed trend across the conversation."""
    def __init__(self): self.history, self.ema = [], 0.0
    def update(self, text):
        toks = re.findall(r"[\w']+", text.lower())
        p, n = sum(t in POS for t in toks), sum(t in NEG for t in toks)
        raw = (p - n) / max(1, p + n) * min(1, (p + n) / 2 + 0.3)
        letters = [c for c in text if c.isalpha()]
        if len(letters) > 8 and sum(c.isupper() for c in letters) / len(letters) > 0.6: raw -= 0.4
        raw -= 0.1 * min(3, text.count("!")) if n else 0
        s = math.tanh(raw * 1.5)
        self.history.append(round(s, 2))
        self.ema = 0.6 * s + 0.4 * self.ema if len(self.history) > 1 else s
        return s
    @property
    def trend(self):
        h = self.history
        if len(h) < 2: return "stable"
        return "worsening" if h[-1] < h[-2] - 0.2 else "improving" if h[-1] > h[-2] + 0.2 else "stable"
