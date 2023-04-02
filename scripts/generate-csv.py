import re
import csv
import os
from datetime import date


with open("usenix.csv", "w", newline="") as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["ID", "Book Title", "Title", "Authors", "PDFs"])

    with open("usenix.bib", "r", encoding="utf8") as usenix_file:
        usenix_bib = usenix_file.read()
        for bib in re.findall(r"@.*?\n\}", usenix_bib, re.DOTALL):
            head = bib.split("\n", 1)[0]
            id = re.search(r"\{(.+?)\,", head)
            if not id:
                continue
            id = id.group(1)

            year = re.search(r"year = \{(.*?)\},", bib)
            month = re.search(r"month = (.*?),", bib)

            # skip not published
            if year and year.group(1) == "Submitted":
                continue

            title = re.search(r"title = \{(.*?)\},", bib)
            booktitle = re.search(r"booktitle = \{.*\((.*?)\).*\},", bib)
            author = re.search(r"author = \{(.*?)\},", bib)

            if not title or not booktitle or not author:
                continue

            title = title.group(1)
            booktitle = booktitle.group(1)
            author = author.group(1)

            pdf_link_path = "pdf-link/%s.txt" % id
            pdf_links = ""
            if os.path.exists(pdf_link_path):
                with open(pdf_link_path, "r", encoding="utf8") as pdf_link_file:
                    pdf_links = pdf_link_file.read().splitlines()
                    pdf_links = [link for link in pdf_links]
                    pdf_links = ";".join(pdf_links)

            csv_writer.writerow([id, booktitle, title, author, pdf_links])
