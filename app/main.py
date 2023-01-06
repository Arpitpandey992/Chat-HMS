from flask import Flask, request, abort
from dotenv import load_dotenv
import os
import openai
import subprocess


def createApp(testing: bool = True):
    # Initialization
    app = Flask(__name__)
    load_dotenv()
    openai.api_key = os.getenv('api_key')
    fineTunedModel = os.getenv('FINE_TUNED_MODEL')

    ADD_PREFIX = True
    PREFIX = "In 100ms, "
    PREFIX_TEST = "100ms"
    SUFFIX = "\n\n###\n\n"
    
    def completeText(prompt):
        # removing invalid characters from the end, this could be much more efficient
        invalidSuffix = ["\n", " "]

        while (prompt[-1] in invalidSuffix):
            prompt = prompt[0:-1]

        # adding a prefix (use only if it was used during training as well)
        if ADD_PREFIX and PREFIX_TEST not in prompt:
            cleanPrompt = PREFIX + prompt + SUFFIX
        else:
            cleanPrompt = prompt + SUFFIX
        print("prompt = "+repr(cleanPrompt))

        # deterministic model, gives good results for similar questions as present in FAQ:
        res = openai.Completion.create(
            model=fineTunedModel,
            prompt=cleanPrompt,
            max_tokens=200,
            temperature=0.00,
            presence_penalty=0.0,
            frequency_penalty=2.0,
            stop=[" END"]
        )

        # stochastic model, takes more risk, but still gives similar results as deterministic model when questions are similar to training data
        # res = openai.Completion.create(
        #     model=fineTunedModel,
        #     prompt=cleanPrompt,
        #     max_tokens=200,
        #     temperature=0.7,
        #     presence_penalty=1.0,
        #     frequency_penalty=1.0,
        #     stop=[" END"]
        # )
        return res

    # Routes :
    @app.route('/api/query', methods=['POST'])
    def autocomplete():
        data = request.get_json()
        if not data or "prompt" not in data:
            abort(400, "Couldn't find 'prompt' in the request")
        prompt = data["prompt"]
        res = completeText(prompt)
        outputText = res["choices"][0]["text"]
        return {"reply": outputText}

    # Not Working for now
    # @app.route('/api/fine-tune', methods=['POST'])
    # def fineTune():
    #     data = request.get_json()
    #     if not data or "prompt" not in data or not "completion" in data:
    #         abort(400, "Please provide a 'prompt' and 'completion'")
    #     prompt = data["prompt"]+"\n\n###\n\n"
    #     completion = data["completion"]+" END"
    #     pathTOJSONL = ''
    #     result = subprocess.run([
    #         'openai', 'api', 'fine_tunes.create', '-t', pathTOJSONL, '-m', fineTunedModel
    #     ], stdout=subprocess.PIPE)
    #     print(result.stdout.decode())
    #     return {"Status": "OK"}

    return app
