from sqlalchemy import text  


def test_database_connection(db_session):
    """Check that the database works and migrations are applied."""
    result = db_session.execute(text("SELECT 1")).fetchone()  
    assert result[0] == 1
    
    # Check that tables are created
    tables_result = db_session.execute(text("SHOW TABLES")).fetchall()      
    table_names = [row[0] for row in tables_result]
    
    # There should be at least the organization table
    assert 'organization' in table_names
    print(f"✅ Found tables: {table_names}")