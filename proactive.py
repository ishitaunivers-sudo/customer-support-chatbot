"""Reach out before the customer complains."""
from datetime import date
MSG = {
 "delay": {"en": "Hi {n}, your order {id} ({item}) is running late. New ETA: {eta}. Sorry! Reply if you'd prefer a refund or reship.",
           "es": "Hola {n}, su pedido {id} ({item}) se retrasa. Nueva fecha: {eta}. ¡Disculpe! Responda si prefiere reembolso.",
           "fr": "Bonjour {n}, votre commande {id} ({item}) est en retard. Nouvelle date: {eta}. Répondez pour un remboursement."},
 "payment": {"en": "Hi {n}, your payment of {amt} (card ending {card}) didn't go through. Your order is held for 24h - reply to retry or update the card.",
             "es": "Hola {n}, su pago de {amt} (tarjeta {card}) falló. Su pedido se reserva 24h; responda para reintentar.",
             "fr": "Bonjour {n}, votre paiement de {amt} (carte {card}) a échoué. Commande conservée 24h; répondez pour réessayer."},
}
def scan(customers, today=None):
    today, out = today or date.today().isoformat(), []
    for cid, c in customers.items():
        lang = c.get("lang", "en")
        for o in c.get("orders", []):
            if o["status"] == "delayed" or (o["status"] != "delivered" and o.get("eta", "9999") < today):
                out.append({"customer": cid, "reason": "delivery_delay", "lang": lang,
                            "message": MSG["delay"].get(lang, MSG["delay"]["en"]).format(n=c["name"], **{"id": o["id"], "item": o["item"], "eta": o.get("new_eta", o["eta"])})})
        for p in c.get("payments", []):
            if p["status"] == "failed":
                out.append({"customer": cid, "reason": "payment_failed", "lang": lang,
                            "message": MSG["payment"].get(lang, MSG["payment"]["en"]).format(n=c["name"], amt=p["amount"], card=p["card"])})
    return out
