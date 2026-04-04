import os

# Find similar service names
services = {}
for dir_name in os.listdir('.'):
    if os.path.isdir(dir_name):
        # Extract base name without suffixes
        base = dir_name.replace('-service', '').replace('-admin', '').replace('-enhanced', '').replace('-complete', '').replace('-system', '')
        if base not in services:
            services[base] = []
        services[base].append(dir_name)

# Find duplicates
duplicates = {k: v for k, v in services.items() if len(v) > 1}

print("=== DUPLICATE SERVICES FOUND ===")
for base, dirs in sorted(duplicates.items()):
    print(f"\n{base}:")
    for d in sorted(dirs):
        print(f"  - {d}")

print(f"\n\nTotal service groups with duplicates: {len(duplicates)}")
