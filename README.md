# Password Hashing with Argon2id in Python (for this LMS project)

This document explains how to use Argon2id correctly to hash and verify passwords in Python, with examples and guidance tailored to this Library Management System (Streamlit) project that uses MongoDB for user storage.

Argon2id is a modern, memory-hard password hashing function (PHC winner). It is designed to be slow and memory intensive, which helps protect passwords even if a database is compromised. It automatically handles per-password salts and encodes parameters within the hash string.


## Why Argon2id?
- Memory-hard and slow by design: Thwarts GPU/ASIC brute-force attacks by requiring significant memory and computation.
- Built-in salt and parameters: The hash string encodes the salt and cost parameters; no need to manage salts yourself.
- Tunable parameters: Time cost, memory cost, and parallelism can be tuned for your hardware.
- Recommended by modern guidance: Often the default recommendation alongside scrypt; successor to bcrypt.

Note: bcrypt remains widely used and secure, but this project now uses Argon2id.


## Installation
Install the Argon2 library for Python (argon2-cffi).

- Using pip:
  - Windows: `pip install argon2-cffi`
  - If you use a virtual environment: `python -m venv .venv && .venv\Scripts\activate && pip install argon2-cffi`
- Using Poetry (pyproject): `poetry add argon2-cffi`

If you hit build issues, upgrade pip and wheel: `python -m pip install --upgrade pip wheel`.


## Core Concepts
- Hash: A non-reversible transformation of a password. Do not store plaintext passwords.
- Salt: Random bytes unique per password. Argon2id salts are generated for you and embedded in the hash output.
- Parameters: `time_cost` (iterations), `memory_cost` (KiB), and `parallelism` (threads). Increase these as hardware improves.
- Encoding: Argon2 APIs work with text passwords; the returned hash is a UTF-8 string (e.g., `$argon2id$v=19$m=65536,t=3,p=2$...`). Store it in full.


## Recommended Settings (starting point)
- `time_cost`: 3
- `memory_cost`: 64*1024 (i.e., 65536 KiB = 64 MiB)
- `parallelism`: 2
- Target around 100–500ms per hash on your deployment environment, then tune.

These defaults match the example used in this repo (see lms/argon.py).


## Quick Start (Python)
```python
from argon2 import PasswordHasher

ph = PasswordHasher(time_cost=3, memory_cost=64*1024, parallelism=2)

password = "user_supplied_password"  # from input form

# Hash the password (returns a string like "$argon2id$v=19$m=65536,t=3,p=2$...")
password_hash_str = ph.hash(password)
```

Verification:
```python
entered_password = "user_entry"  # from login form

# Fetch the stored hash from DB
stored_hash_str = user_doc["password"]  # e.g., "$argon2id$v=19$m=65536,t=3,p=2$..."

try:
    if ph.verify(stored_hash_str, entered_password):
        print("Login successful")
    else:
        print("Incorrect password")
except Exception:
    # Includes argon2.exceptions.VerifyMismatchError and other issues
    print("Incorrect password")
```

Note: `ph.verify()` automatically handles the salt and parameters embedded in the stored hash.


## Using Argon2id with MongoDB
Example user schema in MongoDB (document):
```json
{
  "_id": "...",
  "username": "alice",
  "password": "$argon2id$v=19$m=65536,t=3,p=2$...",
  "created_at": "2025-08-01T12:34:56Z",
  "roles": ["librarian"]
}
```

- The `password` field stores the full Argon2id hash string returned by `ph.hash(password)`.
- Index `username` uniquely to prevent duplicates.

Insertion example:
```python
from argon2 import PasswordHasher
from datetime import datetime, timezone

ph = PasswordHasher(time_cost=3, memory_cost=64*1024, parallelism=2)

username = "alice"
plain = "S3curePa$$w0rd"
password_hash = ph.hash(plain)

collection.insert_one({
    "username": username,
    "password": password_hash,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "roles": ["user"]
})
```

Verification example (similar to lms/argon.py):
```python
entered = input("Enter password: ")
stored_hash = collection.find_one({"username": username})["password"]

from argon2.exceptions import VerifyMismatchError
try:
    if ph.verify(stored_hash, entered):
        print("Login successful")
    else:
        print("Incorrect password")
except VerifyMismatchError:
    print("Incorrect password")
```


## Integrating with this project (argon.py)
- This project provides `lms/argon.py`, which uses `argon2.PasswordHasher` to verify a user’s password from MongoDB.
- Ensure that when you create users, you store an Argon2id hash string (not plaintext). For example, when registering a user:

