import os, json, hashlib

BASE = "updates"
manifest = {}

for root, _, files in os.walk(BASE):
    for f in files:
        path = os.path.join(root, f)
        with open(path, "rb") as file:
            manifest[path.replace(BASE + "/", "")] = hashlib.md5(file.read()).hexdigest()

with open("updates/manifest.json", "w") as out:
    json.dump(manifest, out, indent=2)
