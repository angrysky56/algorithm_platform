#!/usr/bin/env python3
"""
Algorithm Platform Command Line Helper

A simpler command-line alternative to the full shell launcher.
"""

import os
import sys
import subprocess
import argparse
import sqlite3

# Configure paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
SRC_DIR = os.path.join(BASE_DIR, 'src')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')
DB_PATH = os.path.join(DATA_DIR, 'algo.db')

def ensure_database():
    """Ensure the database exists and is initialized."""
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Initializing...")
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        subprocess.run([sys.executable, os.path.join(SCRIPTS_DIR, 'init_database.py')])
    return True

def run_tests():
    """Run algorithm performance tests."""
    ensure_database()
    print("Running algorithm performance tests...")
    subprocess.run([sys.executable, os.path.join(SRC_DIR, 'algorithm_tester.py')])

def visualize():
    """Generate visualizations."""
    ensure_database()
    print("Generating visualizations...")
    subprocess.run([sys.executable, os.path.join(SRC_DIR, 'visualize_performance.py')])

def start_dashboard(port=8080):
    """Start the web dashboard."""
    ensure_database()
    
    # Check if reports directory exists
    if not os.path.exists(REPORTS_DIR):
        print("Reports directory not found. Running visualization first...")
        visualize()
    
    # Check if performance metrics exist
    if not os.path.exists(os.path.join(REPORTS_DIR, 'performance_metrics.json')):
        print("No performance metrics found. Running visualization first...")
        visualize()
    
    print(f"Starting dashboard on http://localhost:{port}/")
    print("Press Ctrl+C to stop")
    
    try:
        os.chdir(REPORTS_DIR)
        subprocess.run([sys.executable, '-m', 'http.server', str(port)])
    except KeyboardInterrupt:
        print("\nDashboard stopped")

def run_docker():
    """Run Docker deployment."""
    print("Starting Docker containers...")
    subprocess.run(['docker-compose', 'up', '-d'], cwd=BASE_DIR)
    print("Docker containers started. Dashboard available at http://localhost:8080/")
    print("Run 'docker-compose down' to stop the containers")

