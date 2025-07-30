from sqlalchemy import text  


def test_database_connection(db_session):
    """Проверяем, что БД работает и миграции применены."""
    result = db_session.execute(text("SELECT 1")).fetchone()  
    assert result[0] == 1
    
    # Проверяем, что таблицы созданы
    tables_result = db_session.execute(text("SHOW TABLES")).fetchall()      
    table_names = [row[0] for row in tables_result]
    
    # Должна быть хотя бы таблица organization
    assert 'organization' in table_names
    print(f"✅ Найдены таблицы: {table_names}")
