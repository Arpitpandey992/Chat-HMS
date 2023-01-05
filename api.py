from flask import Flask, request, abort
from dotenv import load_dotenv
import os
import openai

app = Flask(__name__)
app.debug = True


def configure():
    load_dotenv()


openai.api_key = os.getenv('api_key')
fineTunedModel = os.getenv('FINE_TUNED_MODEL')


def completeText(prompt):
    res = openai.Completion.create(
        model=fineTunedModel,
        prompt=prompt,
        max_tokens=50,
        temperature=1)
    return res


@app.route('/api/query', methods=['POST'])
def autocomplete():
    data = request.get_json()
    if not data or "prompt" not in data:
        abort(400, "Couldn't find 'prompt' in the request")
    prompt = data["prompt"]
    res = completeText(prompt)
    print(res)
    outputText = res["choices"][0]["text"]
    return {"result": outputText}


def main():
    configure()
    app.run()


main()
