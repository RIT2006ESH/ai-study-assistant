import google.generativeai as genai

# Your API key
API_KEY = "AIzaSyDm-yuMzyAMT9QkK7-u1G2hH-pvdA9vzxk"
genai.configure(api_key=API_KEY)

print("Available models that support generateContent:")
print("-" * 50)
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model: {m.name}")
            print(f"Display name: {m.display_name}")
            print("-" * 50)
except Exception as e:
    print(f"Error listing models: {e}")
