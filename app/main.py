from flask import Flask, request, abort
from dotenv import load_dotenv
import os
import openai
import re
# import subprocess


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

    # Helper Functions :
    def cleanInputText(prompt):
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
        return cleanPrompt

    def parseURL(URL, basePath):
        if URL.startswith("http"):
            return URL
        # manually forming the new path, this can probably be done using some internal module as well.
        basePathParts = basePath.split("/")
        relPathParts = URL.split("/")
        if relPathParts[0] == "":
            relPathParts = relPathParts[1:]
        absPathParts = []
        for part in relPathParts:
            if part == "..":
                basePathParts.pop()
            elif part == ".":
                continue
            else:
                absPathParts.append(part)
        newURL = "/".join(basePathParts + absPathParts)
        return newURL

    def cleanOutputText(inputString):
        #mainly fixing the URLs in hyperlinks, if they are in relative format.
        pattern = r'\[(.*?)\]\(([^\]\)]*)\)'
        basePath = "https://www.100ms.live/docs/javascript/v2"
        matches = re.finditer(pattern, inputString)

        newString = inputString
        indexDiff = 0  # to account for the the string size differences as we are changing the string
        for m in matches:
            name = m.group(1)
            URL = m.group(2)
            print(name, URL)
            newURL = parseURL(URL, basePath)
            start = m.start() + indexDiff
            end = m.end() + indexDiff
            newString = newString[:start] + \
                f'[{name}]({newURL})' + newString[end:]
            indexDiff += len(f'[{name}]({newURL})') - (end - start)

        return newString

    def completeText(prompt):
        cleanPrompt = cleanInputText(prompt)

        # deterministic model, gives good results for similar questions as present in FAQ:
        # res = openai.Completion.create(
        #     model=fineTunedModel,
        #     prompt=cleanPrompt,
        #     max_tokens=200,
        #     temperature=0.00,
        #     presence_penalty=0.0,
        #     frequency_penalty=2.0,
        #     stop=[" END"]
        # )

        # stochastic model, takes more risk, but still gives similar results as deterministic model when questions are similar to training data
        res = openai.Completion.create(
            model=fineTunedModel,
            prompt=cleanPrompt,
            max_tokens=200,
            temperature=0.5,
            presence_penalty=1.0,
            frequency_penalty=1.0,
            stop=[" END"]
        )
        return res

    # Routes :
    @app.route('/api/query', methods=['POST'])
    def query():
        data = request.get_json()
        if not data or "prompt" not in data:
            abort(400, "Couldn't find 'prompt' in the request")
        prompt = data["prompt"]
        # We can do some more cleaning and checkning before calling the API
        res = completeText(prompt)
        outputText = res["choices"][0]["text"]
        return {"reply": cleanOutputText(outputText)}

    # Not Working for now
    @app.route('/api/fine-tune', methods=['POST'])
    def fineTune():
        data = request.get_json()
        if not data or "prompt" not in data or not "completion" in data:
            abort(400, "Please provide a 'prompt' and 'completion'")
        prompt = data["prompt"]+"\n\n###\n\n"
        completion = data["completion"]+" END"
        # pathTOJSONL = ''
        # result = subprocess.run([
        #     'openai', 'api', 'fine_tunes.create', '-t', pathTOJSONL, '-m', fineTunedModel
        # ], stdout=subprocess.PIPE)
        # print(result.stdout.decode())
        # we can use this to sort of train the existing model but that will be very inefficient and probably not worth it as well.
        # training should be done with multiple examples at once instead.
        return {"Status": "Work in progress..."}

    return app
