# 🧠 Research Buddy  
**v1.0a – Alpha Release**

> ⚠️ *Note: Commit history unavailable due to project folder restructuring*

---

## 📋 Instructions

1️⃣ **Install the Database Schema**  
📂 Import `schema.sql` into your DBMS (✅ Tested with MySQL).

2️⃣ **Configure Database Access**  
🛠️ Create a `config.json` file in the main directory with the following template:

```json
{
    "host": "",
    "user": "",
    "password": "",
    "database": "research_buddy"
}

```
🔒 Note: Update fields based on your local DBMS credentials.

3️⃣ **Set Your Secret Key**  
🧾 Create a `config.py` file in the main directory with the following content:

```
SECRET_KEY = ''
```
4️⃣ **Set Up Your Environment**  
🐍 Create a virtual environment and install dependencies using:

```
pip install -r requirements.txt
```

5️⃣ **Run the App**  
▶️ Launch the service with:

```
python main.py
```
✅ Make sure your database service (e.g., MySQL in XAMPP) is running.

6️⃣ **Admin Account Setup**  
🛡️ On first startup, create an admin account using status code: `1234`

7️⃣ **Done!**  
🎉 You're all set — welcome to Research Buddy!