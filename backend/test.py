# backend/debug_db.py
import sqlite3
import hashlib
import secrets

def hash_password(password: str) -> str:
    """Hash password"""
    salt = secrets.token_hex(32)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"

def verify_password(plain_password: str, stored_password: str) -> bool:
    """Verify password"""
    try:
        salt, stored_hash = stored_password.split('$')
        pwd_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
        return pwd_hash == stored_hash
    except Exception as e:
        print(f"Verify error: {e}")
        return False

def check_database():
    """Check database status"""
    print("=" * 60)
    print("🔍 DATABASE DEBUG TOOL")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('crypto_advisor.db')
        cursor = conn.cursor()
        
        # Check if database exists
        print("\n✅ Database file exists")
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✅ Found {len(tables)} tables: {[t[0] for t in tables]}")
        
        # Check users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✅ Total users: {user_count}")
        
        if user_count == 0:
            print("\n⚠️  NO USERS FOUND! Creating test user...")
            create_test_user(cursor, conn)
            return
        
        # List all users
        print("\n👥 ALL USERS:")
        print("-" * 60)
        cursor.execute("SELECT user_id, name, email, password_hash FROM users")
        users = cursor.fetchall()
        
        for user in users:
            print(f"ID: {user[0]}")
            print(f"Name: {user[1]}")
            print(f"Email: {user[2]}")
            print(f"Hash: {user[3][:50]}...")
            
            # Test password
            if user[2] == "test@test.com":
                print("\n🔐 Testing password 'test123'...")
                if verify_password("test123", user[3]):
                    print("✅ Password verification: SUCCESS")
                else:
                    print("❌ Password verification: FAILED")
                    print("🔧 Fixing password...")
                    fix_password(cursor, conn, user[2])
            print("-" * 60)
        
        conn.close()
        
    except sqlite3.OperationalError as e:
        print(f"\n❌ Database error: {e}")
        print("💡 Run: python setup_db.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def create_test_user(cursor, conn):
    """Create test user"""
    try:
        password = "test123"
        hashed = hash_password(password)
        
        cursor.execute("""
            INSERT INTO users (user_id, name, email, password_hash, balance, risk_tolerance)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "test_user_123",
            "Test User",
            "test@test.com",
            hashed,
            10000.0,
            5
        ))
        
        conn.commit()
        print("✅ Test user created!")
        print("   Email: test@test.com")
        print("   Password: test123")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        conn.rollback()

def fix_password(cursor, conn, email):
    """Fix user password"""
    try:
        password = "test123"
        hashed = hash_password(password)
        
        cursor.execute("""
            UPDATE users 
            SET password_hash = ?
            WHERE email = ?
        """, (hashed, email))
        
        conn.commit()
        print("✅ Password fixed!")
        
        # Verify
        cursor.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
        new_hash = cursor.fetchone()[0]
        
        if verify_password("test123", new_hash):
            print("✅ Verification: SUCCESS")
        else:
            print("❌ Verification: FAILED")
        
    except Exception as e:
        print(f"❌ Error fixing password: {e}")
        conn.rollback()

def test_api():
    """Test API endpoint"""
    import requests
    
    print("\n" + "=" * 60)
    print("🧪 TESTING API ENDPOINT")
    print("=" * 60)
    
    try:
        # Test health
        print("\n1️⃣ Testing health endpoint...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test login
        print("\n2️⃣ Testing login endpoint...")
        response = requests.post(
            "http://localhost:8000/api/auth/login",
            json={"email": "test@test.com", "password": "test123"},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            data = response.json()
            print(f"Token: {data.get('access_token', '')[:50]}...")
        else:
            print(f"❌ Login failed!")
            print(f"Response: {response.text}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Backend not running!")
        print("💡 Run: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_database()
    
    print("\n" + "=" * 60)
    response = input("🧪 Test API endpoints? (y/n): ")
    if response.lower() == 'y':
        test_api()
    
    print("\n" + "=" * 60)
    print("✅ Debug Complete!")
    print("=" * 60)