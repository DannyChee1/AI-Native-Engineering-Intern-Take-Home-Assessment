# Legacy monolithic app for user management
users = {}  # In-memory storage (simulating flat file)

def register_user(username, password):
    if username in users:
        return "User already exists"
    users[username] = password  # Plaintext password - insecure!    
    return "User registered"
    
def login_user(username, password):
    if username in users and users[username] == password:
        return "Login successful"
    return "Invalid credentials"
    
def get_user_data(username):
    if username in users:
        return f"User: {username}, Password: {users[username]}"  # Exposes sensitive data    
    return "User not found"

# Simulate running the appprint(register_user("alice", "password123"))
print(login_user("alice", "password123"))
print(get_user_data("alice"))