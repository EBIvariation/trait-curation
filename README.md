# trait-curation
A web application for manual curation of trait-to-ontology mappings, including provenance and integration with EBI SPOT stack.

## How to run
1. Navigate to the project directory
2. `python3 -m venv venv` - Creates a virtual environment 
3. `. venv/bin/activate` - Activates the virtual environment
4. `pip3 install -r requirements.txt` - Installs the required dependencies in the virtual environment
5. `python3 manage.py migrate` - Installs the app's database migrations
6. `python3 manage.py runserver` - Starts a development server
