import json

with open('admin_control_report.json', 'r') as f:
    data = json.load(f)
    
print(f"Total Services: {data['summary']['total_services']}")
print(f"Services with Admin: {data['summary']['services_with_admin']}")
print(f"Services Missing Admin: {data['summary']['services_missing_admin']}")
print(f"Admin Coverage: {data['summary']['admin_coverage']}")
print(f"\nServices without admin controls:")

services_without_admin = []
for service, info in data['services'].items():
    if not info.get('has_admin_control', False):
        services_without_admin.append(service)
        print(f"  - {service}")

print(f"\nTotal services needing admin implementation: {len(services_without_admin)}")