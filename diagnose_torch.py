#!/usr/bin/env python3
"""
Diagnose PyTorch DLL load problems on Windows (WinError 1114).
Run inside your virtualenv:
  .\.venv\Scripts\Activate.ps1
  python diagnose_torch.py

This script prints environment info, attempts to import torch,
and if import fails locates `c10.dll` under site-packages and tries
`ctypes.WinDLL` to surface the underlying Windows loader error.
"""
import sys
import os
import platform
import traceback
import glob
import ctypes
from datetime import datetime

def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

print(f"[{now()}] Diagnose PyTorch environment")
print(f"Python executable: {sys.executable}")
print(f"Python version: {platform.python_version()} ({platform.platform()})")
print(f"sys.path (first 10):")
for p in sys.path[:10]:
    print('  ', p)
print('\nEnvironment PATH (last 6 entries):')
for p in (os.environ.get('PATH','').split(os.pathsep)[-6:]):
    print('  ', p)

print('\nTrying import torch...')
try:
    import torch
    print('torch imported successfully')
    try:
        print('torch.__version__ =', torch.__version__)
    except Exception:
        pass
    try:
        print('torch.__file__ =', torch.__file__)
    except Exception:
        pass
    try:
        print('cuda available =', torch.cuda.is_available())
    except Exception:
        pass
    sys.exit(0)
except Exception as e:
    print('Import failed:')
    traceback.print_exc()

# locate c10.dll under site-packages
print('\nSearching for c10.dll under site-packages...')
site_packages = []
# Common locations
candidates = [sys.prefix, sys.exec_prefix]
for base in candidates:
    for root in (os.path.join(base, 'Lib', 'site-packages'), os.path.join(base, 'lib', 'site-packages')):
        if os.path.isdir(root):
            site_packages.append(root)

# also include entries from sys.path that look like site-packages
for p in sys.path:
    if p and ('site-packages' in p or 'site-packages' in p.replace('\\', '/')):
        if os.path.isdir(p) and p not in site_packages:
            site_packages.append(p)

found = []
for sp in site_packages:
    for path in glob.glob(os.path.join(sp, 'torch', 'lib', 'c10.dll')):
        found.append(path)
    # fallback: any c10.dll anywhere under site-packages
    for path in glob.glob(os.path.join(sp, '**', 'c10.dll'), recursive=True):
        if 'site-packages' in path:
            found.append(path)

if not found:
    print('No c10.dll found in site-packages locations. You can still inspect the torch package location manually.')
    print('Candidate site-packages scanned:')
    for sp in site_packages:
        print('  ', sp)
    print('\nYou can run `python -c "import torch; print(torch.__file__)"` after fixing import to locate exact path.')
    sys.exit(2)

print('Found c10.dll candidates:')
for f in found:
    print('  ', f)

# attempt to load each DLL with ctypes to surface loader error
for f in found:
    print(f"\nAttempting ctypes.WinDLL on: {f}")
    try:
        ctypes.WinDLL(f)
        print('  ctypes.WinDLL succeeded (DLL loaded)')
    except Exception as e:
        print('  ctypes.WinDLL failed:')
        traceback.print_exc()

print('\nDiagnostic finished. Please paste the full output here so I can analyze the loader error and recommend next steps.')
