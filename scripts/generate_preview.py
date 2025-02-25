#!/usr/bin/env python3
"""
Generate a preview image for the README.

This script creates a simple visual representation of the platform.
"""

import os
import sys
import argparse

try:
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Rectangle
except ImportError:
    print("Error: This script requires matplotlib and numpy.")
    print("Install them with: pip install matplotlib numpy")
    sys.exit(1)

def generate_preview(output_path):
    """Generate a preview image."""
    # Set up the figure
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#f0f0f0')
    
    # Create a data structure to mock algorithm performance
    algorithms = ['Bubble Sort', 'Quick Sort', 'Merge Sort', 'Binary Search']
    
    # Create mock data
    input_sizes = [50, 100, 200, 500, 1000]
    bubble_times = [0.8, 3.2, 12.8, 80.0, 320.0]
    quick_times = [0.4, 0.9, 2.0, 5.0, 12.0]
    merge_times = [0.5, 1.1, 2.4, 6.0, 15.0]
    binary_times = [0.02, 0.03, 0.04, 0.05, 0.06]
    
    # Plot the data
    plt.plot(input_sizes, bubble_times, 'o-', label='Bubble Sort', linewidth=2, markersize=8)
    plt.plot(input_sizes, quick_times, 's-', label='Quick Sort', linewidth=2, markersize=8)
    plt.plot(input_sizes, merge_times, '^-', label='Merge Sort', linewidth=2, markersize=8)
    plt.plot(input_sizes, binary_times, 'D-', label='Binary Search', linewidth=2, markersize=8)
    
    # Add labels and title
    plt.xlabel('Input Size', fontsize=12)
    plt.ylabel('Execution Time (ms)', fontsize=12)
    plt.title('Algorithm Performance Dashboard', fontsize=16)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left', fontsize=10)
    
    # Set logarithmic scale
    plt.xscale('log')
    plt.yscale('log')
    
    # Add a background for the plot
    ax.set_facecolor('#ffffff')
    for spine in ax.spines.values():
        spine.set_edgecolor('#cccccc')
    
    # Add annotations
    plt.annotate('O(n²)', xy=(input_sizes[3], bubble_times[3]), xytext=(input_sizes[3]*1.2, bubble_times[3]*0.8),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8), fontsize=10)
    
    plt.annotate('O(n log n)', xy=(input_sizes[3], quick_times[3]), xytext=(input_sizes[3]*1.2, quick_times[3]*0.8),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8), fontsize=10)
    
    plt.annotate('O(log n)', xy=(input_sizes[3], binary_times[3]), xytext=(input_sizes[3]*1.2, binary_times[3]*0.8),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8), fontsize=10)
    
    # Add a footer
    plt.figtext(0.5, 0.01, 'Algorithm Development and Analysis Platform', 
                ha='center', fontsize=14, fontstyle='italic')
    
    # Save the figure
    plt.tight_layout(pad=2.0)
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    print(f"Preview image saved to: {output_path}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Generate preview image for README.')
    parser.add_argument('--output', default=None, help='Output path for preview image')
    
    args = parser.parse_args()
    
    # Default output path
    if args.output is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(script_dir)
        output_path = os.path.join(base_dir, 'docs', 'preview.png')
    else:
        output_path = args.output
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Generate preview
    generate_preview(output_path)

if __name__ == "__main__":
    main()
