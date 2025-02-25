#!/usr/bin/env python3
"""
Initialize the algorithm database.

This script creates the database schema and populates it with initial data.
"""

import os
import sqlite3
from datetime import datetime
import sys

def create_database(db_path):
    """Create the database and tables."""
    # Make sure the directory exists
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        print(f"Creating directory: {db_dir}")
        os.makedirs(db_dir, exist_ok=True)
    
    # Connect to the database (will create it if it doesn't exist)
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS algorithms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS algorithm_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        algorithm_id INTEGER NOT NULL,
        version_number INTEGER NOT NULL,
        code TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (algorithm_id) REFERENCES algorithms(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS improvements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        algorithm_id INTEGER NOT NULL,
        old_version_id INTEGER NOT NULL,
        new_version_id INTEGER NOT NULL,
        improvement_note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (algorithm_id) REFERENCES algorithms(id),
        FOREIGN KEY (old_version_id) REFERENCES algorithm_versions(id),
        FOREIGN KEY (new_version_id) REFERENCES algorithm_versions(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        algorithm_id INTEGER NOT NULL,
        version_id INTEGER NOT NULL,
        feedback_text TEXT NOT NULL,
        rating INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (algorithm_id) REFERENCES algorithms(id),
        FOREIGN KEY (version_id) REFERENCES algorithm_versions(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS algorithm_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS algorithm_category_mapping (
        algorithm_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        PRIMARY KEY (algorithm_id, category_id),
        FOREIGN KEY (algorithm_id) REFERENCES algorithms(id),
        FOREIGN KEY (category_id) REFERENCES algorithm_categories(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS performance_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        version_id INTEGER NOT NULL,
        input_size INTEGER NOT NULL,
        execution_time_ms REAL NOT NULL,
        memory_usage_kb REAL,
        platform TEXT,
        test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (version_id) REFERENCES algorithm_versions(id)
    )
    ''')
    
    # Commit the changes
    conn.commit()
    print(f"Database created successfully at {db_path}")
    return conn

def populate_initial_data(conn):
    """Populate the database with initial data."""
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute('SELECT COUNT(*) FROM algorithms')
    count = cursor.fetchone()[0]
    
    if count > 0:
        print("Database already contains data. Skipping initial data population.")
        return
    
    # Add algorithms
    algorithms = [
        ('Bubble Sort', 'A simple sorting algorithm'),
        ('Quick Sort', 'A divide-and-conquer sorting algorithm with O(n log n) average time complexity'),
        ('Merge Sort', 'A stable, divide-and-conquer sorting algorithm with guaranteed O(n log n) time complexity'),
        ('Binary Search', 'An efficient search algorithm for finding elements in a sorted array')
    ]
    
    for algo in algorithms:
        cursor.execute('INSERT INTO algorithms (name, description) VALUES (?, ?)', algo)
    
    # Get the algorithm IDs
    cursor.execute('SELECT id, name FROM algorithms')
    algo_ids = {name: id for id, name in cursor.fetchall()}
    
    # Add algorithm versions
    versions = [
        (algo_ids['Bubble Sort'], 1, '''def bubble_sort(arr): 
    n = len(arr) 
    for i in range(n): 
        for j in range(0, n-i-1): 
            if arr[j] > arr[j+1]: 
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr'''),
        
        (algo_ids['Bubble Sort'], 2, '''def optimized_bubble_sort(arr): 
    n = len(arr) 
    swapped = True
    while swapped: 
        swapped = False
        for i in range(n-1): 
            if arr[i] > arr[i+1]: 
                arr[i], arr[i+1] = arr[i+1], arr[i]
                swapped = True
    return arr'''),
        
        (algo_ids['Quick Sort'], 1, '''def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)'''),
        
        (algo_ids['Merge Sort'], 1, '''def merge_sort(arr):
    """
    Merge sort implementation. Sorts array in ascending order.
    
    Args:
        arr: Input array to sort
        
    Returns:
        Sorted array
    """
    if len(arr) <= 1:
        return arr
    
    # Split array in half
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    # Merge the sorted halves
    return _merge(left, right)

def _merge(left, right):
    """Helper function for merge sort"""
    result = []
    i = j = 0
    
    # Compare elements from both arrays and add smaller one to result
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    # Add remaining elements
    result.extend(left[i:])
    result.extend(right[j:])
    return result'''),
        
        (algo_ids['Binary Search'], 1, '''def binary_search(arr):
    """
    Binary search implementation that finds an element in a sorted array.
    For testing purposes, it searches for a value that is guaranteed to exist.
    
    Args:
        arr: List of elements to search in
        
    Returns:
        Index of the found element or -1 if the array is empty
    """
    # First sort the array (just in case)
    arr = sorted(arr)
    
    if not arr:
        return -1
    
    # Choose a target that definitely exists in the array
    target = arr[len(arr) // 2]
    
    # Perform binary search
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
            
    return -1  # Should never reach here since target is guaranteed to exist
''')
    ]
    
    for version in versions:
        cursor.execute('INSERT INTO algorithm_versions (algorithm_id, version_number, code) VALUES (?, ?, ?)', version)
    
    # Get the version IDs
    cursor.execute('SELECT id, algorithm_id, version_number FROM algorithm_versions')
    version_info = cursor.fetchall()
    version_ids = {}
    for id, algo_id, version_num in version_info:
        if algo_id not in version_ids:
            version_ids[algo_id] = {}
        version_ids[algo_id][version_num] = id
    
    # Add improvements
    improvements = [
        (algo_ids['Bubble Sort'], 
         version_ids[algo_ids['Bubble Sort']][1], 
         version_ids[algo_ids['Bubble Sort']][2], 
         'Added a swapped flag to optimize iterations.')
    ]
    
    for imp in improvements:
        cursor.execute('INSERT INTO improvements (algorithm_id, old_version_id, new_version_id, improvement_note) VALUES (?, ?, ?, ?)', imp)
    
    # Add feedback
    feedback = [
        (algo_ids['Bubble Sort'], 
         version_ids[algo_ids['Bubble Sort']][2], 
         'The optimized version avoids unnecessary iterations, improving efficiency.', 
         5)
    ]
    
    for fb in feedback:
        cursor.execute('INSERT INTO feedback (algorithm_id, version_id, feedback_text, rating) VALUES (?, ?, ?, ?)', fb)
    
    # Add categories
    categories = [
        ('Sorting', 'Algorithms for arranging elements in a specific order'),
        ('Searching', 'Algorithms for finding elements in data structures'),
        ('Graph', 'Algorithms for operating on graph data structures'),
        ('Dynamic Programming', 'Algorithms that solve complex problems by breaking them into simpler subproblems')
    ]
    
    for cat in categories:
        cursor.execute('INSERT INTO algorithm_categories (name, description) VALUES (?, ?)', cat)
    
    # Get the category IDs
    cursor.execute('SELECT id, name FROM algorithm_categories')
    cat_ids = {name: id for id, name in cursor.fetchall()}
    
    # Map algorithms to categories
    mappings = [
        (algo_ids['Bubble Sort'], cat_ids['Sorting']),
        (algo_ids['Quick Sort'], cat_ids['Sorting']),
        (algo_ids['Merge Sort'], cat_ids['Sorting']),
        (algo_ids['Binary Search'], cat_ids['Searching'])
    ]
    
    for mapping in mappings:
        cursor.execute('INSERT INTO algorithm_category_mapping (algorithm_id, category_id) VALUES (?, ?)', mapping)
    
    # Commit the changes
    conn.commit()
    print("Initial data populated successfully")

def main():
    """Main function."""
    # Get database path from environment or use default
    db_path = os.environ.get('DB_PATH')
    if not db_path:
        # This path is relative to the repository, making it work both in Claude app and locally
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'algo.db')
    
    print(f"Using database path: {db_path}")
    
    # Create the database and tables
    conn = create_database(db_path)
    
    # Populate initial data
    populate_initial_data(conn)
    
    # Close the connection
    conn.close()
    print("Database initialization completed")

if __name__ == "__main__":
    main()
