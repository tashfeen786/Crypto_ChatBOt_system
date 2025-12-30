# backend/reset_password.py
import sqlite3
import hashlib
import secrets

def hash_password(password: str) -> str:
    """Same hashing method as auth.py"""
    salt = secrets.token_hex(32)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"

def verify_password(plain_password: str, stored_password: str) -> bool:
    """Verify password"""
    try:
        salt, stored_hash = stored_password.split('$')
        pwd_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
        return pwd_hash == stored_hash
    except:
        return False

def reset_test_user():
    """Reset test user password"""
    conn = sqlite3.connect('crypto_advisor.db')
    cursor = conn.cursor()
    
    try:
        # Check if test user exists
        cursor.execute("SELECT user_id, password_hash FROM users WHERE email = ?", ("test@test.com",))
        user = cursor.fetchone()
        
        if not user:
            print("❌ Test user not found!")
            return
        
        print(f"✅ Found user: {user[0]}")
        print(f"📝 Current hash: {user[1][:50]}...")
        
        # Test current password
        print("\n🔍 Testing current password 'test123'...")
        if verify_password("test123", user[1]):
            print("✅ Password already correct! Issue might be elsewhere.")
        else:
            print("❌ Password verification failed. Resetting...")
        
        # Generate new hash
        new_password = "test123"
        new_hash = hash_password(new_password)
        
        print(f"\n🔐 New hash generated: {new_hash[:50]}...")
        
        # Update password
        cursor.execute("""
            UPDATE users 
            SET password_hash = ?
            WHERE email = ?
        """, (new_hash, "test@test.com"))
        
        conn.commit()
        
        print("\n✅ Password reset successful!")
        print("   Email: test@test.com")
        print("   Password: test123")
        
        # Verify new password
        cursor.execute("SELECT password_hash FROM users WHERE email = ?", ("test@test.com",))
        updated_hash = cursor.fetchone()[0]
        
        if verify_password("test123", updated_hash):
            print("✅ Verification successful! Password works now.")
        else:
            print("❌ Verification failed! Something is wrong.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def list_all_users():
    """List all users in database"""
    conn = sqlite3.connect('crypto_advisor.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT user_id, name, email, balance FROM users")
        users = cursor.fetchall()
        
        print("\n👥 All Users:")
        print("-" * 60)
        for user in users:
            print(f"ID: {user[0]}")
            print(f"Name: {user[1]}")
            print(f"Email: {user[2]}")
            print(f"Balance: ${user[3]}")
            print("-" * 60)
        
        print(f"\n📊 Total Users: {len(users)}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        conn.close()

def delete_all_users():
    """Delete all users (fresh start)"""
    response = input("⚠️  Delete ALL users? This cannot be undone! (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Cancelled.")
        return
    
    conn = sqlite3.connect('crypto_advisor.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM users")
        conn.commit()
        print("✅ All users deleted!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def create_new_test_user():
    """Create a fresh test user"""
    conn = sqlite3.connect('crypto_advisor.db')
    cursor = conn.cursor()
    
    try:
        # Delete old test user if exists
        cursor.execute("DELETE FROM users WHERE email = ?", ("test@test.com",))
        
        # Create new test user
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
        
        print("✅ New test user created!")
        print("   Email: test@test.com")
        print("   Password: test123")
        
        # Verify
        cursor.execute("SELECT password_hash FROM users WHERE email = ?", ("test@test.com",))
        stored_hash = cursor.fetchone()[0]
        
        if verify_password("test123", stored_hash):
            print("✅ Password verification: SUCCESS")
        else:
            print("❌ Password verification: FAILED")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Password Reset Tool")
    print("=" * 60)
    
    while True:
        print("\n📋 Options:")
        print("1. Reset test user password")
        print("2. Create new test user")
        print("3. List all users")
        print("4. Delete all users")
        print("5. Exit")
        
        choice = input("\n👉 Choose option (1-5): ")
        
        if choice == "1":
            reset_test_user()
        elif choice == "2":
            create_new_test_user()
        elif choice == "3":
            list_all_users()
        elif choice == "4":
            delete_all_users()
        elif choice == "5":
            print("\n👋 Bye!")
            break
        else:
            print("❌ Invalid option!")