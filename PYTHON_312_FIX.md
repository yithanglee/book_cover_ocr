# Python 3.12+ Installation Fix

## Problems with Python 3.12

Python 3.12 has TWO breaking changes that affect our dependencies:

1. **Removed `distutils` module** → Causes setuptools errors
2. **Removed `pkgutil.ImpImporter`** → Causes numpy 1.24.3 build failures
3. **Old packages don't have Python 3.12 wheels** → Forces building from source (fails)

## Solution: Use Python 3.12 Compatible Versions

### Option 1: Use Python 3.12 Install Script (RECOMMENDED) ⭐

```bash
cd /home/ubuntu/Development/book_cover_ocr
chmod +x install_py312.sh
./install_py312.sh
```

This script:
1. Upgrades pip, setuptools, and wheel
2. Uses `requirements_py312.txt` with compatible versions
3. Installs numpy 1.26.4 (instead of 1.24.3)
4. Installs PyTorch 2.2.1 (instead of 2.1.2)
5. Uses binary wheels (no building from source)
6. Verifies everything works

### Option 2: Manual Installation with Python 3.12 Requirements

```bash
# Step 1: Upgrade pip and setuptools
python3 -m pip install --upgrade pip setuptools wheel

# Step 2: Install numpy first (from binary wheel)
pip install numpy==1.26.4

# Step 3: Install PyTorch
pip install torch==2.2.1 torchvision==0.17.1 --index-url https://download.pytorch.org/whl/cpu

# Step 4: Install remaining dependencies
pip install -r requirements_py312.txt
```

## Why This Happens

Python 3.12 removed `distutils` which was deprecated since Python 3.10. Some older packages still depend on it, so we need to:

1. **Upgrade setuptools**: Modern setuptools provides a replacement for distutils
2. **Upgrade pip**: Latest pip knows how to handle this situation
3. **Upgrade wheel**: Helps with building packages

## Verification

After running the fix, verify it works:

```bash
python3 -c "import torch; import transformers; import faiss; import fastapi; print('✓ Success!')"
```

You should see: `✓ Success!`

## Package Version Differences

| Package | Original (Py 3.8-3.11) | Python 3.12 Compatible |
|---------|------------------------|------------------------|
| numpy | 1.24.3 | 1.26.4 ✓ |
| torch | 2.1.2 | 2.2.1 ✓ |
| torchvision | 0.16.2 | 0.17.1 ✓ |
| transformers | 4.36.2 | 4.38.2 ✓ |
| onnxruntime | 1.16.3 | 1.17.1 ✓ |
| faiss-cpu | 1.7.4 | 1.8.0 ✓ |
| aiosqlite | 0.19.0 | 0.20.0 ✓ |

## Alternative: Use Python 3.8-3.11

If you prefer to avoid Python 3.12:

```bash
# Check if you have Python 3.11 or 3.10
python3.11 --version || python3.10 --version

# Create venv with older Python
python3.11 -m venv venv  # or python3.10
source venv/bin/activate
pip install -r requirements.txt  # Use original requirements
```

## After Fixing

Once dependencies are installed, you can proceed with:

```bash
# Migrate from v1
python3 migrate_to_v2.py

# Start the service
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Still Having Issues?

If you still get errors:

1. **Check Python version**:
   ```bash
   python3 --version
   ```

2. **Clear pip cache**:
   ```bash
   pip cache purge
   ```

3. **Reinstall in clean environment**:
   ```bash
   deactivate  # if in venv
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   ./fix_python312.sh
   ```

4. **Check available disk space**:
   ```bash
   df -h
   ```
   PyTorch needs ~2GB of free space.

5. **Install system packages** (if needed):
   ```bash
   sudo apt-get update
   sudo apt-get install python3-dev python3-pip build-essential
   ```

## Summary

**For Python 3.12+**: Always upgrade pip/setuptools FIRST before installing other packages!

```bash
python3 -m pip install --upgrade pip setuptools wheel
```

This is the #1 fix for Python 3.12 installation issues.

