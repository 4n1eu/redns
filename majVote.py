from resolver import resolve_domain

all = []

a1 = resolve_domain("4n1.eu", "txt")
a2 = resolve_domain("google.de", "txt")

if not a1:
    exit()
if not a1:
    exit()

for rrset in a1:
    all.append(rrset)
for rrset in a2:
    all.append(rrset)

for rrset in all:
    print(rrset)

