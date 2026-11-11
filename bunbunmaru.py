import ollama

response = ollama.chat(
    model="bunbunmaru",
    format="json",
    messages=[
        {
            "role": "user",
            "content": "Break this story right now!",
            "images": ["./blahaj.jpg"],
        }
    ],
)
print(response["message"]["content"])
