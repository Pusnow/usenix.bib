import re
import csv
import os
from datetime import date


def get_matched(mtch):
    if mtch:
        return mtch.group(1)
    else:
        return ""


with open("usenix.csv", "w", newline="") as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(
        [
            "id",
            "author",
            "title",
            "booktitle",
            "year",
            "isbn",
            "address",
            "pages",
            "url",
            "publisher",
            "month",
            "pdf",
        ]
    )

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

            title = re.search(r"title = \{(.*?)\},\s*\n", bib)
            booktitle = re.search(r"booktitle = \{.*\((.*?)\).*\},\s*\n", bib)
            author = re.search(r"author = \{(.*?)\},\s*\n", bib)
            isbn = re.search(r"isbn = \{(.*?)\},\s*\n", bib)
            address = re.search(r"address = \{(.*?)\},\s*\n", bib)
            pages = re.search(r"pages = \{(.*?)\},\s*\n", bib)
            url = re.search(r"url = \{(.*?)\},\s*\n", bib)
            publisher = re.search(r"publisher = \{(.*?)\},\s*\n", bib)

            title = get_matched(title)
            booktitle = get_matched(booktitle)
            author = get_matched(author)
            isbn = get_matched(isbn)
            address = get_matched(address)
            pages = get_matched(pages)
            url = get_matched(url)
            publisher = get_matched(publisher)

            year = get_matched(year)
            month = get_matched(month)

            pdf_link_path = "pdf-link/%s.txt" % id
            pdf_links = ""
            if os.path.exists(pdf_link_path):
                with open(pdf_link_path, "r", encoding="utf8") as pdf_link_file:
                    pdf_links = pdf_link_file.read().splitlines()
                    pdf_links = [link for link in pdf_links]
                    pdf_links = ";".join(pdf_links)

            csv_writer.writerow(
                [
                    id,
                    author,
                    title,
                    booktitle,
                    year,
                    isbn,
                    address,
                    pages,
                    url,
                    publisher,
                    month,
                    pdf_links,
                ]
            )
