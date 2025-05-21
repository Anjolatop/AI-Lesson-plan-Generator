import openai
import os
from dotenv import load_dotenv

load_dotenv()  # Loads your .env file if you’re using one

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

models = client.models.list()

for m in models.data:
    print(m.id)