#step1:setup GROQ API key
import os
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

#step2:convet image to required format
import base64


def encode_image(image_path):
    #image_path = "acne.jpg"
    image_file = open(image_path, "rb")
    return base64.b64encode(image_file.read()).decode('utf-8')
    
#step3: send multimodal LLM()
from groq import Groq

query="is there acne on this face? if yes, what is the severity of acne? if no, please say no acne"
model="meta-llama/llama-4-scout-17b-16e-instruct"

def analyze_image_with_query(query,model, encoded_image):
    client=Groq(api_key=GROQ_API_KEY)

    messages=[
        {
            "role":"user",
            "content":[
             {
                  "type":"text",
                  "text":query
              },
             {
                 "type":"image_url",
                    "image_url":{
                        "url":f"data:image/jpeg;base64,{encoded_image}",
                    },
                },
            ],
            }
    ]
    chat_completion = client.chat.completions.create(
        model=model,
        messages=messages,
    
    )
    return (chat_completion.choices[0].message.content)
# Create a Groq client
