#!/usr/bin/env python3
"""
Copy frontend files to backend directory for Railway deployment
"""
import os
import shutil
from pathlib import Path

# Get paths
backend_dir = Path(__file__).parent
repo_root = backend_dir.parent
frontend_source = repo_root / "frontend"
frontend_dest = backend_dir / "frontend"

print(f"[COPY] Source: {frontend_source}")
print(f"[COPY] Destination: {frontend_dest}")
print(f"[COPY] Source exists: {frontend_source.exists()}")
print(f"[COPY] Destination exists: {frontend_dest.exists()}")

if frontend_source.exists() and frontend_source.is_dir():
    # Remove existing destination if it exists
    if frontend_dest.exists():
        print(f"[COPY] Removing existing {frontend_dest}")
        shutil.rmtree(frontend_dest)
    
    # Copy frontend to backend
    print(f"[COPY] Copying {frontend_source} to {frontend_dest}")
    shutil.copytree(frontend_source, frontend_dest)
    print(f"[COPY] Success! Frontend copied to {frontend_dest}")
    
    # Verify index.html exists
    index_file = frontend_dest / "index.html"
    if index_file.exists():
        print(f"[COPY] Verified: index.html exists at {index_file}")
    else:
        print(f"[COPY] WARNING: index.html not found at {index_file}")
else:
    print(f"[COPY] ERROR: Frontend source not found at {frontend_source}")

