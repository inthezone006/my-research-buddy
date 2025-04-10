# Research Buddy
v1.0a - Release

Note: *Commit history not available from moving project folders*

### Instructions
1. Install the schema into your DBMS (Tested on MySQL) using the `schema.sql` file.
2. Create the file `config.json` file in the main directory with the following template:
Note: *This may be different based on your DBMS configuration.*
```
{
    "host": "",
    "user": "",
    "password": "",
    "database": "research_buddy"
}
```
3. Create the file `config.py` file in the main directory with the following template:
```
SECRET_KEY = ''
```
4. Create a virtual environment using the `requirements.txt` file.
5. Run `main.py` for the service after ensuring the DBMS is running properly.