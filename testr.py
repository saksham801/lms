from argon2 import PasswordHasher
ph = PasswordHasher(time_cost=3, memory_cost=64*1024, parallelism=2)
hash1 = ph.hash("123456")
hash2 = ph.hash("123456")

print(hash1 == hash2)