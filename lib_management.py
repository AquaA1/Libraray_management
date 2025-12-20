import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class LibrarySystem:
    def __init__(self, db_file='library_db.json'):
        self.db_file = db_file
        self.load_database()

    def load_database(self):
        """Load or create database"""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                self.db = json.load(f)
        else:
            # Initialize with sample data
            self.db = {
                'students': {
                    'R25EH017': {'name': 'Anish Kumar', 'password': 'pass123'},
                    'R25EH018': {'name': 'Anish Madhav', 'password': 'pass123'},
                    'R25EH032': {'name': 'Chinmay', 'password': 'pass123'},
                    'R25EH052': {'name': 'Edwin John', 'password': 'pass123'},
                },
                'admin': {'username': 'admin', 'password': 'admin123'},
                'books': {
                    'B001': {'title': 'Python Programming', 'genre': 'Technology', 'available': True},
                    'B002': {'title': 'Data Science Handbook', 'genre': 'Technology', 'available': True},
                    'B003': {'title': 'The Great Gatsby', 'genre': 'Fiction', 'available': True},
                    'B004': {'title': '1984', 'genre': 'Fiction', 'available': True},
                    'B005': {'title': 'Sapiens', 'genre': 'History', 'available': True},
                    'B006': {'title': 'Educated', 'genre': 'Biography', 'available': True},
                    'B007': {'title': 'Atomic Habits', 'genre': 'Self-Help', 'available': True},
                    'B008': {'title': 'The Alchemist', 'genre': 'Fiction', 'available': True},
                    'B009': {'title': 'Machine Learning Basics', 'genre': 'Technology', 'available': True},
                    'B010': {'title': 'Brief History of Time', 'genre': 'Science', 'available': True}
                },
                'borrow_history': []
            }
            self.save_database()

    def save_database(self):
        """Save database to JSON"""
        with open(self.db_file, 'w') as f:
            json.dump(self.db, f, indent=4)

    def student_login(self, srn, password):
        """Student login authentication"""
        if srn in self.db['students']:
            if self.db['students'][srn]['password'] == password:
                return True
        return False

    def admin_login(self, username, password):
        """Admin login authentication"""
        return (username == self.db['admin']['username'] and
                password == self.db['admin']['password'])

    def view_available_books(self):
        """Display available books grouped by genre"""
        books_df = pd.DataFrame.from_dict(self.db['books'], orient='index')
        books_df.index.name = 'Book ID'
        available = books_df[books_df['available'] == True]
        return available

    def display_books_by_genre(self, available_only=True):
        """Display books organized by genre"""
        books_df = pd.DataFrame.from_dict(self.db['books'], orient='index')
        books_df['Book Code'] = books_df.index

        if available_only:
            books_df = books_df[books_df['available'] == True]
            print("\n" + "=" * 70)
            print("AVAILABLE BOOKS BY GENRE")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("ALL BOOKS BY GENRE")
            print("=" * 70)

        if books_df.empty:
            print("\nNo books available at the moment.")
            return

        # Group by genre
        genres = books_df['genre'].unique()
        genres = sorted(genres)

        for genre in genres:
            genre_books = books_df[books_df['genre'] == genre]
            print(f"\n📚 {genre.upper()}")
            print("-" * 70)

            for idx, row in genre_books.iterrows():
                status = "✓ Available" if row['available'] else "✗ Borrowed"
                print(f"  [{idx}] {row['title']:<40} {status}")

        print("\n" + "=" * 70)

    def borrow_book(self, srn, book_id):
        """Borrow a book"""
        if book_id not in self.db['books']:
            return "Book not found!"

        if not self.db['books'][book_id]['available']:
            return "Book is currently unavailable!"

        # Update book availability
        self.db['books'][book_id]['available'] = False

        # Add to borrow history
        borrow_record = {
            'srn': srn,
            'student_name': self.db['students'][srn]['name'],
            'book_id': book_id,
            'book_title': self.db['books'][book_id]['title'],
            'genre': self.db['books'][book_id]['genre'],
            'borrow_date': datetime.now().strftime('%Y-%m-%d'),
            'return_date': None,
            'duration': None
        }
        self.db['borrow_history'].append(borrow_record)
        self.save_database()

        return f"Successfully borrowed '{self.db['books'][book_id]['title']}'"

    def return_book(self, srn, book_id):
        """Return a book"""
        # Find the active borrow record
        for record in reversed(self.db['borrow_history']):
            if (record['srn'] == srn and
                    record['book_id'] == book_id and
                    record['return_date'] is None):
                # Update return information
                record['return_date'] = datetime.now().strftime('%Y-%m-%d')
                borrow_date = datetime.strptime(record['borrow_date'], '%Y-%m-%d')
                return_date = datetime.strptime(record['return_date'], '%Y-%m-%d')
                record['duration'] = (return_date - borrow_date).days

                # Make book available again
                self.db['books'][book_id]['available'] = True
                self.save_database()

                return f"Successfully returned '{self.db['books'][book_id]['title']}'"

        return "No active borrow record found for this book!"

    def student_history(self, srn):
        """Get borrowing history for a student"""
        history = [record for record in self.db['borrow_history']
                   if record['srn'] == srn]
        if history:
            return pd.DataFrame(history)
        return pd.DataFrame()

    def get_borrow_df(self):
        """Get borrow history as DataFrame"""
        if self.db['borrow_history']:
            df = pd.DataFrame(self.db['borrow_history'])
            df['borrow_date'] = pd.to_datetime(df['borrow_date'])
            df['month'] = df['borrow_date'].dt.to_period('M').astype(str)
            return df
        return pd.DataFrame()


