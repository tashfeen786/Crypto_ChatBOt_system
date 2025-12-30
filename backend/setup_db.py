# backend/setup_db.py
import sqlite3
from datetime import datetime

def setup_database():
    """
    Setup SQLite database with all required tables
    """
    print("🔧 Setting up database...")
    
    # Connect to database (creates if doesn't exist)
    conn = sqlite3.connect('crypto_advisor.db')
    cursor = conn.cursor()
    
    try:
        # ==================== USERS TABLE ====================
        print("📋 Creating users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                balance REAL DEFAULT 1000.0,
                risk_tolerance INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ==================== PORTFOLIO TABLE ====================
        print("📋 Creating portfolio table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                quantity REAL NOT NULL,
                avg_buy_price REAL NOT NULL,
                current_price REAL,
                total_invested REAL NOT NULL,
                current_value REAL,
                profit_loss REAL,
                profit_loss_percentage REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, symbol)
            )
        """)
        
        # ==================== TRANSACTIONS TABLE ====================
        print("📋 Creating transactions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                symbol TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                total_amount REAL NOT NULL,
                fee REAL DEFAULT 0.0,
                status TEXT DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # ==================== CHAT HISTORY TABLE ====================
        print("📋 Creating chat_history table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                coins_mentioned TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # ==================== WATCHLIST TABLE ====================
        print("📋 Creating watchlist table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, symbol)
            )
        """)
        
        # ==================== ALERTS TABLE ====================
        print("📋 Creating alerts table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                target_price REAL,
                condition TEXT,
                is_active INTEGER DEFAULT 1,
                triggered_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # ==================== INDEXES ====================
        print("📋 Creating indexes...")
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_user ON portfolio(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_history_user ON chat_history(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_watchlist_user ON watchlist(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id)")
        
        # Commit changes
        conn.commit()
        
        print("✅ Database setup completed successfully!")
        print("\n📊 Tables created:")
        print("   - users")
        print("   - portfolio")
        print("   - transactions")
        print("   - chat_history")
        print("   - watchlist")
        print("   - alerts")
        
        # Show database info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n✅ Total tables: {len(tables)}")
        
    except Exception as e:
        print(f"❌ Error setting up database: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

def add_test_user():
    """
    Add a test user for development
    """
    import hashlib
    import secrets
    
    print("\n🧪 Adding test user...")
    
    conn = sqlite3.connect('crypto_advisor.db')
    cursor = conn.cursor()
    
    try:
        # Check if test user already exists
        cursor.execute("SELECT user_id FROM users WHERE email = ?", ("test@test.com",))
        if cursor.fetchone():
            print("⚠️  Test user already exists!")
            return
        
        # Hash password (same method as auth.py)
        password = "test123"
        salt = secrets.token_hex(32)
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        hashed_password = f"{salt}${pwd_hash}"
        
        # Insert test user
        cursor.execute("""
            INSERT INTO users (user_id, name, email, password_hash, balance, risk_tolerance)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "test_user_123",
            "Test User",
            "test@test.com",
            hashed_password,
            10000.0,
            5
        ))
        
        conn.commit()
        
        print("✅ Test user created!")
        print("   Email: test@test.com")
        print("   Password: test123")
        print("   Balance: $10,000")
        print("   Risk Tolerance: 5/10")
        
    except Exception as e:
        print(f"❌ Error adding test user: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def show_database_stats():
    """
    Show database statistics
    """
    print("\n📊 Database Statistics:")
    
    conn = sqlite3.connect('crypto_advisor.db')
    cursor = conn.cursor()
    
    try:
        # Count users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"   Users: {user_count}")
        
        # Count transactions
        cursor.execute("SELECT COUNT(*) FROM transactions")
        transaction_count = cursor.fetchone()[0]
        print(f"   Transactions: {transaction_count}")
        
        # Count chat history
        cursor.execute("SELECT COUNT(*) FROM chat_history")
        chat_count = cursor.fetchone()[0]
        print(f"   Chat Messages: {chat_count}")
        
    except Exception as e:
        print(f"❌ Error getting stats: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Crypto AI Advisor - Database Setup")
    print("=" * 50)
    
    # Setup database
    setup_database()
    
    # Add test user
    response = input("\n❓ Do you want to add a test user? (y/n): ")
    if response.lower() == 'y':
        add_test_user()
    
    # Show stats
    show_database_stats()
    
    print("\n" + "=" * 50)
    print("✅ Setup Complete!")
    print("=" * 50)
    print("\n💡 Next steps:")
    print("   1. Run backend: uvicorn main:app --reload")
    print("   2. Run frontend: cd ../frontend && npm run dev")
    print("   3. Visit: http://localhost:3000")
    print("")