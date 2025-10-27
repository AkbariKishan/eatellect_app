import os
from dotenv import load_dotenv
from groq import Groq
import traceback

def test_groq_api():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("No GROQ API key found! Please set GROQ_API_KEY in your .env file")
        return
    
    print("API token loaded:", api_key[:4] + "..." if api_key else "None")

    try:
        client = Groq(api_key=api_key)
        
        # Test input
        input_text = """Analyze the health implications of this food product and provide a detailed response.
        
        Product ingredients: Contains sugar, flour, and preservatives.
        
        Respond in the following format:
        
        HEALTH RATING:
        - Rate from 1-10 (1 being least healthy, 10 being most healthy)
        
        NUTRITIONAL BENEFITS:
        - List key nutritional benefits
        
        HEALTH CONCERNS:
        - List potential health concerns
        
        DIETARY CONSIDERATIONS:
        - List dietary considerations (e.g., vegan, contains gluten)
        
        RECOMMENDATIONS:
        - Provide specific consumption recommendations"""
        
        print("\nGenerating response...")
        chat_completion = client.chat.completions.create(
            model="gemma2‑9b‑it",
            messages=[
                {
                    "role": "system",
                    "content": "You are a health and nutrition expert that provides detailed analysis of food products."
                },
                {
                    "role": "user",
                    "content": input_text
                }
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        
        print("\nTest successful!")
        print("\nInput:", input_text)
        print("\nResponse:", chat_completion.choices[0].message.content)
        
    except Exception as e:
        print(f"Error details:")
        traceback.print_exc()

if __name__ == "__main__":
    test_groq_api()