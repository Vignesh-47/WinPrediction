import json
import sys
import re

# Set matplotlib backend to Agg to prevent GUI popups
try:
    import matplotlib
    matplotlib.use('Agg')
except ImportError:
    pass

def patch_source(source):
    """Fix known incompatibilities with newer pandas/sklearn versions."""

    # Fix 1: old pandas groupby().cumsum()['col'] -> groupby()['col'].cumsum()
    # Pattern: df.groupby('x').cumsum()['col']
    source = re.sub(
        r"([\w_]+)\.groupby\((['\"][\w_]+['\"])\)\.cumsum\(\)\[(['\"][\w_]+['\"])\]",
        r"\1.groupby(\2)[\3].cumsum()",
        source
    )

    # Fix 2: OneHotEncoder(sparse=False) -> OneHotEncoder(sparse_output=False)
    source = source.replace("OneHotEncoder(sparse=False", "OneHotEncoder(sparse_output=False")

    return source

print("Reading Untitled.ipynb...")
with open('Untitled.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Running notebook cells...")
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        if not source.strip():
            continue

        # Apply compatibility patches
        source = patch_source(source)

        print(f"Executing cell {i+1}...")
        try:
            exec(source, globals())
        except Exception as e:
            print(f"\n[ERROR] Failed at cell {i+1}: {e}", file=sys.stderr)
            print("Code content of the failed cell:", file=sys.stderr)
            print("-" * 40, file=sys.stderr)
            print(source, file=sys.stderr)
            print("-" * 40, file=sys.stderr)
            sys.exit(1)

print("\n[SUCCESS] All cells executed! 'pipe.pkl' has been generated.")
