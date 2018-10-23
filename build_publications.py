#! /usr/bin/env python

import sys
from adspy.scraper import queryADS,citations
import fnmatch
import os
from adspy.progress import *
import numpy as np





# Open .tex file
f = open("publications.tex","w")
import datetime
today = datetime.date.today()
now = today.strftime('%d %B %Y')
#s = "Astericks ($\\ast$) indicate first author papers. Numbers in square brackets indicate number of citations as of " + \
#    now + ".\n\n\n\\begin{etaremune}[leftmargin=15pt]\n"
s = "Astericks ($\\ast$) indicate first author papers.\n\n\n\\begin{etaremune}[leftmargin=15pt]\n"
f.write(s)

total_papers = 0
refereed = 0
first_author = 0
Ncitations = []

print("Constructing publication list...")
papers_info = queryADS(authors="Merson,A",sortBy="NDATE",refereed=None)
text = ""
progress = Progress(len(papers_info))
for paper in papers_info:
    
    label = None

    bibcode = paper[0].split("{")[1].split(",")[0]
    Ncit = len(citations(bibcode,refereed=False))
    
    # Extract list of authors
    authors = " ".join(paper).split("author = {")[1].split('title = ')[0]
    authors = authors.replace(" and ",";").replace("} ,","},").replace("},","")
    authors = authors.split(";")
    numberAuthors = len(authors)
    for i in range(len(authors)):
        auth = authors[i]
        auth = auth.replace("{","",1).strip()
        if "Merson" in auth:
            auth = "\\textbf{" + auth + "}"
        authors[i] = auth
    if "Merson" in authors[0]:
        label = "Merson"
    else:
        label = authors[0].split()[0]
    authors = "; ".join(authors)
    if "; et al." in authors:
        authors = authors.replace("; et al."," \\textit{et al.}")
    if "Merson" not in authors or numberAuthors > 50:
        #authors = authors.split(";")[0] + " \\textit{et al.}; contributing author"
        authors = authors.split(";")[0] + " \\textit{et al.} including \\textbf{Merson, A.}"
    # Extract title of paper
    title = " ".join(paper).split('title = "{')[1].split('}",')[0]
    title = title.replace("$\\backslash$","\\").replace("\\$","$")
    title = title.replace("\~{}","$\sim$")
    title = title.replace("{\\tilde}","$\sim$")
    
    # Extract year of paper
    year = fnmatch.filter(paper,"*year*")[0].split()[-1]
    label = label + year
    # Extract journal
    journal = fnmatch.filter(paper,"*journal*")[0].split("=")[-1]
    journal = journal.replace("{","").replace("}","").strip()

    if journal == "ArXiv e-prints,":
        if len(fnmatch.filter(paper,"*primaryClass*"))>0:
            journal = fnmatch.filter(paper,"*primaryClass*")[0].split("=")[-1].strip()
        else:
            journal = fnmatch.filter(paper,"*archivePrefix*")[0].split("=")[-1].strip()
        journal = journal.replace('"',"").split(".")[0]
        eprint = fnmatch.filter(paper,"*eprint*")[0].split("=")[-1].strip()
        journal = journal + "/" + eprint.replace("{","").replace("}","")
        journal = journal.replace(",","")
    else:
        journal = journal.replace("{","").replace("}","")
        code = fnmatch.filter(paper,"*volume*")[0].split("=")[-1].strip()
        if len(fnmatch.filter(paper,"*pages*"))>0:
            code = code +" "+fnmatch.filter(paper,"*pages*")[0].split("=")[-1].replace(",","").strip()
        journal = journal +" "+ code.replace("{","").replace("}","")
        refereed += 1
        

    # Write to LaTeX file
    label = label.replace(",","")
    text = "\item \label{itm:"+label+"}"
    if "Merson" in label:
        text = text + "{\Large $\\ast$}"
        first_author += 1
    text = text + " `"+title+"'\\newline\n"
    text = text + "  \\begin{small}"+authors+";\end{small} "+year+" "+journal
    #text = text + " ["+str(Ncit)+"]"
    text = text + "\n\n"    
    f.write(text)    

    
    total_papers += 1
    Ncitations.append(Ncit)

    progress.increment()
    progress.print_status_line()


f.write("\end{etaremune}\n")
f.close()



def hindex(cites):
    import numpy as np
    cites = np.array(cites)
    npapers = len(cites)
    h = 0
    for np in range(1,npapers+1):
        mask = cites>=np
        if len(cites[mask])>=np:
            h += 1
    return h
    


Ncitations = np.array(Ncitations)
total_citations = np.sum(Ncitations)

f = open("publications_summary.tex","w")
info = "Total of "+str(total_papers)+" papers, of which "+str(refereed)+" published or accepted for publication in main "+\
    "international peer reviewed journals. First author in "+str(first_author)+" papers.\n"
f.write(info)
info = "\\noindent Total number of citations is "+str(total_citations)+", giving an impact factor h-index of "+str(hindex(Ncitations)) + ".\n\n"
f.write(info)
f.close()







