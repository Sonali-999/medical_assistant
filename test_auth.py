from auth import register_user, login_user, save_user_chat, get_user_chats

# Test signup
print("Signup:", register_user("test@example.com", "123456"))

# Test login
print("Login:", login_user("test@example.com", "123456"))

# Test saving chats
save_user_chat(1, "Hello Doctor", "Hi, how are you?")
print("Chats:", get_user_chats(1))
