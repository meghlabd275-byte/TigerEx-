import os
import re

# Define exchanges to check
exchanges = ['binance', 'bybit', 'okx', 'kucoin', 'bitget', 'mexc', 'bitmart', 'coinw']

print("Checking Exchange Integrations in TigerEx\n")
print("=" * 80)

# Search for exchange mentions in backend files
for exchange in exchanges:
    print(f"\n{exchange.upper()} Integration:")
    print("-" * 40)
    
    found_files = []
    
    # Search in backend directory
    for root, dirs, files in os.walk('backend'):
        for file in files:
            if file.endswith(('.py', '.js', '.rs', '.go')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        if exchange in content:
                            found_files.append(file_path)
                except:
                    pass
    
    if found_files:
        print(f"  Found in {len(found_files)} files:")
        for f in found_files[:5]:
            print(f"    - {f}")
        if len(found_files) > 5:
            print(f"    ... and {len(found_files) - 5} more files")
    else:
        print(f"  NOT FOUND - Needs implementation")

print("\n" + "=" * 80)