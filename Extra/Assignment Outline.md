# Assignment Outline
## Exploring the OpenAI API
* I started with checking the capabilities of the GPT-3 API, by writing random prompts and checking the results. It initially had zero knowledge regarding 100ms.
* After playing with it for some time, i made a rough roadmap about how i would proceed with the assignment. I decided to do the things in the following order:
  * Create an initial testing model by parsing the data from `FAQ.md` and check how much it is able to learn about 100ms from that.
  * Then, build the required API and host it. I did this early on because i was not familiar with building APIs in python, so i thought of getting it done beforehand, so i could focus on improving the model if needed.
  * Setting up everything -> testing and improving the model.

## Parsing the FAQ and Training the First Model
* I started by downloading the `faq.md` file and looking for patterns within it. After removing the uneccesary bits (like the intro, table of contents), the file had information like:
```
## Section 1
### Question 1 (Single Line)
Answer 1 (Can Span Multiple Lines)
### Question 2
Answer 2
...
##Section 2
...
```
* Then, i checked the OpenAI API documentation for fine-tuning. The required input was in .jsonl in the format:
    * {"prompt":"", "completion":""}
    * {"prompt":"", "completion":""}

* So, i built a jupyter notebook to read the markdown file and extract the information in Question and answer format. To get the data in a .jsonl file, i used `jsonlines` library.
* After getting the final file, it is required to manually use OpenAI's data preparation tool using a terminal, as python alternative is not provided. (I could use `subprocess` module to call it from the notebook itself, but it was easier to just use a terminal and manually do it).
* trained the file initially, then tested it out using OpenAI playground.

### Observations on First Model:
* It performed very poorly. it wasn't even able to replicate the answers when the prompt given was the exact same as the training data. 
* Many times it just spits out random information it has internally, completely unrelated to 100ms. We need to provide it context somehow. The solution to this which i tried later was to add a prefix to all those prompts that didn't contain the word `100ms`, so that the model would know the context as well.
* Before adding prefixes, i just added one more question `What is the name of the company` with it's answer as `100ms`. I thought this should be able to provide what `100ms` meant in any further inputs, but this didn't work sadly. I still kept this question for later training sessions.
* Also, the first model would often make up a random link for the required task and pack it in markdown hyperlink format, kind of trying to fool us into thinking that it gave a meaningful output.

With this model, i proceeded to making the API and hosting the service.

## Making the API and Hosting
* For this, i searched for libraries and services that i could use for usage with a python project. After some searching, i went with `Flask` for setting up the APIs
* I used it's documentation for quickly setting it up and tested it using `Thunder Client` extension in Vscode.
* After setting up the server, i looked up the OpenAI API documentation and wrote the logic for querying the OpenAI API using the prompt provided throught the `/api/query` endpoint.
* Then i hosted the service using `Render` through their free plan.
  
## Creating better models and Tuning Hyper-parameters.
* I was not at all satisfied with the results the initial model gave. So i tried some ways in which i could get better results.
* First of all, the biggest issue was the extreme lack of training data. 100 training data points are not at all enough for a deep learning model. But this is not something that could be dealt with immediately. 
* I added `\n\n###\n\n` to the end of each prompt and ` END` to the end of each completion, as it helps the model in identifying where the data points are separated from one another (written in OpenAI Documentation).
* Now, one of the biggest issues with the initial model was it's lack of context w.r.t 100ms. It would often give answers assuming the question was asking for general information. For example, a question like : `Are there any trial account limitations?` can be asked in a lot of contexts.
* So, i just added a prefix `In 100ms, ` to all training samples which didn't contain the word `100ms`.
* Now, this isn't the best way by far, but it did help in giving context to the model. So, the second model did work better when asking questions directly from the faq. I did change the API request in a similar way, by attaching the prefix to the prompts.
* This worked better, but it was still working poorly if there was even a small change in the input prompt.
* Since the amount of data was very small, it is often recommended in case of deep neural networks to increase the number of `epochs` to better understand the structure of the data.
* So i did just that, and trained another model using the same data, with `16 epochs` instead of the standard `4 epochs`. This improved the performance a lot "relatively" (Training for more epochs costs more)
* Now, the model is able to understand the question even if the question is asked slightly differently from what's present in FAQ. 
* But it still cannot make up information that makes sense, so when it is asked something that it does not know the answer to, it very confidently spits out some nonsense.
* This is very similar to the behaviour of Chat-GPT, where it is always confident. So i doubt this is something that could be improved from our side.
* For example, when presented with the 
    * question : `is 100ms Soc 2 compliant?`
    * Answer : `Yes we are Soc - 2 complaint.`
