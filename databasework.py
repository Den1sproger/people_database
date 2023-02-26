import os

import pymysql
import pymysql.cursors

from dotenv import load_dotenv, find_dotenv



load_dotenv(find_dotenv())
host = os.getenv('host')
user = os.getenv('user')
password = os.getenv('password')
db_name = os.getenv('db_name')


class Database:
    """The class responsible for working with the database of people"""

    def __init__(self):
        # Connect to the database
        # Подключение к базе данных
        try: 
            self.connection = pymysql.connect(
                host=host, user=user, port=3306,
                password=password, database=db_name,
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception as _ex:
            print(_ex)


    def view_people(self) -> str:
        # Viewing people in the database
        # Просмотр людей в базе данных
        people = ''
        with self.connection:
            with self.connection.cursor() as cursor:
                insert_query = "SELECT id, surname FROM persons;"
                cursor.execute(insert_query)
                rows = cursor.fetchall()
                for row in rows:
                    people += f"{str(row['id'])} {row['surname']}\n" 
                return people


    def add_person(self, name: str, info: str) -> str:
        # Adding a person to the databaase
        # Добавление человека в базу данных
        with self.connection:
            with self.connection.cursor() as cursor:
                insert_query = f"INSERT INTO persons (surname, biography)" \
                f"VALUES ('{name}', '{info}');"
                cursor.execute(insert_query)
            self.connection.commit()


    def add_review(self, text: str, person_id: int) -> None:
        # Adding a review about person to the database
        # Добавление отзыва о человеке в базу данных
        with self.connection:
            with self.connection.cursor() as cursor:
                insert_query = f"INSERT INTO reviews (review, person_id)" \
                f"VALUES ('{text}', {person_id});"
                cursor.execute(insert_query)
            self.connection.commit()


    def select_person(self, id: int) -> list:
        # Select a person to view
        # Выбрать человека для просмотра
        with self.connection:
            with self.connection.cursor() as cursor:
                insert_query = f"SELECT * FROM persons WHERE id = {id};"
                cursor.execute(insert_query)
                return cursor.fetchall()
                    

    def view_reviews(self, person_id: int) -> list:
        # Viewing the reviews about a person
        # Просмотр отзывов о человеке
        with self.connection:
            with self.connection.cursor() as cursor:
                insert_query = f"SELECT review FROM reviews WHERE person_id = {person_id}"
                cursor.execute(insert_query)
                return cursor.fetchall()


    def __del__(self):
        # Destructor
        pass


