import os
import openai
openai.api_key = "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"
FINE_TUNED_MODEL = "curie:ft-personal-2023-01-04-14-53-22"


def completeText(prompt):
    res = openai.Completion.create(
        model=FINE_TUNED_MODEL,
        prompt=prompt,
        max_tokens=50,
        temperature=1)
    return res


print(completeText("what are the access a teacher can have over the student's screen?"))