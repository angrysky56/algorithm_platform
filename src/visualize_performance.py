#!/usr/bin/env python3
"""
Algorithm Performance Visualizer

This script creates visualizations for algorithm performance metrics stored in the SQLite database.
"""

import sqlite3
import os
import sys
import json
from datetime import datetime

# Try to import visualization libraries
try:
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib, numpy, or pandas not available. Install with:")
    print("pip install matplotlib numpy pandas")
    print("Only JSON export will be available.")

def get_algorithm_metrics(conn):
    """
    Retrieve performance metrics for all algorithm versions.
    
    Args:
        conn: SQLite connection
        
    Returns:
        DataFrame or list containing performance metrics
    """
    query = """
    SELECT 
        a.id as algorithm_id,
        a.name as algorithm_name,
        av.id as version_id,
        av.version_number,
        pm.input_size,
        pm.execution_time_ms,
        pm.memory_usage_kb
    FROM 
        algorithms a
    JOIN 
        algorithm_versions av ON a.id = av.algorithm_id
    JOIN 
        performance_metrics pm ON av.id = pm.version_id
    ORDER BY
        a.name, av.version_number, pm.input_size
    """
    
    if MATPLOTLIB_AVAILABLE:
        return pd.read_sql_query(query, conn)
    else:
        cursor = conn.cursor()
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

def plot_execution_time(metrics_df, output_dir):
    """
    Plot execution time for all algorithms.
    
    Args:
        metrics_df: DataFrame containing performance metrics
        output_dir: Directory to save plot
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Cannot create plots without matplotlib")
        return
        
    plt.figure(figsize=(12, 10))  # Increased height for better display
    
    # Group by algorithm and version
    for (algo_name, version), group in metrics_df.groupby(['algorithm_name', 'version_number']):
        plt.plot(group['input_size'], group['execution_time_ms'], 
                 marker='o', label=f"{algo_name} v{version}")
    
    plt.xlabel('Input Size')
    plt.ylabel('Execution Time (ms)')
    plt.title('Algorithm Performance: Execution Time')
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left')  # Position legend at upper left to avoid overlap
    plt.xscale('log')
    plt.yscale('log')
    
    # Add more space at the bottom
    plt.subplots_adjust(bottom=0.15)
    
    # Save the plot
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(f"{output_dir}/execution_time.png")
    print(f"Saved execution time plot to {output_dir}/execution_time.png")

def plot_memory_usage(metrics_df, output_dir):
    """
    Plot memory usage for all algorithms.
    
    Args:
        metrics_df: DataFrame containing performance metrics
        output_dir: Directory to save plot
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Cannot create plots without matplotlib")
        return
        
    plt.figure(figsize=(12, 10))  # Increased height for better display
    
    # Group by algorithm and version
    for (algo_name, version), group in metrics_df.groupby(['algorithm_name', 'version_number']):
        plt.plot(group['input_size'], group['memory_usage_kb'], 
                 marker='s', label=f"{algo_name} v{version}")
    
    plt.xlabel('Input Size')
    plt.ylabel('Memory Usage (KB)')
    plt.title('Algorithm Performance: Memory Usage')
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left')  # Position legend at upper left to avoid overlap
    plt.xscale('log')
    
    # Add more space at the bottom
    plt.subplots_adjust(bottom=0.15)
    
    # Save the plot
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(f"{output_dir}/memory_usage.png")
    print(f"Saved memory usage plot to {output_dir}/memory_usage.png")

def generate_performance_report(metrics_df, output_dir):
    """
    Generate a performance report as HTML.
    
    Args:
        metrics_df: DataFrame containing performance metrics
        output_dir: Directory to save report
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Cannot create HTML report without pandas")
        return
        
    # Create a pivot table for easy comparison
    pivot_time = metrics_df.pivot_table(
        index=['algorithm_name', 'version_number'],
        columns='input_size',
        values='execution_time_ms',
        aggfunc='mean'
    )
    
    pivot_memory = metrics_df.pivot_table(
        index=['algorithm_name', 'version_number'],
        columns='input_size',
        values='memory_usage_kb',
        aggfunc='mean'
    )
    
    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Algorithm Performance Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2 {{ color: #333; }}
            table {{ border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
            th {{ background-color: #f2f2f2; }}
            .header {{ background-color: #4CAF50; color: white; }}
            img {{ max-width: 100%; height: auto; margin-bottom: 40px; }} /* Added margin for charts */
            .chart-container {{ margin-bottom: 60px; }} /* Added container with margin */
        </style>
    </head>
    <body>
        <h1>Algorithm Performance Report</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Execution Time (ms)</h2>
        {pivot_time.to_html()}
        
        <h2>Memory Usage (KB)</h2>
        {pivot_memory.to_html()}
        
        <h2>Performance Charts</h2>
        <div class="chart-container">
            <h3>Execution Time</h3>
            <img src="execution_time.png" alt="Execution Time Chart">
        </div>
        
        <div class="chart-container">
            <h3>Memory Usage</h3>
            <img src="memory_usage.png" alt="Memory Usage Chart">
        </div>
    </body>
    </html>
    """
    
    # Save the HTML report
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/performance_report.html", "w") as f:
        f.write(html)
    
    print(f"Saved performance report to {output_dir}/performance_report.html")

