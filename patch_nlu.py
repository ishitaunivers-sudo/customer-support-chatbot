p = "supportbot/nlu.py"
t = open(p, encoding="utf-8").read()
if '"delivery_delay": "where status ' not in t:
    t = t.replace('"delivery_delay": "delivery ', '"delivery_delay": "where status delivery ')
open(p, "w", encoding="utf-8").write(t)
print("nlu.py updated")
