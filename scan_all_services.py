import os
import json

backend_dir = 'backend'
services = []

# Get all service directories
for item in os.listdir(backend_dir):
    item_path = os.path.join(backend_dir, item)
    if os.path.isdir(item_path):
        services.append(item)

services.sort()

print(f"Total Backend Services: {len(services)}")
print("\nAll Backend Services:")
for i, service in enumerate(services, 1):
    print(f"{i}. {service}")

# Save to file
with open('all_backend_services.json', 'w') as f:
    json.dump({
        'total': len(services),
        'services': services
    }, f, indent=2)

print(f"\nSaved to all_backend_services.json")