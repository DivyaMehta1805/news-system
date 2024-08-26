import sqlite3
import pandas as pd

def setup_database(csv_file_path, db_file_path):
    # Read the CSV file
        df = pd.read_csv(csv_file_path)
    
        print(f"CSV file read successfully. Shape: {df.shape}")
        
        # Connect to SQLite database (or create if it doesn't exist)
        conn = sqlite3.connect(db_file_path)
        print(f"Connected to database: {db_file_path}")
        
        # Write the dataframe to SQLite
        df.to_sql('articles', conn, if_exists='replace', index=False)
        print("Data written to 'articles' table")
        
        # Create an index on the 'best_matching_topic' column for faster queries
        conn.execute('CREATE INDEX IF NOT EXISTS idx_topic ON articles(best_matching_topic)')
        print("Index created on 'best_matching_topic' column")
        
        # Verify the data
        cursor = conn.cursor()
        
        # Check the number of rows
        cursor.execute("SELECT COUNT(*) FROM articles")
        row_count = cursor.fetchone()[0]
        print(f"Number of rows in the database: {row_count}")
        
        # Check the table structure
        cursor.execute("PRAGMA table_info(articles)")
        columns = cursor.fetchall()
        print("Table structure:")
        for column in columns:
            print(f"  {column[1]} ({column[2]})")
        
        # Check a few rows
        cursor.execute("SELECT * FROM articles LIMIT 5")
        sample_rows = cursor.fetchall()
        print("Sample rows:")
        for row in sample_rows:
            print(f"  {row}")
        
        conn.close()
        print(f"Database created successfully at {db_file_path}")
        return True
    

# Usage
success = setup_database('output_with_embeddings.csv', 'articles.db')
if success:
    print("Database setup completed successfully.")
else:
    print("Database setup failed.")   