* When asked :
    * question : `is 100ms Soc 3045 compliant?`
    * Answer : `Yes we are Soc - 3045 complaint.`
* Which makes no sense at all. It always tries to give a definite answer, and not something like "i don't know". Also, it rarely ever gives a negative response like "No".
* However, I found this model to be acceptable. So i went ahead with it.
* I also tried to train a `davinci` model for `4 epochs` to see if the results are significantly better.
* `davinci` also performed pretty bad (reason being the same as `curie-001` i think, less examples and less epochs). It costed 10 times as much to train and use, so it isn't economically viable either.

## Finding the right OpenAI Parameters
* With the system in place, i started experimenting with the `Temperature, Top P, Presence Penalty and Frequency Penalty` settings. I did experiment with these settings earlier as well, but they barely improved anything in case of the first models.
* The newer models were able to understand whenever the prompt was asking for the information present in FAQ (Though it didn't work if we change the prompt too much) or general information (where it often gave incorrect answer because of it's lack of knowledge)
* So, after some testing, i went with these values : 
```
max_tokens=200,
temperature=0.5,
presence_penalty=1.0,
frequency_penalty=1.0,
```
* The settings here basically forbids repetitive output, while allowing some creativity in it's output. It was still giving the same answer as written in FAQ whenever the prompt was asked from it.

## Fixing the relative Hyperlinks in Outputs
* The hyperlinks that the model sometimes outputs, contains relative links. To deal with them, i processed the final output through a function to replace all relative links with absolute ones (although they give 404 currently).
* The outputs give by the model contained the links in the format `[Link Text](Link)`
* So, i could use a custom logic to find and replace these links, which would probably be very efficient, but for now, i used regular expression to find these links and replace them using another function.
* To get the regular expression, i took the help of chat-GPT since it is surprisingly good at writing them. Although the code it gave for replacing the string was sort of wrong, so i wrote it myself.
* For joining the base path and relative path i used a custom logic using `os` module. I think there must be an easier way to do this but i couldn't find one quickly.
  
## Issues in Implementing an Endpoint for Adding more Question/Answers
* The training process of deep-neural networks is done in batches, so it is pretty much required to have at least hundred examples for training. So, it not at all reasonable to implement an API for directly training the model on single training examples.
* Not to mention, the training process itself is costly, with some constant cost attached to each training session, along with variable cost (proportional to number of training samples). So it is again better and economical to train on large samples at once.
* What we can do here is to store the incoming prompts and completions in a database, and then we can manually train the model or automatically train it whenever the number of samples exceeds a certain amount.

## Some Observations
* the model is able to give the correct output for the faq questions and it still works when the order of the words in the question is similar, but asked differently.
* Like, for question : `Why am I constantly getting low bandwidth alerts?`
* it gives correct result when asked : 
`"Why is it that i am constantly getting low bandwidth alerts ?"`
* but it gives wrong result when asked : 
`"i am constantly getting low bandwidth alerts, why is this happening?"`
* [This was tested with model 005-prefix-16-epochs]
* The relative links created by the model always starts with /javascript/v2/...
so these links themselves are wrong and they do not fit with the base link that we are using either.

## Some Potential Improvements
* need to get more data somehow.
* the code for fixing hyperlinks can be more efficient
* before doing the API calls, we can process and validate the inputs first, to make sure that they contains a sentence in english. Also, we can format it properly in case it contains multiple spaces and other such things.
* We can store the api calls to avoid making redundant calls to openAI's API, and instead give the result directly from the memory itself.