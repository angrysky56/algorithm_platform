# Algorithm Development and Analysis Platform

A comprehensive platform for developing, benchmarking, visualizing, and documenting algorithms with SQLite database storage and interactive visualization tools.

![Algorithm Platform Dashboard](docs/preview.png)

## Overview

This platform provides an integrated environment for algorithm development with:

- **Database Storage**: Store algorithms, versions, categories, and performance metrics
- **Performance Testing**: Benchmark algorithms with various input sizes
- **Interactive Visualizations**: Generate interactive charts and reports
- **Documentation Export**: Create documentation compatible with Obsidian or any Markdown editor
- **Docker Support**: Deploy the entire platform in a containerized environment
- **Knowledge Graph**: Map relationships between algorithms and computer science concepts

## Getting Started

### Prerequisites

- Python 3.8+
- SQLite
- Optional: matplotlib, numpy, pandas (for advanced visualizations)
- Optional: Docker and Docker Compose (for containerized deployment)
- Optional: Obsidian (for knowledge management)

### Quick Start

Clone the repository and run the launcher script:

```bash
cd ~/Repositories/ai_workspace/algorithm_platform
./algo_platform.sh
```

Alternatively, use the Python command-line interface:

```bash
# Run performance tests
./run.py test

# Generate visualizations
./run.py visualize

# Start the web dashboard
./run.py dashboard

# Run the entire workflow
./run.py run-all
```

## Project Structure

```
algorithm_platform/
├── data/                  # Database and data files
│   └── algo.db            # SQLite database
├── docs/                  # Documentation
│   └── obsidian_export/   # Markdown files for Obsidian
├── reports/               # Generated reports and visualizations
│   ├── performance_report.html  # HTML report
│   └── performance_metrics.json # JSON metrics
├── scripts/               # Utility scripts
│   ├── init_database.py   # Database initialization
│   └── export_to_obsidian.py # Obsidian export tool
├── src/                   # Source code
│   ├── algorithm_tester.py    # Performance testing
│   └── visualize_performance.py  # Visualization generation
├── .gitignore             # Git ignore file
├── algo_platform.sh       # Interactive launcher script
├── docker-compose.yml     # Docker configuration
├── obsidian_template.md   # Template for Obsidian notes
├── run.py                 # Command-line interface
└── README.md              # This file
```

## Features

### 1. Algorithm Management

The platform manages algorithms with:

- **Versioning**: Track multiple versions of each algorithm
- **Categorization**: Organize algorithms by type (sorting, searching, etc.)
- **Metadata**: Store descriptions, improvements, and feedback

```bash
# Add a new algorithm via the CLI
./run.py add "Selection Sort" "A simple sorting algorithm" selection_sort.py --category 1
```

### 2. Performance Testing

Benchmark algorithms with different input sizes:

- **Automatic testing**: Test all algorithms in the database
- **Metrics collection**: Measure execution time and memory usage
- **Consistent environment**: Run tests in Docker for reproducibility

```bash
# Run performance tests
./run.py test
```

### 3. Visualization

Generate interactive visualizations and reports:

- **Execution time charts**: Compare algorithm performance
- **Memory usage charts**: Analyze memory efficiency
- **Interactive dashboard**: Web-based visualization
- **JSON exports**: Raw data for custom analysis

```bash
# Start the visualization dashboard
./run.py dashboard
```

### 4. Documentation

Export algorithm documentation in various formats:

- **Markdown files**: Compatible with any Markdown editor
- **Obsidian export**: Create formatted notes for Obsidian
- **Documentation generation**: Auto-generate docs from database

```bash
# Export documentation for Obsidian
./run.py export --format obsidian
```

### 5. Docker Deployment

Run the entire platform in Docker:

```bash
# Start the Docker environment
docker-compose up -d
```

The dashboard will be available at http://localhost:8080/

## Included Algorithms

The platform comes with several classic algorithms:

- **Bubble Sort**: Simple comparison-based sorting
- **Quick Sort**: Efficient divide-and-conquer sorting
- **Merge Sort**: Stable divide-and-conquer sorting
- **Binary Search**: Efficient search in sorted arrays

## Development

### Adding New Algorithms

1. Use the interactive menu: `./algo_platform.sh` > Option 7
2. Use the command-line tool: `./run.py add [name] [description] [file] --category [id]`
3. Direct database insertion (see `scripts/init_database.py` for examples)

### Customizing Documentation Templates

Edit the `obsidian_template.md` file to customize the format of exported documentation.

### Database Schema

- `algorithms`: Basic algorithm information
- `algorithm_versions`: Code versions
- `algorithm_categories`: Categories
- `algorithm_category_mapping`: Category relationships
- `performance_metrics`: Performance data
- `improvements`: Version improvements
- `feedback`: User feedback

## Acknowledgements

This platform was developed in collaboration with Claude from Anthropic, demonstrating the power of AI-assisted software development.

## License

This project is available under the MIT License.
