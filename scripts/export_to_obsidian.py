#!/usr/bin/env python3
"""
Export Algorithm Data to Obsidian Vault

This script exports algorithm data from the SQLite database to Obsidian notes.
"""

import os
import sys
import sqlite3
import argparse
import subprocess
from datetime import datetime

def get_database_path():
    """Get the path to the SQLite database."""
    # Check environment variable first
    db_path = os.environ.get('DB_PATH')
    if not db_path:
        # Default path relative to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(script_dir)
        db_path = os.path.join(base_dir, 'data', 'algo.db')
    
    return db_path

def get_algorithms(db_path):
    """Get all algorithms from the database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.id, a.name, a.description, av.code
        FROM algorithms a
        JOIN algorithm_versions av ON a.id = av.algorithm_id
        WHERE av.version_number = (
            SELECT MAX(version_number) 
            FROM algorithm_versions 
            WHERE algorithm_id = a.id
        )
    ''')
    
    algorithms = cursor.fetchall()
    conn.close()
    
    return algorithms

def get_algorithm_categories(db_path, algo_id):
    """Get algorithm categories."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.name
        FROM algorithm_categories c
        JOIN algorithm_category_mapping m ON c.id = m.category_id
        WHERE m.algorithm_id = ?
    ''', (algo_id,))
    
    categories = cursor.fetchall()
    conn.close()
    
    return [cat['name'] for cat in categories]

def export_to_markdown(output_dir, algorithms, db_path):
    """Export algorithms to Markdown files."""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    for algo in algorithms:
        algo_id = algo['id']
        name = algo['name']
        description = algo['description'] or 'No description provided.'
        code = algo['code']
        
        # Get categories
        categories = get_algorithm_categories(db_path, algo_id)
        
        # Create tag list
        tags = ['algorithm']
        tags.extend([cat.lower().replace(' ', '-') for cat in categories])
        tags_str = ' '.join([f'#{tag}' for tag in tags])
        
        # Generate filename
        filename = name.replace(' ', '_').lower() + '.md'
        
        print(f"Exporting to file: {filename}")
        
        # Create content
        content = f"""# {name}

Tags: {tags_str}

## Description

{description}

## Implementation

```python
{code}
```

## Complexity Analysis

- Time Complexity: 
- Space Complexity: 

## Examples

"""
        
        # Write to file
        with open(os.path.join(output_dir, filename), 'w') as f:
            f.write(content)
        
        print(f"Successfully exported to file: {filename}")
    
    return os.path.abspath(output_dir)

def open_obsidian(vault_path):
    """Attempt to open Obsidian with the given vault path."""
    try:
        if sys.platform == 'darwin':  # macOS
            subprocess.run(['open', '-a', 'Obsidian', vault_path])
        elif sys.platform == 'win32':  # Windows
            subprocess.run(['start', 'obsidian://open?vault=' + os.path.basename(vault_path)], shell=True)
        else:  # Linux/Unix
            subprocess.run(['xdg-open', 'obsidian://open?vault=' + os.path.basename(vault_path)])
        return True
    except Exception as e:
        print(f"Could not open Obsidian: {str(e)}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Export algorithm data to Obsidian-compatible files.')
    parser.add_argument('--output-dir', default=None, help='Output directory for Markdown files')
    parser.add_argument('--db-path', default=None, help='Path to SQLite database')
    parser.add_argument('--open', action='store_true', help='Attempt to open Obsidian after export')
    
    args = parser.parse_args()
    
    # Get database path
    db_path = args.db_path or get_database_path()
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        sys.exit(1)
    
    print(f"Using database at: {db_path}")
    
    # Get algorithms
    algorithms = get_algorithms(db_path)
    
    if not algorithms:
        print("No algorithms found in the database.")
        sys.exit(0)
    
    print(f"Found {len(algorithms)} algorithms")
    
    # Export to Markdown files
    output_dir = args.output_dir or os.path.join(os.path.dirname(os.path.dirname(db_path)), 'docs')
    print(f"Exporting to Markdown files in: {output_dir}")
    export_path = export_to_markdown(output_dir, algorithms, db_path)
    
    print(f"Export completed successfully to {export_path}")
    
    # Attempt to open Obsidian if requested
    if args.open:
        print("Attempting to open Obsidian...")
        if open_obsidian(export_path):
            print("Obsidian opened successfully.")
        else:
            print("Could not open Obsidian automatically. Please open it manually.")
            print(f"Files have been exported to: {export_path}")

if __name__ == "__main__":
    main()
