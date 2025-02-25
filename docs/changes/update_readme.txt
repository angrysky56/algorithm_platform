Added an export command to the run.py script:
bashCopy./run.py export --format obsidian --output-dir docs/obsidian_export

Created a setup.sh script that:

Creates necessary directories
Installs Python dependencies
Initializes the database
Generates a preview image
Makes scripts executable


Created a script to generate a preview image for the README

These changes make the platform more user-friendly, easier to set up, and improve its documentation. The Obsidian integration now works through export/import rather than direct API integration, which is more reliable and works across different environments.
To use the updated platform, users can simply:

Run ./setup.sh to set up everything
Run ./algo_platform.sh for the menu interface, or
Use ./run.py for command-line access
