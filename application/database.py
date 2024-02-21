import sqlite3
import hashlib
import secrets


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("userdata.db")
        self.cur = self.conn.cursor()
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS userdata (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                username VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                salt VARCHAR(255) NOT NULL
            )
        """)

        self.cur.execute("""
                   CREATE TABLE IF NOT EXISTS test_results (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_id INTEGER,
                       test_type VARCHAR(255),
                       pose VARCHAR(255),
                       test_date DATE,
                       test_result VARCHAR(255),
                       FOREIGN KEY (user_id) REFERENCES userdata (id)
                   )
               """)

        self.conn.commit()

    """
        Funkcja register_user() jest wykorzystywana przy rejestrowanu nowych 
        użytkowników. W funkcji generowana jest randomowa sól, po czym hasło 
        jest haszowane razem z randomową solą i pozycja jest dodawana do 
        tabeli w bazie danych. 
    """
    def register_user(self, username, password):
        salt = secrets.token_hex(16)
        hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
        self.cur.execute("INSERT INTO userdata (username, password, salt) VALUES (?, ?, ?)", (username, hashed_password, salt))
        self.conn.commit()

    """
        Funkcja verify_user() jest wykorzystywana przy logowaniu się użytkowników,
        pobiera z bazy danych wiersze, gdzie nazwa użytkownika zgadza się z 
        wprowadzoną przy logowaniu. Jeżeli hasło zgadza się z wprowadzonym przy 
        rejestracji to użytkownik pomyślnie zaloguje się na swoje konto.
    """
    def verify_user(self, username, password):
        self.cur.execute("SELECT * FROM userdata WHERE username = ?", (username,))
        user_data = self.cur.fetchone()
        if user_data:
            hashed_password = hashlib.sha256((password + user_data[3]).encode()).hexdigest()
            if user_data[2] == hashed_password:
                return [True, user_data[0]]
        return False

    """
        Funkcja check_username() wykorzystywana jest przy rejestracji, sprawdza, czy 
        nie powtarza sie nazwa użytkownika z nazw już zapisanych w bazie danych. 
        Nie ma możliwości rejestracji bez unikalnej nazwy użytkownika.
    """
    def check_username(self, username):
        self.cur.execute("SELECT * FROM userdata WHERE username = ?", (username,))
        user_data = self.cur.fetchone()
        return user_data is None

    def get_test_results(self, user_id):
        self.cur.execute("SELECT * FROM test_results WHERE user_id = ?", (user_id,))
        return self.cur.fetchall()

    def add_test_result(self, user_id, test_type, pose, test_date, test_result):
        self.cur.execute("INSERT INTO test_results (user_id, test_type, pose, test_date, test_result) VALUES (?, ?, "
                         "?, ?, ?)",
                         (user_id, test_type, pose, test_date, test_result))
        self.conn.commit()

    def __del__(self):
        self.conn.close()
