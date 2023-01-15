import os
import os.path
import sys
import re
import openai
import time
import math

# Helper text
if len(sys.argv) < 4:
    print("bookIllustrator.py - Cut a book into chapters and smaller configurable sections.\n\n Usage: python bookIllustrator.py [bookname] [delimiterText] [path/to/book]\n\nExample: bookIllustrator.py Dracula CHAPTER ./dracula.txt \n\nIt is recommended to remove all non chapter text from the file before running.")
    sys.exit()

# Vars #
## String on which to cut Chapters
delimiterText = sys.argv[2]

# Book name and path
bookFile = sys.argv[3]
bookName = sys.argv[1]

# Set the number of words to send to Open AI at a time
maxRequestWords = 1000

# Chapters array and counter. -1 so loop can initialize
chapters = []
chapterCount = -1

# Array of arrays utility
def chunkify(lst,n):
    return [lst[i::n] for i in range(n)]

# main parsing loop to cut book into chapters
with open(bookFile, "r") as book:
    print("Reading Book File...\n\n")
    
    for line in book:
        ## Make Chapters
        # Create array of chapters, appending new position if delimiter found
        if chapterCount == -1 or delimiterText in line:
            print("New Chapter Found.")
            chapters.append("\n")
            chapterCount += 1
        chapters[chapterCount] += line
            
print("\nBook parsed. Found " + str(chapterCount+1) + " chapters.")


# Create edit book file and prompt file master
editedBookFile = open(bookName + "-edited.txt", "a+")
masterPromptFile = open(bookName + "-prompts.txt", "a+")
masterPromptFileClean = open(bookName + "-promptsCLEAN.txt", "a+")
logFile = open (bookName + "-edited.log", "a+")
print("Log, prompt and book files created.")
# Reset Chapter Count
chapterCount = 0

# Chapter Loop Prompt Generation
for chapter in chapters:

    chapterCount += 1
    masterPromptFile.write("~~~BEGIN Chapter " + str(chapterCount) + "~~~")
    # Write chapter to edited book file
    editedBookFile.write(chapter)
    logFile.write("\nSTART Chapter " + str(chapterCount))
    print("\n\nParsing chapter " + str(chapterCount) + "...")    
    
    # Set folderpath for chapter
    folderPath = bookName + "-Chapter" + str(chapterCount)

    # Set Chapter File
    chapterFile = folderPath + "/Chapter" + str(chapterCount) + ".txt"

    os.mkdir(folderPath)
    print("\nChapter folder created.")
    
    chapterFileWrite = open(chapterFile, "w")
    chapterFileWrite.write(chapter)
    print("Chapter text file written.")
    
    chapterPromptFilePath = folderPath + "/prompts.txt"
    chapterPromptFile = open(chapterPromptFilePath, "w")

    chapterRequests = []
    chapterWords = chapter.replace('\r','').replace('\n',' ')
    chapterWords = re.sub(" {2,}", " ", chapterWords)
    chapterWordsArray = chapterWords.split()
    chapterRequestsLen = math.ceil(len(chapterWordsArray) / maxRequestWords)
    chapterRequestsList = chunkify(chapterWordsArray,chapterRequestsLen)
    for requestList in chapterRequestsList:
        chapterRequests.append(" ".join(requestList))


    print("\nChapter parsed for GPT-3 requests. Running API requests on " + str(len(chapterRequests)) + " chapter sections for chapter " + str(chapterCount) + "...")
    logRequestCount = 1
    chapWC = maxRequestWords
    for chapterRequest in chapterRequests:
        logFile.write("\nRequest " + str(logRequestCount) + "a Request:\n" + "Summarize each scene in the following text:" + chapterRequest + "\n\nScene 1: ")
        for i in range(5):
            try:
                print("\nRequest "+ str(logRequestCount) + "/" + str(len(chapterRequests)) + "\n1st API call in progress...")
                response = openai.Completion.create(model="text-davinci-003", prompt="Summarize each scene in the following text:" + chapterRequest + "\n\nScene 1: ", frequency_penalty=0, presence_penalty=0, top_p=1, temperature=0.75, max_tokens=2084)
            except:
                print("\n\nAPI Response failed. Retrying...")
                time.sleep(1)
                continue
            else:
                logFile.write("\nRequest " + str(logRequestCount) + "a Response:\n" + response.choices[0].text)
                for j in range(5):
                    logFile.write("\nRequest " + str(logRequestCount) + "b Request:\n" + "For each of the following scenes from " + bookName + ", generate a detailed description of a relevant illustration:\nScene 0: Jonathan Harker leaves Munich at 8:35 PM and arrives in Vienna the next morning.\nScene 1: " + response.choices[0].text + "\n\nIllustration 0: A detailed illustration of Jonathan Harker, lit by a lamp at night in a train compartment looking out the window which shows the passing countryside illuminated by the moonlight.\n \nIllustration 1: ")
                    print("2nd API call in progress...")
                    try:
                        response2 = openai.Completion.create(model="text-davinci-003", prompt="For each of the following scenes from " + bookName + ", generate a detailed description of a relevant illustration:\nScene 1: " + response.choices[0].text + "\n\nIllustration 0: A detailed illustration of Jonathan Harker, lit by a lamp at night in a train compartment looking out the window which shows the passing countryside illuminated by the moonlight.\n \nIllustration 1: ", frequency_penalty=0, presence_penalty=0, top_p=1, temperature=0.75, max_tokens=2084)
                    except:
                        print("\n\nAPI Response 2 failed. Retrying...")
                        time.sleep(1)
                        continue
                    else:
                        logFile.write("\nRequest " + str(logRequestCount) + "b Response:\n" + response2.choices[0].text)
                        print("\nPrompt successfully generated.")
                        logRequestCount += 1
                        break
                break
        cleanedPrompts = re.sub("Illustration [0-9]*\: ","",response2.choices[0].text)
        cleanedPrompts = re.sub("^\n", "", cleanedPrompts)
        masterPromptFile.write("\n~~ For words " + str(chapWC) + " - " + str(chapWC+maxRequestWords) + " ~~\n")
        masterPromptFile.write(cleanedPrompts)
        chapterPromptFile.write("\n~~ For words " + str(chapWC) + " - " + str(chapWC+maxRequestWords) + " ~~\n")
        chapterPromptFile.write(cleanedPrompts)
        masterPromptFileClean.write(cleanedPrompts)
        chapWC += maxRequestWords
        print("Prompt written to master and chapter files")
    print("\n\nAll chapter prompts generated. Continuing to next chapter...")
print("\n\nAll prompts generated. Finishing...")