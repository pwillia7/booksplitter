import os
import os.path
import sys
import openai
import time
from pathlib import Path
if len(sys.argv) < 3:
    print("generatePrompts.py - Use openAI GPT3 to generate stable diffusion prompts. Runs recursively in specified folder.\n\n Usage: python generaptePrompts.py [folder/containing/text] [textfilename] [textName]\n\nExample python generatePrompts.py . section.txt 'Pride and Prejudice'")
    sys.exit()
# Load your API key from an environment variable or secret management service
openai.api_key = ""
for path in Path(sys.argv[1]).rglob(sys.argv[2]):
    promptFile = path.open()
    count = 0
    prompts = []
    while True:
        time.sleep(.25)
        count += 1
        # Get next line from file
        line = promptFile.readline()
        for i in range(5):
            try:
                response = openai.Completion.create(model="text-davinci-003", prompt="Distill and summarize the following passage of " + sys.argv[3] + " and return a csv of key words for the passage: " + line, frequency_penalty=0,
    presence_penalty=0, top_p=1, temperature=0.75, max_tokens=256)
            except:
                time.sleep(1)
                continue
            else:
                break
        prompts.append(response.choices[0].text)
        # if line is empty
        # end of file is reached
        if not line:
            finPromptFile = open(str(path.parents[0]) + "/finishedPrompts.txt","a+")
            finLogFile = open(str(path.parents[0]) + "/finishedPrompts.log","x")
            promptCount = 1
            keywSwitch = 0
            for prompt in prompts:
                finLogFile.write(prompt)
                promptLines = prompt.split("\n")
                for pline in promptLines:
                    if keywSwitch == 1:
                        finPromptFile.write(pline)
                        keywSwitch = 0
                        continue
                    if "Key words:" in pline or "key words:" in pline or "keywords:" in pline or "Key Words:" in pline or "Keywords:" in pline:
                        finPromptFile.write(pline + "\n")
                        promptCount += 1
                        if pline == "Key words:" or pline == "key words:" or pline == "keywords:" or pline == "Key Words:" or pline == "Keywords:":
                            keywSwitch = 1
            break
    promptFile.close()