def clean_database():
    """Clean the database."""
    ensure_database()
    
    print("Cleaning database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Find duplicate algorithms
    cursor.execute('''
        SELECT name, COUNT(*) as count 
        FROM algorithms 
        GROUP BY name 
        HAVING count > 1
    ''')
    
    duplicates = cursor.fetchall()
    print(f"Found {len(duplicates)} duplicate algorithm types.")
    
    # Delete duplicate algorithms
    for name, count in duplicates:
        print(f"Processing duplicates for: {name}")
        
        # Get all versions of this algorithm
        cursor.execute('SELECT id FROM algorithms WHERE name = ? ORDER BY id', (name,))
        algo_ids = [row[0] for row in cursor.fetchall()]
        
        # Keep the first one, delete the rest
        keep_id = algo_ids[0]
        delete_ids = algo_ids[1:]
        
        print(f"  Keeping algorithm ID: {keep_id}")
        print(f"  Deleting algorithm IDs: {delete_ids}")
        
        # Delete related records for the duplicate algorithms
        for delete_id in delete_ids:
            # Get version IDs for this algorithm
            cursor.execute('SELECT id FROM algorithm_versions WHERE algorithm_id = ?', (delete_id,))
            version_ids = [row[0] for row in cursor.fetchall()]
            
            # Delete performance metrics for these versions
            for version_id in version_ids:
                cursor.execute('DELETE FROM performance_metrics WHERE version_id = ?', (version_id,))
                print(f"    Deleted performance metrics for version ID: {version_id}")
            
            # Delete versions
            cursor.execute('DELETE FROM algorithm_versions WHERE algorithm_id = ?', (delete_id,))
            print(f"    Deleted versions for algorithm ID: {delete_id}")
            
            # Delete improvements and feedback
            cursor.execute('DELETE FROM improvements WHERE algorithm_id = ?', (delete_id,))
            cursor.execute('DELETE FROM feedback WHERE algorithm_id = ?', (delete_id,))
            
            # Delete category mappings
            cursor.execute('DELETE FROM algorithm_category_mapping WHERE algorithm_id = ?', (delete_id,))
            
            # Finally delete the algorithm
            cursor.execute('DELETE FROM algorithms WHERE id = ?', (delete_id,))
            print(f"    Deleted algorithm ID: {delete_id}")
    
    # Commit the changes
    conn.commit()
    conn.close()
    print("Database cleaned successfully")

def list_algorithms():
    """List all algorithms in the database."""
    ensure_database()
    
    print("Algorithms in the database:")
    print("--------------------------")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.id, a.name, COUNT(av.id) as versions, 
               (SELECT COUNT(*) FROM performance_metrics pm 
                JOIN algorithm_versions av2 ON pm.version_id = av2.id 
                WHERE av2.algorithm_id = a.id) as metrics
        FROM algorithms a
        LEFT JOIN algorithm_versions av ON a.id = av.algorithm_id
        GROUP BY a.id
        ORDER BY a.name
    ''')
    
    algorithms = cursor.fetchall()
    
    if not algorithms:
        print("No algorithms found")
    else:
        print(f"{'ID':<4} {'Name':<20} {'Versions':<10} {'Metrics':<10}")
        print("-" * 50)
        for algo in algorithms:
            algo_id, name, versions, metrics = algo
            print(f"{algo_id:<4} {name:<20} {versions:<10} {metrics:<10}")
    
    conn.close()

def add_algorithm(name, description, code, category_id=1):
    """Add a new algorithm to the database."""
    ensure_database()
    
    print(f"Adding algorithm: {name}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Insert algorithm
    cursor.execute('INSERT INTO algorithms (name, description) VALUES (?, ?)', (name, description))
    algo_id = cursor.lastrowid
    
    # Insert algorithm version
    cursor.execute('INSERT INTO algorithm_versions (algorithm_id, version_number, code) VALUES (?, ?, ?)', 
                  (algo_id, 1, code))
    
    # Map algorithm to category
    cursor.execute('INSERT INTO algorithm_category_mapping (algorithm_id, category_id) VALUES (?, ?)', 
                  (algo_id, category_id))
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"Algorithm added successfully with ID: {algo_id}")

def run_all():
    """Run the complete workflow: test, visualize, dashboard."""
    ensure_database()
    run_tests()
    visualize()
    start_dashboard()

def export_algorithms(format='markdown', output_dir=None):
    """Export algorithms to the specified format."""
    ensure_database()
    
    if format == 'obsidian':
        print("Exporting algorithms for Obsidian...")
        script_path = os.path.join(SCRIPTS_DIR, 'export_to_obsidian.py')
        cmd = [sys.executable, script_path]
        
        if output_dir:
            cmd.extend(['--output-dir', output_dir])
        
        subprocess.run(cmd)
    else:
        print(f"Exporting algorithms to {format} format...")
        script_path = os.path.join(SCRIPTS_DIR, 'export_to_obsidian.py')
        cmd = [sys.executable, script_path]
        
        if output_dir:
            cmd.extend(['--output-dir', output_dir])
        
        subprocess.run(cmd)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Algorithm Platform Command Line Helper')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # init command
    init_parser = subparsers.add_parser('init', help='Initialize the database')
    
    # test command
    test_parser = subparsers.add_parser('test', help='Run algorithm performance tests')
    
    # visualize command
    viz_parser = subparsers.add_parser('visualize', help='Generate visualizations')
    
    # dashboard command
    dash_parser = subparsers.add_parser('dashboard', help='Start the web dashboard')
    dash_parser.add_argument('-p', '--port', type=int, default=8080, help='Port to run the dashboard on')
    
    # docker command
    docker_parser = subparsers.add_parser('docker', help='Run Docker deployment')
    
    # clean command
    clean_parser = subparsers.add_parser('clean', help='Clean the database')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List all algorithms')
    
    # add command
    add_parser = subparsers.add_parser('add', help='Add a new algorithm')
    add_parser.add_argument('name', help='Algorithm name')
    add_parser.add_argument('description', help='Algorithm description')
    add_parser.add_argument('file', help='File containing the algorithm code')
    add_parser.add_argument('-c', '--category', type=int, default=1, help='Category ID')
    
    # export command
    export_parser = subparsers.add_parser('export', help='Export algorithms to different formats')
    export_parser.add_argument('--format', choices=['markdown', 'obsidian'], default='markdown', help='Export format')
    export_parser.add_argument('--output-dir', help='Output directory for exported files')
    
    # run-all command
    run_all_parser = subparsers.add_parser('run-all', help='Run the complete workflow: test, visualize, dashboard')
    
    args = parser.parse_args()
    
    # Execute the command
    if args.command == 'init':
        ensure_database()
        print("Database initialized successfully")
    elif args.command == 'test':
        run_tests()
    elif args.command == 'visualize':
        visualize()
    elif args.command == 'dashboard':
        start_dashboard(args.port)
    elif args.command == 'docker':
        run_docker()
    elif args.command == 'clean':
        clean_database()
    elif args.command == 'list':
        list_algorithms()
    elif args.command == 'add':
        with open(args.file, 'r') as f:
            code = f.read()
        add_algorithm(args.name, args.description, code, args.category)
    elif args.command == 'export':
        export_algorithms(args.format, args.output_dir)
    elif args.command == 'run-all':
        run_all()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
