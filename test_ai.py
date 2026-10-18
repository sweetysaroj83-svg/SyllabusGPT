from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-6-luna",
    input="Say hello to SyllabusGPT in one sentence."
)

print(response.output_text)