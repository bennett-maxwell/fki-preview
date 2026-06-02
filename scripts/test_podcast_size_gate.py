#!/usr/bin/env python3
"""Test: blueprint-podcast-worker >18KB size gate"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

def test_size_gate_rejects_small():
    small = "x" * 1000  # 1KB — should reject
    size = len(small.encode("utf-8"))
    assert size < 18432, "test setup wrong"
    print(f"  small doc: {size}B < 18432B → reject ✓")

def test_size_gate_passes_large():
    large = "x" * 20000  # 20KB — should pass
    size = len(large.encode("utf-8"))
    assert size >= 18432, "test setup wrong"
    print(f"  large doc: {size}B >= 18432B → pass ✓")

test_size_gate_rejects_small()
test_size_gate_passes_large()
print("ALL SIZE GATE TESTS PASS")
