#!/usr/bin/env python3
"""
Algorithm Performance Tester

This script tests the performance of algorithms stored in the SQLite database.
It measures execution time and memory usage for different input sizes.
"""

import sqlite3
import time
import os
import sys
import random
import tracemalloc
import json
from datetime import datetime
import re
import traceback
import inspect

def get_algorithm_code(conn, algorithm_id, version_id=None):
    """
    Retrieve algorithm code from the database.
    
    Args:
        conn: SQLite connection
        algorithm_id: ID of the algorithm
        version_id: Specific version ID (if None, gets the latest version)
        
    Returns:
        Tuple containing (version_id, code)
    """
    cursor = conn.cursor()
    
    if version_id is None:
        cursor.execute("""
            SELECT id, code FROM algorithm_versions 
            WHERE algorithm_id = ? 
            ORDER BY version_number DESC LIMIT 1
        """, (algorithm_id,))
    else:
        cursor.execute("""
            SELECT id, code FROM algorithm_versions 
            WHERE algorithm_id = ? AND id = ?
        """, (algorithm_id, version_id))
        
    result = cursor.fetchone()
    
    if not result:
        raise ValueError(f"No algorithm found with ID {algorithm_id} and version {version_id}")
        
    return result

def generate_test_data(size, data_type="int", sorted=False, nearly_sorted=False):
    """
    Generate test data for algorithm testing.
    
    Args:
        size: Size of the data to generate
        data_type: Type of data ('int', 'float', 'str')
        sorted: Whether the data should be sorted
        nearly_sorted: Whether the data should be nearly sorted (90% sorted)
        
    Returns:
        List of generated data
    """
    if data_type == "int":
        data = [random.randint(0, size * 10) for _ in range(size)]
    elif data_type == "float":
        data = [random.random() * size for _ in range(size)]
    elif data_type == "str":
        data = [chr(random.randint(97, 122)) * random.randint(1, 5) for _ in range(size)]
    else:
        raise ValueError(f"Unsupported data type: {data_type}")
        
    if sorted:
        data.sort()
    elif nearly_sorted:
        data.sort()
        swaps = int(size * 0.1)  # Swap 10% of elements
        for _ in range(swaps):
            i, j = random.sample(range(size), 2)
            data[i], data[j] = data[j], data[i]
            
    return data

def find_main_function(namespace, algorithm_name):
    """
    Find the main function in the algorithm code.
    
    Args:
        namespace: Dictionary containing the algorithm functions
        algorithm_name: Name of the algorithm (for heuristic matching)
        
    Returns:
        The main function object
    """
    # List of potential function name patterns by algorithm type
    name_patterns = {
        "Bubble Sort": [r'bubble_sort', r'.*sort'],
        "Quick Sort": [r'quick_sort', r'.*sort'],
        "Merge Sort": [r'merge_sort', r'.*sort'],
        "Binary Search": [r'binary_search', r'.*search'],
        "default": [r'.*sort', r'.*search', r'.*find']
    }
    
    # Get patterns for this algorithm or use default patterns
    patterns = name_patterns.get(algorithm_name, name_patterns["default"])
    
    # Filter functions from the namespace
    functions = [(name, obj) for name, obj in namespace.items() 
                if callable(obj) and name not in globals()]
    
    if not functions:
        raise ValueError("No functions found in the algorithm code")
    
    # Try to match by name patterns
    for pattern in patterns:
        for name, func in functions:
            if re.match(pattern, name, re.IGNORECASE):
                return func
    
    # If no match, filter for functions that take a single argument
    single_param_funcs = []
    for name, func in functions:
        try:
            sig = inspect.signature(func)
            if len(sig.parameters) == 1:
                single_param_funcs.append((name, func))
        except:
            pass
    
    if single_param_funcs:
        # Use the first function with a single parameter
        return single_param_funcs[0][1]
    
    # Last resort: return the first function
    return functions[0][1]

def test_algorithm(code, test_data, algorithm_name, iterations=3):
    """
    Test an algorithm with the given test data.
    
    Args:
        code: Algorithm code as string
        test_data: Data to test the algorithm with
        algorithm_name: Name of the algorithm (for function detection)
        iterations: Number of iterations to run for averaging
        
    Returns:
        Dict containing performance metrics
    """
    # Create a namespace for the algorithm
    namespace = {}
    
    # Execute the algorithm code in the namespace
    exec(code, namespace)
    
    # Find the main function
    main_func = find_main_function(namespace, algorithm_name)
    
    # Measure execution time
    total_time = 0
    
    # Measure memory usage
    tracemalloc.start()
    
    for _ in range(iterations):
        # Create a copy of the test data to avoid modification between runs
        test_copy = test_data.copy()
        
        start_time = time.time()
        result = main_func(test_copy)
        end_time = time.time()
        
        total_time += (end_time - start_time) * 1000  # Convert to milliseconds
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    avg_time = total_time / iterations
    
    return {
        "execution_time_ms": avg_time,
        "memory_usage_kb": peak / 1024,  # Convert to KB
        "input_size": len(test_data),
        "platform": sys.platform
    }

def save_results(conn, version_id, metrics):
    """
    Save performance metrics to the database.
    
    Args:
        conn: SQLite connection
        version_id: Algorithm version ID
        metrics: Dict containing performance metrics
    """
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO performance_metrics 
        (version_id, input_size, execution_time_ms, memory_usage_kb, platform) 
        VALUES (?, ?, ?, ?, ?)
    """, (
        version_id,
        metrics["input_size"],
        metrics["execution_time_ms"],
        metrics["memory_usage_kb"],
        metrics["platform"]
    ))
    
    conn.commit()
    return cursor.lastrowid

def main():
    """
    Main function to test algorithms and save performance metrics.
    """
    # Get database path from environment or use default
    db_path = os.environ.get('DB_PATH')
    if not db_path:
        db_path = os.path.expanduser('~/Repositories/ai_workspace/algorithm_platform/data/algo.db')
    
    # Ensure the database directory exists
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        print(f"Creating database directory: {db_dir}")
        os.makedirs(db_dir, exist_ok=True)
    
    print(f"Using database at: {db_path}")
    
    # Connect to the database
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)
    
    # Get available algorithms
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM algorithms")
    algorithms = cursor.fetchall()
    
    print(f"Found {len(algorithms)} algorithms")
    
    # Test each algorithm
    for algo in algorithms:
        algo_id = algo["id"]
        algo_name = algo["name"]
        
        print(f"\nTesting algorithm: {algo_name} (ID: {algo_id})")
        
        # Get the latest version of the algorithm
        version_id, code = get_algorithm_code(conn, algo_id)
        
        print(f"Using version ID: {version_id}")
        
        # Test with smaller sizes to avoid timeouts
        for size in [50, 100, 200]:
            print(f"  Testing with input size: {size}")
            
            # Generate test data
            test_data = generate_test_data(size)
            
            try:
                # Test the algorithm
                metrics = test_algorithm(code, test_data, algo_name)
                
                # Save the results
                result_id = save_results(conn, version_id, metrics)
                
                print(f"  Results saved (ID: {result_id}):")
                print(f"    Execution time: {metrics['execution_time_ms']:.2f} ms")
                print(f"    Memory usage: {metrics['memory_usage_kb']:.2f} KB")
            except Exception as e:
                print(f"  Error testing {algo_name} with input size {size}:")
                print(f"  {str(e)}")
                print(f"  {traceback.format_exc()}")
                print("  Continuing with next test...")
    
    conn.close()
    print("\nTesting completed")

if __name__ == "__main__":
    main()
