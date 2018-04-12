import sqlite3
import pandas

def execute_query(query, db):
    """
    Envoie une requête SQL pour une abse de données fixée
    :param query: la requête SQL à évaluer
    :param db: la base de données à considérer
    :return: le résultat de la requête et le nom des colonnes du résultat
    """
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    headers = [i[0] for i in cursor.description]
    conn.close()
    return rows, headers


def return_dataset_from_query(query, db):
    """
    Renvoie le jeu de données correspondant au résultat d'une requête SQL données
    :param query: la requête SQL générant le jeu de données
    :param db: la base de données à considérer
    :return: le jeu de données sous forme d'un tableau 2D
    """
    result, headers = execute_query(query, db)
    dataset = []
    for row in result:
        dataset.append(row)
    return dataset, headers


def get_keys(database):
    keys = []
    con = sqlite3.connect(database)
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    result = cursor.fetchall()
    print('Tables: ', result)
    for table in result:
        table = table[0]
        cursor.execute("pragma table_info(" + table + ")")
        columns = cursor.fetchall()
        for c in columns:
            if c[-1] != 0:
                keys.append(c[1])
        cursor.execute("pragma foreign_key_list(" + table + ")")
        foreign_keys = cursor.fetchall()
        for fk in foreign_keys:
            keys.append(fk[3])

    print('Keys: ', keys)
    return keys


def create_database_packages(conn):
    cursor = conn.cursor()

    cursor.execute("""
            CREATE TABLE Cities(
                city_ID DECIMAL,
                distance DECIMAL,
                PRIMARY KEY (city_ID)
            )
        """)

    cursor.execute("""
       CREATE TABLE Packages(
            package_ID DECIMAL,
            destination DECIMAL,
            length DECIMAL,
            width DECIMAL,
            height DECIMAL,
            weight DECIMAL,
            price DECIMAL,
            PRIMARY KEY (package_ID)
            FOREIGN KEY (destination) references Villes(city_ID)
        )
    """)

    conn.commit()
    df = pandas.read_csv('newcolis10000_english.csv', sep=",")
    df.to_sql('Packages', conn, if_exists='append', index=False)

    df = pandas.read_csv('cities.csv', sep=",")
    df.to_sql('Cities', conn, if_exists='append', index=False)

