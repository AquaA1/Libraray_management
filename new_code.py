import json, os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

sns.set_style("whitegrid")

# ---------------- LIBRARY SYSTEM ---------------- #
class LibrarySystem:
    def __init__(self, db='library_db.json'):
        self.db_file = db
        self.load()

    def load(self):
        if os.path.exists(self.db_file):
            self.db = json.load(open(self.db_file))
        else:
            self.db = {
                "students": {
                    "SRN001": {"name": "Alice", "password": "123"},
                    "SRN002": {"name": "Bob", "password": "123"}
                },
                "admin": {"username": "admin", "password": "admin"},
                "books": {
                    "B001": {"title": "Python", "genre": "Tech", "available": True},
                    "B002": {"title": "1984", "genre": "Fiction", "available": True},
                    "B003": {"title": "Sapiens", "genre": "History", "available": True}
                },
                "history": []
            }
            self.save()

    def save(self):
        json.dump(self.db, open(self.db_file, "w"), indent=2)

    def student_login(self, srn, pwd):
        return srn in self.db["students"] and self.db["students"][srn]["password"] == pwd

    def admin_login(self, u, p):
        return u == self.db["admin"]["username"] and p == self.db["admin"]["password"]

    def show_books(self, only_available=True):
        for k, v in self.db["books"].items():
            if not only_available or v["available"]:
                print(f"{k} | {v['title']} | {v['genre']} | {'Yes' if v['available'] else 'No'}")

    def borrow(self, srn, bid):
        if bid not in self.db["books"] or not self.db["books"][bid]["available"]:
            return "Book unavailable"
        self.db["books"][bid]["available"] = False
        self.db["history"].append({
            "srn": srn,
            "student": self.db["students"][srn]["name"],
            "book": self.db["books"][bid]["title"],
            "genre": self.db["books"][bid]["genre"],
            "date": datetime.now().strftime("%Y-%m-%d")
        })
        self.save()
        return "Book borrowed"

    def get_history(self):
        return pd.DataFrame(self.db["history"])

# ---------------- ANALYTICS ---------------- #
class AdminAnalytics:
    def __init__(self, lib):
        self.df = lib.get_history()

    def genre_analysis(self):
        if self.df.empty: return
        sns.countplot(y=self.df["genre"])
        plt.title("Borrowed Books by Genre")
        plt.show()

    def top_books(self):
        if self.df.empty: return
        sns.countplot(y=self.df["book"], order=self.df["book"].value_counts().index)
        plt.title("Most Borrowed Books")
        plt.show()

# ---------------- MENUS ---------------- #
def student_menu(lib, srn):
    while True:
        print("\n1.View 2.Borrow 3.Logout")
        c = input("Choice: ")
        if c == "1": lib.show_books()
        elif c == "2":
            print(lib.borrow(srn, input("Book ID: ").upper()))
        else: break

def admin_menu(lib):
    a = AdminAnalytics(lib)
    while True:
        print("\n1.View Books 2.Genre Analysis 3.Top Books 4.Logout")
        c = input("Choice: ")
        if c == "1": lib.show_books(False)
        elif c == "2": a.genre_analysis()
        elif c == "3": a.top_books()
        else: break

# ---------------- MAIN ---------------- #
def main():
    lib = LibrarySystem()
    while True:
        print("\n1.Student 2.Admin 3.Exit")
        c = input("Choice: ")
        if c == "1":
            srn = input("SRN: ").upper()
            pwd = input("Password: ")
            if lib.student_login(srn, pwd): student_menu(lib, srn)
            else: print("Invalid login")
        elif c == "2":
            if lib.admin_login(input("User: "), input("Pass: ")):
                admin_menu(lib)
            else: print("Invalid login")
        else: break

if __name__ == "__main__":
    main()