class AdminAnalytics:
    def __init__(self, library_system):
        self.lib = library_system
        self.df = self.lib.get_borrow_df()

    def genre_analysis(self):
        """Visualize borrowing by genre"""
        if self.df.empty:
            print("No borrowing data available!")
            return

        plt.figure(figsize=(10, 6))
        genre_counts = self.df['genre'].value_counts()

        sns.barplot(x=genre_counts.values, y=genre_counts.index, palette='viridis')
        plt.title('Books Borrowed by Genre', fontsize=16, fontweight='bold')
        plt.xlabel('Number of Borrows', fontsize=12)
        plt.ylabel('Genre', fontsize=12)
        plt.tight_layout()
        plt.show()

    def most_borrowed_books(self, top_n=10):
        """Visualize most borrowed books"""
        if self.df.empty:
            print("No borrowing data available!")
            return

        plt.figure(figsize=(12, 6))
        book_counts = self.df['book_title'].value_counts().head(top_n)

        sns.barplot(x=book_counts.values, y=book_counts.index, palette='rocket')
        plt.title(f'Top {top_n} Most Borrowed Books', fontsize=16, fontweight='bold')
        plt.xlabel('Number of Borrows', fontsize=12)
        plt.ylabel('Book Title', fontsize=12)
        plt.tight_layout()
        plt.show()

    def borrowing_frequency(self):
        """Visualize borrowing frequency over time"""
        if self.df.empty:
            print("No borrowing data available!")
            return

        plt.figure(figsize=(12, 6))
        daily_borrows = self.df.groupby('borrow_date').size()

        plt.plot(daily_borrows.index, daily_borrows.values, marker='o', linewidth=2)
        plt.title('Borrowing Frequency Over Time', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Number of Books Borrowed', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    def student_book_matrix(self):
        """Show which student borrowed which books"""
        if self.df.empty:
            print("No borrowing data available!")
            return

        # Create pivot table
        pivot = self.df.pivot_table(
            index='student_name',
            columns='book_title',
            aggfunc='size',
            fill_value=0
        )

        plt.figure(figsize=(14, 8))
        sns.heatmap(pivot, annot=True, fmt='d', cmap='YlOrRd', cbar_kws={'label': 'Times Borrowed'})
        plt.title('Student-Book Borrowing Matrix', fontsize=16, fontweight='bold')
        plt.xlabel('Book Title', fontsize=12)
        plt.ylabel('Student Name', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

    def monthly_trends(self):
        """Analyze monthly borrowing trends"""
        if self.df.empty:
            print("No borrowing data available!")
            return

        plt.figure(figsize=(12, 6))
        monthly_borrows = self.df.groupby('month').size()

        sns.barplot(x=monthly_borrows.index, y=monthly_borrows.values, palette='mako')
        plt.title('Monthly Borrowing Trends', fontsize=16, fontweight='bold')
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Number of Books Borrowed', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def student_ranking(self):
        """Rank students by borrowing activity"""
        if self.df.empty:
            print("No borrowing data available!")
            return

        plt.figure(figsize=(10, 6))
        student_counts = self.df['student_name'].value_counts()

        colors = sns.color_palette('coolwarm', len(student_counts))
        sns.barplot(x=student_counts.values, y=student_counts.index, palette=colors)
        plt.title('Student Borrowing Ranking', fontsize=16, fontweight='bold')
        plt.xlabel('Books Borrowed', fontsize=12)
        plt.ylabel('Student Name', fontsize=12)

        # Add ranking numbers
        for i, v in enumerate(student_counts.values):
            plt.text(v + 0.1, i, f'#{i + 1}', va='center', fontweight='bold')

        plt.tight_layout()
        plt.show()

    def popular_genres_pie(self):
        """Show genre popularity as pie chart"""
        if self.df.empty:
            print("No borrowing data available!")
            return

        plt.figure(figsize=(10, 8))
        genre_counts = self.df['genre'].value_counts()

        colors = sns.color_palette('Set3', len(genre_counts))
        plt.pie(genre_counts.values, labels=genre_counts.index, autopct='%1.1f%%',
                colors=colors, startangle=90)
        plt.title('Most Popular Genres', fontsize=16, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()
        plt.show()

    def duration_analysis(self):
        """Analyze average borrowing duration"""
        completed = self.df[self.df['duration'].notna()]

        if completed.empty:
            print("No completed borrows with duration data!")
            return

        plt.figure(figsize=(12, 6))
        avg_duration = completed.groupby('book_title')['duration'].mean().sort_values(ascending=False)

        sns.barplot(x=avg_duration.values, y=avg_duration.index, palette='viridis')
        plt.title('Average Borrowing Duration by Book', fontsize=16, fontweight='bold')
        plt.xlabel('Average Days Borrowed', fontsize=12)
        plt.ylabel('Book Title', fontsize=12)
        plt.tight_layout()
        plt.show()

    def comprehensive_dashboard(self):
        """Display all analytics"""
        print("\n" + "=" * 50)
        print("ADMIN ANALYTICS DASHBOARD")
        print("=" * 50 + "\n")

        print("1. Genre Analysis")
        self.genre_analysis()

        print("\n2. Most Borrowed Books")
        self.most_borrowed_books()

        print("\n3. Borrowing Frequency")
        self.borrowing_frequency()

        print("\n4. Student-Book Matrix")
        self.student_book_matrix()

        print("\n5. Monthly Trends")
        self.monthly_trends()

        print("\n6. Student Ranking")
        self.student_ranking()

        print("\n7. Popular Genres")
        self.popular_genres_pie()

        print("\n8. Duration Analysis")
        self.duration_analysis()


def student_menu(lib, srn):
    """Student interface"""
    while True:
        print("\n" + "=" * 40)
        print(f"STUDENT MENU - {lib.db['students'][srn]['name']}")
        print("=" * 40)
        print("1. View Available Books (by Genre)")
        print("2. Borrow Book")
        print("3. Return Book")
        print("4. View My Borrowing History")
        print("5. Logout")

        choice = input("\nEnter choice: ")

        if choice == '1':
            lib.display_books_by_genre(available_only=True)

        elif choice == '2':
            book_id = input("Enter Book ID to borrow: ").upper()
            result = lib.borrow_book(srn, book_id)
            print(result)

        elif choice == '3':
            book_id = input("Enter Book ID to return: ").upper()
            result = lib.return_book(srn, book_id)
            print(result)

        elif choice == '4':
            history = lib.student_history(srn)
            if not history.empty:
                print("\n--- Your Borrowing History ---")
                print(history.to_string())
            else:
                print("No borrowing history found!")

        elif choice == '5':
            print("Logging out...")
            break


def admin_menu(lib):
    """Admin interface"""
    analytics = AdminAnalytics(lib)

    while True:
        print("\n" + "=" * 40)
        print("ADMIN MENU")
        print("=" * 40)
        print("1. View All Books (by Genre)")
        print("2. Genre Analysis")
        print("3. Most Borrowed Books")
        print("4. Borrowing Frequency")
        print("5. Logout")

        choice = input("\nEnter choice: ")

        if choice == '1':
            lib.display_books_by_genre(available_only=False)

        elif choice == '2':
            analytics.genre_analysis()

        elif choice == '3':
            analytics.most_borrowed_books()

        elif choice == '4':
            analytics.borrowing_frequency()

        elif choice == '5':
            print("Logging out...")
            break


def main():
    """Main program"""
    lib = LibrarySystem()

    while True:
        print("\n" + "=" * 40)
        print("LIBRARY MANAGEMENT SYSTEM")
        print("=" * 40)
        print("1. Student Login")
        print("2. Admin Login")
        print("3. Exit")

        choice = input("\nEnter choice: ")

        if choice == '1':
            srn = input("Enter SRN: ").upper()
            password = input("Enter Password: ")

            if lib.student_login(srn, password):
                print(f"\nWelcome, {lib.db['students'][srn]['name']}!")
                student_menu(lib, srn)
            else:
                print("Invalid credentials!")

        elif choice == '2':
            username = input("Enter Admin Username: ")
            password = input("Enter Admin Password: ")

            if lib.admin_login(username, password):
                print("\nAdmin access granted!")
                admin_menu(lib)
            else:
                print("Invalid credentials!")

        elif choice == '3':
            print("Thank you for using the Library System!")
            break


if __name__ == "__main__":
    main()