# Event Interpreter
## How to Run
1) Add data2013.json and data2015.json into data folder
2) Pip install requirements.txt into virtual environment
3) Enter the src directory
4) To get human readable output, run: `python gg_api.py`<br>
To get autograder output, run: `python  autograder.py`<br>
    You can supply autograder with the optional flags of either 2013 or 2015 (will run both if not specified) and any number of the following tasks (will run all if none specified).
    - hosts
    - awards
    - nomniees
    - presenters
    - winner

    Note that some modifications have been made to the autograder (such as it now calls preceremony() and has accurate relative links), but none of the core functionality has been altered.

## Project Deliverables

- All code must be in Python 3. You can use any Python package or NLP toolkit, but please save and share your requirements as follows: create an environment for the project, run `pip freeze > requirements.txt`, make sure it works after running `python install -r requirements.txt` in an empty environment, and then include this `requirements.txt` in your submission/repository.
- You must use a publicly accessible repository such as Github, and commit code regularly. When pair programming, note in the commit message those who were present and involved. We use these logs to verify complaints about AWOL teammates, and to avoid penalizing the entire group for one student’s violation of academic integrity. We don’t look at the commits unless there’s something really wrong with the code, or there’s a complaint.
- Please use the Python standard for imports described [here](https://www.python.org/dev/peps/pep-0008/#imports)
- Bundle all your code together, your submission will be a .zip file on canvas.
- If you use a DB, it must be Mongo DB, and you must provide the code you used to populate your database.
- Your code must be runnable by the TA: Include a readme.txt file with instructions on what file(s) to run, what packages to download / where to find them, how to install them, etc and any other necessary information. The readme should also include the address for your Github repository.
- Your code must run in a reasonable amount of time. Your grade will likely be impacted if this is greater than 10 minutes.
- Your code cannot rely on a single Twitter user for correct answers. Particularly, the official Golden Globes account.

## Minimum Requirements

1. Host(s) (for the entire ceremony)
2. Award Names
3. Presenters, mapped to awards*
4. Nominees, mapped to awards*
5. Winners, mapped to awards*

Note: *These will default to using a hardcoded list of the awards to avoid penalizing you for cascading error. Please note that, when mining award names specifically, you cannot hardcode parts of these names in your solution with the only exception of the word "Best."

## Additional Goal Examples

- Red carpet: For example, determine who was best dressed, worst dressed, most discussed, most controversial, or perhaps find pictures of the best and worst dressed, etc.
- Humor: For example, what were the best jokes of the night, and who said them?
- Parties: For example, what parties were people talking about the most? Were people saying good things, or bad things?
- Sentiment: What were the most common sentiments used with respect to the winners, hosts, presenters, acts, and/or nominees?
- Acts: What were the acts, when did they happen, and/or what did people have to say about them?
- Your choice: If you have a cool idea, suggest it to the TA! Ideas that will require the application of NLP and semantic information are more likely to be approved.

## Required Output Formats

1. A human-readable format. This is where your additional goals output happens
2. A JSON format compatible with the autograder; this is only containing the information for the minimum tasks.

