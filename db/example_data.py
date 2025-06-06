import sqlite3
import pandas as pd
import os

def create_sample_sqlite_db():
    """Create a sample SQLite database for testing purposes"""
    
    # Create db directory if it doesn't exist
    db_dir = os.path.dirname(__file__)
    db_path = os.path.join(db_dir, "sample_data.db")
    
    # Sample data
    customers_data = {
        'customer_id': [1, 2, 3, 4, 5],
        'name': ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Eva Brown'],
        'email': ['alice@email.com', 'bob@email.com', 'carol@email.com', 'david@email.com', 'eva@email.com'],
        'age': [28, 35, 42, 31, 26],
        'city': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
    }
    
    orders_data = {
        'order_id': [101, 102, 103, 104, 105, 106, 107, 108],
        'customer_id': [1, 2, 1, 3, 4, 2, 5, 3],
        'product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Tablet', 'Headphones', 'Webcam', 'Speaker'],
        'amount': [999.99, 25.99, 79.99, 299.99, 499.99, 89.99, 149.99, 199.99],
        'order_date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19', '2024-01-20', '2024-01-21', '2024-01-22']
    }
    
    # Create database and tables
    conn = sqlite3.connect(db_path)
    
    # Create customers table
    customers_df = pd.DataFrame(customers_data)
    customers_df.to_sql('customers', conn, if_exists='replace', index=False)
    
    # Create orders table
    orders_df = pd.DataFrame(orders_data)
    orders_df.to_sql('orders', conn, if_exists='replace', index=False)
    
    # Create a sample analytics view
    conn.execute("""
        CREATE VIEW IF NOT EXISTS customer_summary AS
        SELECT 
            c.customer_id,
            c.name,
            c.city,
            COUNT(o.order_id) as total_orders,
            SUM(o.amount) as total_spent,
            AVG(o.amount) as avg_order_value
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.name, c.city
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Sample SQLite database created at: {db_path}")
    print("📊 Tables created: customers, orders, customer_summary (view)")
    print("\n🚀 Test your database connection with these settings:")
    print(f"   Database Type: SQLite")
    print(f"   Database File Path: {db_path}")
    
    return db_path

if __name__ == "__main__":
    create_sample_sqlite_db() 