import os
import sys
import re
if len(sys.argv) < 4:
    print("bookCutter.py - Cut a book into chapters and smaller configurable sections.\n\n Usage: python bookcutter.py [bookname] [delimiterText] [path/to/book] [pageWordCount]\n\nExample: bookcutter.py Dracula CHAPTER ./dracula.txt 425\n\nIt is recommended to remove all non chapter text from the file before running.")
    sys.exit()
sectionDelim = "SECTIONREPLACE61723"
bookName = sys.argv[1]
delimiterText = sys.argv[2]
bookFile = sys.argv[3]
pageWordCount = int(sys.argv[4])
curWordCount = 0
# cut up on delimiter
chapters = []
chapterCount = -1
with open(bookFile, "r") as book:
    for line in book:
        words = line.lower()
        words = re.sub("[^\w ]", "", words)
        wordsLen = words.split(" ")
        if len(wordsLen) + curWordCount > pageWordCount:
            line = sectionDelim + line
            curWordCount = 0
        else:
            curWordCount += len(wordsLen)
        if chapterCount == -1:
            chapters.append(line)
            chapterCount += 1
            continue
        if delimiterText in line:
            chapterCount += 1
            chapters.append("\n")
        chapters[chapterCount] += "\n" + line
# make folders and files for chapters. Write the chapter files out.
chapterCount = 1
for chapter in chapters:
    sections = chapter.split(sectionDelim)
    folderPath = bookName + "-Chapter" + str(chapterCount)
    chapterFolder = folderPath + "/Chapter" + str(chapterCount) + ".txt"
    os.mkdir(folderPath)
    chapterFile = open(chapterFolder,"w")
    chapterFile.write(chapter)
    sectionCount = 1
    sectionFile = open(folderPath + "/sections" + ".txt", "w")
    for section in sections:
        sectionFile.write(section.replace("\n",""))
        sectionFile.write("\n")
        sectionCount += 1
    chapterCount += 1
# cut into smaller pieces