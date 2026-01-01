# CS311 Project 7 -- Luke Rickert
# Incorporates web scraping and database integration
# Scrapes Wikipedia for highest grossing films and stores info in a database. Some queries are available. 

#   Note: Now gives a 403 code. Can't be scraped anymore?

import requests
import sqlite3
from bs4 import BeautifulSoup
import re


class Movie:
    def __init__(self, t, g, y):
        self.title = t
        self.gross = self.cleanup_gross(g)
        self.year = self.cleanup_year(y)


    def cleanup_gross(self, income):
        income = re.sub(r'\D', '', income)  #remove all non-digits

        return int(income)
    
    
    def cleanup_year(self, year):
        return int(year.strip())
    

def printMenu():
    print(f"\n{'-' * 20}MENU{'-' * 20}\n")
    print("1. Search Movies by Year\n")
    print('2. Display the Highest-Grossing Movie\n')
    print('3. Display the Total Worldwide Gross\n')
    print('4. Display the Year with Most Movies Released\n')
    print('0. Exit')
    print('-' * 44, '\n')


movie_data_list = []

url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"

html = requests.get(url)


soup = BeautifulSoup(html.text, 'html.parser')

table_html = soup.find_all('tbody')[0].find_all('tr')

del table_html[0]   #delete the header


for m in table_html:
    title = m.find('th').find('a').get_text()
    other_data = m.find_all('td')


    movie_obj = Movie(title, other_data[2].get_text(), other_data[3].get_text())
    movie_data_list.append(movie_obj)




#############################################  Database code ###################################

conn = sqlite3.connect('project7.db')

cursor = conn.cursor()


cursor.execute(
    """CREATE TABLE IF NOT EXISTS Movies(
        Title   VarChar(35),
        Gross   INT,
        Year    INT,
        CONSTRAINT MoviePK PRIMARY KEY(Title)
     ) """
)


for m in movie_data_list:
    cursor.execute(
        "INSERT INTO Movies(Title, Gross, Year) VALUES (?, ?, ?)", (m.title, m.gross, m.year)
    )

conn.commit()


################################################## Main Program #############################################


while True:
    printMenu()

    try:
        choice = int(input("Enter your choice: "))


        if choice == 0:
            break
        elif choice == 1:
            try:
                year = int(input("Enter a year: "))

                cursor.execute("SELECT * FROM Movies WHERE Year = ?", (year,))

                results = cursor.fetchall()

                if len(results) == 0:
                    print("No results in", year)
                    continue

                print('Movies released in', year, '(sorted by worldwide gross):')
                for e in enumerate(results):
                    print(f'{e[0] + 1}. {e[1][0]} - ${e[1][1]}')
            except:
                print('Please enter a valid year')


        elif choice == 2:
            cursor.execute("SELECT * FROM Movies WHERE Gross = (SELECT MAX(Gross) FROM Movies)")
            result = cursor.fetchall()

            if len(result) == 0:
                print("Database is empty")
                continue

            print("Highest-Grossing Movie:")
            print(f'{result[0][0]} - ${result[0][1]}')
        

        elif choice == 3:
            cursor.execute("SELECT COUNT(*), SUM(Gross) FROM Movies")
            result = cursor.fetchall()

            if result[0][1] == None:
                print("Database is empty")
                continue

            print(f'The top {result[0][0]} movies have grossed ${result[0][1]} in total')
            

        elif choice == 4:
            cursor.execute("""SELECT Year FROM (SELECT COUNT(*), Year FROM Movies GROUP BY Year ORDER BY COUNT(*) DESC) LIMIT 1""") 
            result = cursor.fetchall()

            if len(result) == 0:
                print("Database is empty")
                continue

            print(f'The year with the most movies in the top 50 was {result[0][0]}')

        else:
            print("Please enter a valid menu input option")

    except ValueError:
        print('Please enter a valid input')



conn.close()

