#!/bin/bash

# Algorithm Development and Analysis Platform Launcher

# Set up colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Base directory
BASE_DIR="/home/ty/Repositories/ai_workspace/algorithm_platform"
DATA_DIR="$BASE_DIR/data"
SRC_DIR="$BASE_DIR/src"
REPORTS_DIR="$BASE_DIR/reports"
SCRIPTS_DIR="$BASE_DIR/scripts"
DOCS_DIR="$BASE_DIR/docs"

# Function to display header
display_header() {
    clear
    echo -e "${BLUE}=== Algorithm Development and Analysis Platform ===${NC}"
    echo -e "${BLUE}=================================================${NC}"
    echo
}

# Function to check if database exists
check_database() {
    if [ ! -f "$DATA_DIR/algo.db" ]; then
        echo -e "${YELLOW}Database not found! Initializing database...${NC}"
        python "$SCRIPTS_DIR/init_database.py"
        if [ $? -ne 0 ]; then
            echo -e "${RED}Database initialization failed!${NC}"
            return 1
        fi
        echo -e "${GREEN}Database initialized successfully!${NC}"
    else
        echo -e "${GREEN}Database found at $DATA_DIR/algo.db${NC}"
    fi
    return 0
}

# Function to check Python dependencies
check_dependencies() {
    echo -e "${BLUE}Checking Python dependencies...${NC}"
    
    # List of required packages
    PACKAGES=("matplotlib" "numpy" "pandas")
    MISSING=()
    
    for pkg in "${PACKAGES[@]}"; do
        if python -c "import $pkg" &>/dev/null; then
            echo -e "${GREEN}✓ $pkg is installed${NC}"
        else
            echo -e "${YELLOW}✗ $pkg is not installed${NC}"
            MISSING+=("$pkg")
        fi
    done
    
    if [ ${#MISSING[@]} -gt 0 ]; then
        echo -e "${YELLOW}Some packages are missing. Would you like to install them? (y/n)${NC}"
        read -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}Installing missing packages...${NC}"
            pip install "${MISSING[@]}"
            if [ $? -ne 0 ]; then
                echo -e "${RED}Package installation failed. Some features may not work.${NC}"
                return 1
            fi
            echo -e "${GREEN}Packages installed successfully!${NC}"
        else
            echo -e "${YELLOW}Proceeding without installing packages. Some features may not work.${NC}"
        fi
    fi
    
    return 0
}

# Function to run algorithm tests
run_tests() {
    echo -e "${BLUE}Running algorithm performance tests...${NC}"
    python "$SRC_DIR/algorithm_tester.py"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Tests failed!${NC}"
        return 1
    fi
    echo -e "${GREEN}Tests completed successfully!${NC}"
    return 0
}

# Function to generate visualizations
generate_visualizations() {
    echo -e "${BLUE}Generating performance visualizations...${NC}"
    python "$SRC_DIR/visualize_performance.py"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Visualization generation failed!${NC}"
        return 1
    fi
    echo -e "${GREEN}Visualizations created successfully!${NC}"
    return 0
}

# Function to start web dashboard
start_dashboard() {
    echo -e "${BLUE}Starting web dashboard...${NC}"
    
    # Check if reports directory exists
    if [ ! -d "$REPORTS_DIR" ]; then
        echo -e "${RED}Reports directory not found!${NC}"
        echo -e "${YELLOW}Run the visualizations first.${NC}"
        return 1
    fi
    
    # Check if there are reports in the directory
    if [ ! -f "$REPORTS_DIR/performance_metrics.json" ]; then
        echo -e "${RED}No performance metrics found!${NC}"
        echo -e "${YELLOW}Run the visualizations first.${NC}"
        return 1
    fi
    
    # Check if the server is already running
    if pgrep -f "python -m http.server 8080" > /dev/null; then
        echo -e "${YELLOW}Server is already running!${NC}"
        echo -e "${GREEN}Dashboard available at http://localhost:8080/${NC}"
    else
        # Start the server
        echo -e "${GREEN}Starting HTTP server...${NC}"
        cd "$REPORTS_DIR"
        python -m http.server 8080 &>/dev/null &
        SERVER_PID=$!
        cd - > /dev/null
        
        echo -e "${GREEN}Dashboard available at http://localhost:8080/${NC}"
        echo -e "${YELLOW}Press Enter to stop the server${NC}"
        read
        
        # Stop the server
        kill $SERVER_PID 2>/dev/null
        echo -e "${GREEN}Server stopped.${NC}"
    fi
    
    return 0
}

# Function to run Docker setup
run_docker() {
    echo -e "${BLUE}Setting up Docker environment...${NC}"
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is not installed!${NC}"
        echo -e "${YELLOW}Please install Docker and Docker Compose.${NC}"
        return 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Docker Compose is not installed!${NC}"
        echo -e "${YELLOW}Please install Docker Compose.${NC}"
        return 1
    fi
    
    # Run Docker Compose
    echo -e "${GREEN}Starting Docker containers...${NC}"
    cd "$BASE_DIR"
    docker-compose up -d
    if [ $? -ne 0 ]; then
        echo -e "${RED}Docker Compose failed!${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Docker containers started successfully!${NC}"
    echo -e "${GREEN}Dashboard available at http://localhost:8080/${NC}"
    echo -e "${YELLOW}Run 'docker-compose down' to stop the containers.${NC}"
    
    return 0
}

# Function to export algorithms for Obsidian
export_for_obsidian() {
    echo -e "${BLUE}Exporting algorithms for Obsidian...${NC}"
    
    # Run the Python script to export algorithms
    python "$SCRIPTS_DIR/export_to_obsidian.py" --output-dir "$DOCS_DIR/obsidian_export"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Export failed!${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Algorithms exported successfully!${NC}"
    echo -e "${YELLOW}Files have been exported to: $DOCS_DIR/obsidian_export${NC}"
    echo -e "${YELLOW}You can now import these files into Obsidian.${NC}"
    
    # Ask if user wants to open the directory
    echo -e "${YELLOW}Would you like to open the export directory now? (y/n)${NC}"
    read -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Attempt to open the directory
        if command -v xdg-open &> /dev/null; then
            xdg-open "$DOCS_DIR/obsidian_export"
        elif command -v open &> /dev/null; then
            open "$DOCS_DIR/obsidian_export"
        elif command -v explorer &> /dev/null; then
            explorer "$DOCS_DIR/obsidian_export"
        else
            echo -e "${RED}Could not open directory. Please navigate to:${NC}"
            echo -e "${YELLOW}$DOCS_DIR/obsidian_export${NC}"
        fi
    fi
    
    return 0
}

# Function to create documentation files locally
create_documentation() {
    echo -e "${BLUE}Creating documentation for algorithms...${NC}"
    
    # Get algorithms from database
    python -c "
import sqlite3
import os
from datetime import datetime

# Paths
db_path = '$DATA_DIR/algo.db'
docs_dir = '$DOCS_DIR'
template_path = '$BASE_DIR/obsidian_template.md'

# Ensure docs directory exists
os.makedirs(docs_dir, exist_ok=True)

# Check if template exists
if not os.path.exists(template_path):
    # Create default template
    with open(template_path, 'w') as f:
        f.write('''# \${algo_name}

Tags: #algorithm

## Description

\${algo_desc}

## Implementation

```python
\${algo_code}
```

## Complexity Analysis

- Time Complexity: 
- Space Complexity: 

## Examples

''')
    print(f'Created template at {template_path}')

# Read template
with open(template_path, 'r') as f:
    template = f.read()

# Database connection
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get algorithms
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

# Generate documentation
for algo in algorithms:
    algo_id, name, description, code = algo
    # Generate filename
    filename = name.replace(' ', '_').lower() + '.md'
    
    # Fill template
    content = template.replace('\${algo_name}', name)
    content = content.replace('\${algo_desc}', description or 'No description provided.')
    content = content.replace('\${algo_code}', code)
    
    # Write to file
    with open(os.path.join(docs_dir, filename), 'w') as f:
        f.write(content)
    
    print(f'Created documentation for: {name}')
"
    
    echo -e "${GREEN}Documentation created in $DOCS_DIR${NC}"
    return 0
}

# Function to add new algorithm
add_algorithm() {
    echo -e "${BLUE}Adding a new algorithm to the database...${NC}"
    
    # Get algorithm details
    echo -e "${YELLOW}Please enter the algorithm details:${NC}"
    echo -n "Name: "
    read algo_name
    echo -n "Description: "
    read algo_desc
    
    # Choose category
    echo -e "${YELLOW}Available categories:${NC}"
    python - << EOF
import sqlite3
import os

db_path = os.path.expanduser('$DATA_DIR/algo.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('SELECT id, name FROM algorithm_categories')
categories = cursor.fetchall()

for id, name in categories:
    print(f"{id}: {name}")

conn.close()
EOF
    
    echo -n "Category ID: "
    read category_id
    
    # Get algorithm code
    echo -e "${YELLOW}Enter the algorithm code (end with 'EOF' on a new line):${NC}"
    algo_code=""
    while IFS= read -r line; do
        if [ "$line" == "EOF" ]; then
            break
        fi
        algo_code="$algo_code$line
"
    done
    
    # Insert into database
    python - << EOF
import sqlite3
import os

db_path = os.path.expanduser('$DATA_DIR/algo.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insert algorithm
cursor.execute('INSERT INTO algorithms (name, description) VALUES (?, ?)', ('$algo_name', '$algo_desc'))
algo_id = cursor.lastrowid

# Insert algorithm version
cursor.execute('INSERT INTO algorithm_versions (algorithm_id, version_number, code) VALUES (?, ?, ?)', (algo_id, 1, """$algo_code"""))

# Map algorithm to category
cursor.execute('INSERT INTO algorithm_category_mapping (algorithm_id, category_id) VALUES (?, ?)', (algo_id, $category_id))

# Commit changes
conn.commit()
conn.close()

print("Algorithm added successfully!")
EOF
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to add algorithm!${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Algorithm added successfully!${NC}"
    return 0
}

# Function to clean database
clean_database() {
    echo -e "${BLUE}Cleaning database...${NC}"
    echo -e "${YELLOW}This will delete duplicate algorithms and performance metrics.${NC}"
    echo -e "${RED}WARNING: This operation cannot be undone!${NC}"
    echo -n "Are you sure you want to continue? (y/n): "
    read -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Operation cancelled.${NC}"
        return 0
    fi
    
    # Clean the database
    python - << EOF
import sqlite3
import os

db_path = os.path.expanduser('$DATA_DIR/algo.db')
conn = sqlite3.connect(db_path)
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

# Commit changes
conn.commit()
print("Database cleaned successfully!")
conn.close()
EOF
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to clean database!${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Database cleaned successfully!${NC}"
    return 0
}

# Main menu function
show_menu() {
    display_header
    echo -e "${BLUE}Main Menu${NC}"
    echo -e "1. Run algorithm performance tests"
    echo -e "2. Generate performance visualizations"
    echo -e "3. Start web dashboard"
    echo -e "4. Deploy with Docker Compose"
    echo -e "5. Export for Obsidian"
    echo -e "6. Create documentation files"
    echo -e "7. Add new algorithm"
    echo -e "8. Clean database (remove duplicates)"
    echo -e "9. Exit"
    echo
    echo -n "Enter your choice [1-9]: "
}

# Main loop
while true; do
    # Check database on first run
    if [ ! -v DATABASE_CHECKED ]; then
        check_database
        DATABASE_CHECKED=true
    fi
    
    show_menu
    read choice
    
    case $choice in
        1)
            check_dependencies
            run_tests
            echo -e "${YELLOW}Press Enter to continue...${NC}"
            read
            ;;
        2)
            check_dependencies
            generate_visualizations
            echo -e "${YELLOW}Press Enter to continue...${NC}"
            read
            ;;
        3)
            start_dashboard
            ;;
        4)
            run_docker
            echo -e "${YELLOW}Press Enter to continue...${NC}"
            read
            ;;
        5)
            export_for_obsidian
            echo -e "${YELLOW}Press Enter to continue...${NC}"
            read
            ;;
        6)
            create_documentation
            echo -e "${YELLOW}Press Enter to continue...${NC}"
            read
            ;;
        7)
            add_algorithm
            echo -e "${YELLOW}Press Enter to continue...${NC}"
            read
            ;;
        8)
            clean_database
            echo -e "${YELLOW}Press Enter to continue...${NC}"
            read
            ;;
        9)
            echo -e "${GREEN}Exiting. Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please try again.${NC}"
            echo -e "${YELLOW}Press Enter to continue...${NC}"
            read
            ;;
    esac
done
