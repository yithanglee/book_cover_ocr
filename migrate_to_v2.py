#!/usr/bin/env python3
"""
Migration script from v1 to v2
- Migrates meta.json to SQLite database
- Regenerates embeddings with CLIP model
- Backs up old files
"""
import shutil
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def backup_file(filepath: str):
    """Create a backup of a file with timestamp"""
    path = Path(filepath)
    if not path.exists():
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_suffix(f".backup_{timestamp}{path.suffix}")
    shutil.copy2(path, backup_path)
    logger.info(f"Backed up {filepath} → {backup_path}")
    return backup_path


def migrate():
    """Run the complete migration process"""
    logger.info("="*60)
    logger.info("Starting migration from v1 to v2")
    logger.info("="*60)
    
    # Step 1: Backup important files
    logger.info("\n[1/4] Backing up existing files...")
    backup_file("meta.json")
    backup_file("embeddings.npy")
    backup_file("app.py")
    
    # Step 2: Initialize database and migrate data
    logger.info("\n[2/4] Migrating data to SQLite database...")
    from utils.database import initialize_database, migrate_from_json
    
    initialize_database()
    migrated_count = migrate_from_json()
    logger.info(f"✓ Migrated {migrated_count} books to SQLite")
    
    # Step 3: Initialize CLIP model
    logger.info("\n[3/4] Initializing CLIP model...")
    from utils.embedding_v2 import initialize_clip_model
    initialize_clip_model()
    logger.info("✓ CLIP model loaded successfully")
    
    # Step 4: Regenerate embeddings with CLIP
    logger.info("\n[4/4] Regenerating embeddings with CLIP...")
    from generate_embeddings_v2 import generate_embeddings
    generate_embeddings(use_clip=True)
    
    # Step 5: Summary and next steps
    logger.info("\n" + "="*60)
    logger.info("Migration completed successfully!")
    logger.info("="*60)
    logger.info("\nNext steps:")
    logger.info("1. Replace app.py with app_v2.py:")
    logger.info("   mv app.py app_old.py")
    logger.info("   mv app_v2.py app.py")
    logger.info("\n2. Install new dependencies:")
    logger.info("   pip install -r requirements.txt")
    logger.info("\n3. Start the upgraded service:")
    logger.info("   uvicorn app:app --host 0.0.0.0 --port 8000")
    logger.info("\n4. Test the service:")
    logger.info("   curl http://localhost:8000/health")
    logger.info("\n5. The old files are backed up with timestamps")
    logger.info("="*60)


if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        logger.error(f"\nMigration failed: {e}", exc_info=True)
        logger.error("\nPlease check the error and try again.")
        exit(1)

