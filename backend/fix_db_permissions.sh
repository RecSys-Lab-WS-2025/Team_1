#!/bin/bash
# Fix database permissions and remove extended attributes

DB_PATH="data/app.db"
DB_DIR="data"

echo "🔧 Fixing database permissions..."

# 1. Remove extended attributes (macOS quarantine, etc.)
echo "1. Removing extended attributes..."
xattr -c "$DB_PATH" 2>/dev/null || true
xattr -c "$DB_DIR" 2>/dev/null || true

# 2. Set proper file permissions
echo "2. Setting file permissions..."
chmod 664 "$DB_PATH"
chmod 755 "$DB_DIR"

# 3. Verify permissions
echo "3. Verifying permissions..."
ls -la "$DB_PATH"
ls -ld "$DB_DIR"

# 4. Test write access
echo "4. Testing write access..."
python3 -c "
import sqlite3
import os
db_path = '$DB_PATH'
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        conn.execute('CREATE TABLE IF NOT EXISTS _permission_test (id INTEGER)')
        conn.execute('INSERT INTO _permission_test VALUES (1)')
        conn.commit()
        conn.execute('DROP TABLE _permission_test')
        conn.commit()
        conn.close()
        print('✅ Database is writable')
    except Exception as e:
        print(f'❌ Database write test failed: {e}')
        exit(1)
else:
    print('⚠️  Database file does not exist')
"

echo ""
echo "✅ Permission fix complete!"
echo "💡 Now restart your backend server:"
echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000"

