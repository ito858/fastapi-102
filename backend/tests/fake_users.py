# generate_fake_users.py
from faker import Faker
import json

fake = Faker()

# Generate 20 fake user profiles
users = []
for _ in range(20):
    user = {
        "username": fake.user_name(),
        "password": fake.password(length=10),  # Simple password for testing
        "vip": {
            "code": f"VIP{fake.random_number(digits=10, fix_len=True)}",  # VIP + 10-digit number (13 chars total)
            "nascita": fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%Y-%m-%d"),
            "cellulare": fake.phone_number(),
            "sms": fake.boolean(),
            "Punti": fake.random_int(min=0, max=1000),
            "Sconto": fake.random_int(min=0, max=50),
            "Nome": fake.first_name(),
            "cognome": fake.last_name(),
            "Email": fake.email(),
            "Indirizzo": fake.street_address(),
            "Citta": fake.city(),
            "Prov": fake.state_abbr(),
            "Cap": fake.postcode(),
            "CodiceFiscale": fake.ssn(),  # Using SSN as a proxy for CodiceFiscale
        }
    }
    users.append(user)

# Save to JSON file
with open("fake_users.json", "w") as f:
    json.dump(users, f, indent=4)

print("Generated 20 fake user profiles in 'fake_users.json'")
