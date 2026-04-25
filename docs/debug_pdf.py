# -*- coding: utf-8 -*-
import sys
sys.stdout = sys.stderr

print("Starting...")

try:
    from reportlab.lib.pagesizes import A4
    print("reportlab ok")
except Exception as e:
    print(f"reportlab error: {e}")

try:
    import pypdfium2
    print("pypdfium2 ok")
except Exception as e:
    print(f"pypdfium2 error: {e}")

print("All imports done")
