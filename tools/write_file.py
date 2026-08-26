import base64, sys, os
p, d = sys.argv[1], sys.argv[2]
dn = os.path.dirname(p)
if dn:
    os.makedirs(dn, exist_ok=True)
open(p, 'wb').write(base64.b64decode(d))
print('Wrote:', p)
