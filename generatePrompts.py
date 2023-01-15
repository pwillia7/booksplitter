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
openai.api_key = process.env.OPENAI_API_KEY
chapterCount = 0
for path in Path(sys.argv[1]).rglob(sys.argv[2]):
    chapterCount += 1
    print("Prompt file found...")
    promptFile = path.open()
    prompts = []
    print("Generating prompts via GPT-3...")
    while True:
        # Get next line from file
        line = promptFile.readline()
        for i in range(5):
            try:
                response = openai.Completion.create(model="text-davinci-003", prompt="Create a summary of each scene from the following passage of " + sys.argv[3] + ":\n" + line + ".", frequency_penalty=0, presence_penalty=0, top_p=1, temperature=0.75, max_tokens=256)
            except:
                print("API Response failed. Retrying...")
                time.sleep(1)
                continue
            else:
                for j in range(5):
                    print("2nd API call in progress...")
                    try:
                        response2 = openai.Completion.create(model="text-davinci-003", prompt="Return a single csv list of keywords for the following scene summaries from " + sys.argv[3] + ":\n" + response.choices[0].text, frequency_penalty=0, presence_penalty=0, top_p=1, temperature=0.75, max_tokens=256)
                    except:
                        print("API Response 2 failed. Retrying...")
                        time.sleep(1)
                        continue
                    else:
                        print("Prompt successfully generated.")
                        break
                break
        prompts.append(response2.choices[0].text)
        print("Prompt Generation Completed. Generated " + str(len(prompts)) + " prompts.")
        # if line is empty
        # end of file is reached
        if not line:
            chapterCount +=1
            mainPromptFile = open(str(path.parents[1]) + "/allPrompts.txt","a+")
            mainPromptFile.write("Chapter: " + str(chapterCount))
            finPromptFile = open(str(path.parents[0]) + "/finishedPrompts.txt","a+")
            for prompt in prompts:
                finPromptFile.write(prompt)
                mainPromptFile.write(prompt)
            break                    
    promptFile.close()