def generate_simple_html_report(metrics, output_dir):
    """
    Generate a simple HTML report without matplotlib dependencies.
    
    Args:
        metrics: List of dictionaries containing performance metrics
        output_dir: Directory to save report
    """
    # Group metrics by algorithm and version
    grouped_metrics = {}
    for metric in metrics:
        algo_key = (metric['algorithm_name'], metric['version_number'])
        if algo_key not in grouped_metrics:
            grouped_metrics[algo_key] = []
        grouped_metrics[algo_key].append(metric)
    
    # Generate HTML table rows for execution time
    time_rows = ""
    for (algo_name, version), metrics_list in sorted(grouped_metrics.items()):
        # Sort by input size
        metrics_list = sorted(metrics_list, key=lambda x: x['input_size'])
        
        row = f"<tr><td>{algo_name} v{version}</td>"
        for metric in metrics_list:
            row += f"<td>{metric['execution_time_ms']:.2f}</td>"
        row += "</tr>"
        time_rows += row
    
    # Generate HTML table rows for memory usage
    memory_rows = ""
    for (algo_name, version), metrics_list in sorted(grouped_metrics.items()):
        # Sort by input size
        metrics_list = sorted(metrics_list, key=lambda x: x['input_size'])
        
        row = f"<tr><td>{algo_name} v{version}</td>"
        for metric in metrics_list:
            row += f"<td>{metric['memory_usage_kb']:.2f}</td>"
        row += "</tr>"
        memory_rows += row
    
    # Get unique input sizes for table headers
    input_sizes = sorted(list(set(metric['input_size'] for metric in metrics)))
    
    # Generate header row
    header_row = "<tr><th>Algorithm</th>"
    for size in input_sizes:
        header_row += f"<th>{size}</th>"
    header_row += "</tr>"
    
    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Algorithm Performance Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2 {{ color: #333; }}
            table {{ border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
            th {{ background-color: #f2f2f2; }}
            .header {{ background-color: #4CAF50; color: white; }}
        </style>
    </head>
    <body>
        <h1>Algorithm Performance Report</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Execution Time (ms)</h2>
        <table>
            <thead>
                {header_row}
            </thead>
            <tbody>
                {time_rows}
            </tbody>
        </table>
        
        <h2>Memory Usage (KB)</h2>
        <table>
            <thead>
                {header_row}
            </thead>
            <tbody>
                {memory_rows}
            </tbody>
        </table>
        
        <p>Note: Install matplotlib, numpy, and pandas for graphical visualizations.</p>
    </body>
    </html>
    """
    
    # Save the HTML report
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/performance_report.html", "w") as f:
        f.write(html)
    
    print(f"Saved simple performance report to {output_dir}/performance_report.html")

def export_to_json(metrics, output_dir):
    """
    Export metrics to JSON format.
    
    Args:
        metrics: DataFrame or list containing performance metrics
        output_dir: Directory to save JSON
    """
    if MATPLOTLIB_AVAILABLE and isinstance(metrics, pd.DataFrame):
        # Convert DataFrame to list of dictionaries
        json_data = metrics.to_dict(orient='records')
    else:
        # Already a list of dictionaries
        json_data = metrics
    
    # Save the JSON file
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/performance_metrics.json", "w") as f:
        json.dump(json_data, f, indent=2)
    
    print(f"Saved metrics to {output_dir}/performance_metrics.json")

def main():
    """
    Main function to visualize algorithm performance.
    """
    # Get database path from environment or use default
    db_path = os.environ.get('DB_PATH')
    if not db_path:
        db_path = os.path.expanduser('~/Repositories/ai_workspace/algorithm_platform/data/algo.db')
    
    print(f"Using database at: {db_path}")
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        sys.exit(1)
    
    # Get output directory from environment or use default
    output_dir = os.environ.get('OUTPUT_DIR')
    if not output_dir:
        output_dir = os.path.expanduser("~/Repositories/ai_workspace/algorithm_platform/reports")
    
    print(f"Saving reports to: {output_dir}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Connect to the database
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)
    
    # Get performance metrics
    metrics = get_algorithm_metrics(conn)
    
    # Generate visualizations and reports
    if MATPLOTLIB_AVAILABLE:
        plot_execution_time(metrics, output_dir)
        plot_memory_usage(metrics, output_dir)
        generate_performance_report(metrics, output_dir)
    else:
        generate_simple_html_report(metrics, output_dir)
    
    # Export to JSON (works with or without matplotlib)
    export_to_json(metrics, output_dir)
    
    conn.close()
    print("\nVisualization completed")

if __name__ == "__main__":
    main()