```python
import pymongo as mongo
from argon2 import PasswordHasher

client = mongo.MongoClient("localhost:27017")
db = client["LMS"]
collection = db["users"]

ph = PasswordHasher(time_cost=3, memory_cost=64*1024, parallelism=2)

username = input("New username: ")
password = input("New password: ")

password_hash = ph.hash(password)
collection.insert_one({"username": username, "password": password_hash})
print("User created.")
```

And during login:
```python
user = collection.find_one({"username": username})
if user and ph.verify(user["password"], password):
    print("Login successful")
else:
    print("Incorrect username or password")
```


## Choosing and Tuning Costs
- Benchmark on your deployment hardware and select `time_cost`, `memory_cost`, and `parallelism` so hashing takes around 100–500ms during signup/login.
- Reassess periodically and raise the parameters over time as hardware improves.


## Re-Hashing and Parameter Upgrades
PasswordHasher provides `check_needs_rehash` to help you upgrade parameters over time.

```python
from argon2 import PasswordHasher

ph = PasswordHasher(time_cost=3, memory_cost=64*1024, parallelism=2)

stored_hash_str = user_doc["password"]
if ph.check_needs_rehash(stored_hash_str):
    new_hash = ph.hash(provided_password)
    collection.update_one({"_id": user_doc["_id"]}, {"$set": {"password": new_hash}})
```

Adjust the PasswordHasher initialization to your new target parameters; `check_needs_rehash` will return True when an update is needed.


## Security Best Practices
- Never store plaintext passwords or reversible encryption of passwords.
- Always hash passwords server-side; never trust client-side hashing.
- Use HTTPS everywhere to protect passwords in transit.
- Consider adding a server-side "pepper": a secret stored in configuration, appended before hashing. Example:
  ```python
  import os
  PEPPER = os.environ.get("PASSWORD_PEPPER", "")
  password_hash = ph.hash(password + PEPPER)
  # Verify by appending the same PEPPER before verify
  ```
  Store the pepper in environment variables or a secret manager, not in the database.
- Implement login rate-limiting and account lockouts to slow brute-force attempts.
- Provide a secure password reset flow using time-limited tokens; never email raw passwords.
- Require strong passwords or use passphrases; optionally add zxcvbn-based feedback.
- Log suspicious activity and monitor for excessive failed attempts.


## Handling Unicode and Encoding
- PasswordHasher accepts Python strings and handles encoding internally. If you work with bytes elsewhere, decode to UTF-8 consistently before hashing and verifying.


## Common Mistakes to Avoid
- Storing plaintext passwords.
- Using fast hashes (MD5/SHA-1/SHA-256) instead of password hash functions.
- Truncating the Argon2 hash string. Always store it in full.
- Attempting to manage salts manually. Argon2 handles salts for you.
- Mixing multiple hashing algorithms without a migration plan.


## Troubleshooting
- Install errors on Windows/macOS/Linux: `python -m pip install --upgrade pip wheel` then `pip install argon2-cffi`.
- "Incorrect password" for known-correct password: ensure you stored an Argon2id hash (not plaintext) and are verifying with `PasswordHasher.verify()`.
- Performance concerns: lower `time_cost` or `memory_cost` temporarily and measure; then raise to the highest acceptable values.
- MongoDB type mismatch: store and retrieve the hash as a UTF-8 string.


## FAQ
- Can I decrypt an Argon2id hash? No. It is one-way.
- Should I add my own salt? No. `PasswordHasher.hash()` generates and embeds a salt automatically.
- Is Argon2 better than bcrypt? Argon2id is often recommended today due to its memory hardness; bcrypt remains secure and widely available.
- Can I change the parameters later? Yes. Use `check_needs_rehash` and update hashes on the next successful login.


## References
- argon2-cffi on PyPI: https://pypi.org/project/argon2-cffi/
- OWASP Password Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- NIST Digital Identity Guidelines (SP 800-63): https://pages.nist.gov/800-63-3/


## Appendix: Minimal End-to-End Example (Argon2id)
```python
import pymongo as mongo
from argon2 import PasswordHasher

client = mongo.MongoClient("localhost:27017")
db = client["LMS"]
collection = db["users"]

ph = PasswordHasher(time_cost=3, memory_cost=64*1024, parallelism=2)

# Register
u = input("Username: ")
p = input("Password: ")
hash_str = ph.hash(p)
collection.insert_one({"username": u, "password": hash_str})

# Login
u2 = input("Login username: ")
p2 = input("Login password: ")
user = collection.find_one({"username": u2})
if user and ph.verify(user["password"], p2):
    print("Login successful")
else:
    print("Incorrect username or password")
```
