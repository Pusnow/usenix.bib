import re
import os
from datetime import date
import concurrent.futures
import unicodedata
import urllib.request
import urllib.parse

MONTH_MAP = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

URL_SPECIAL_REPLACES = {
    "d{\\textquoteright}antoni": "d'antoni",
}

URL_FIX_ID = {
    "187158": "https://www.usenix.org/conference/hotdep14/workshop-program/presentation/xu",
    "179424": "https://www.usenix.org/conference/hotpar13/workshop-program/presentation/shefﬁeld",
}

URL_REPLACES = {
    "{\\textemdash}": "—",
    "{\\textendash}": "–",
    "{\\textquoteright}": "’",
    "{\\texttrademark}": "™",
    "{\\textquotedblleft}": "“",
    "{\\textquotedblright}": "”",
    "{\\textbullet}": "•",
    "{\\textregistered}": "®",
    "{\\i}": "i",
    "{\\'\\i}": "í",
    "{\\c c}": "ç",
}


def fix_url(id, url):

    if id in URL_FIX_ID:
        url = URL_FIX_ID[id]

    for mp in [URL_SPECIAL_REPLACES, URL_REPLACES]:
        for key in mp:
            if key in url:
                url = url.replace(key, mp[key])
    url = re.sub(r"\{\\\"(.)\}", r"\1%s" % "\u0308", url)
    url = re.sub(r"\{\\\'(.)\}", r"\1%s" % "\u0307", url)
    url = re.sub(r"\{\\`(.)\}", r"\1%s" % "\u0300", url)
    url = re.sub(r"\{\\\^(.)\}", r"\1%s" % "\u0302", url)
    url = re.sub(r"\{\\~(.)\}", r"\1%s" % "\u0303", url)
    url = re.sub(r"\{\\\=\{(.)\}\}", r"\1%s" % "\u0304", url)
    url = unicodedata.normalize("NFC", url)

    url = ":".join((urllib.parse.quote(a) for a in url.split(":")))

    return url


def download_url(id, url):
    with urllib.request.urlopen(url) as conn:
        return conn.read()


JOBS = []
with open("usenix.bib", "r", encoding="utf8") as usenix_file:
    usenix_bib = usenix_file.read()
    for bib in re.findall(r"@.*?\n\}", usenix_bib, re.DOTALL):
        head = bib.split("\n", 1)[0]
        id = re.search(r"\{(.+?)\,", head)
        if not id:
            continue
        id = id.group(1)
        with open("bib/%s.bib" % id, "w", encoding="utf8") as bib_file:
            bib_file.write(bib)

        pdf_link_path = "pdf-link/%s.txt" % id

        if os.path.exists(pdf_link_path):
            continue

        url = re.search(r"url = \{(.*?)\},", bib)

        if not url:
            continue
        url = url.group(1)

        year = re.search(r"year = \{(.*?)\},", bib)
        month = re.search(r"month = (.*?),", bib)

        # skip not published
        if year and month:
            year = int(year.group(1))
            month = MONTH_MAP[month.group(1)]
            today = date.today()
            if year >= today.year and month >= today.month:
                continue
        elif year and year.group(1) == "Submitted":
            continue

        fixed_url = fix_url(id, url)
        JOBS.append((id, fixed_url))


with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    future_to_url = {executor.submit(download_url, job[0], job[1]): job for job in JOBS}
    total = len(JOBS)
    start = 1
    for future in concurrent.futures.as_completed(future_to_url):
        id = future_to_url[future][0]
        url = future_to_url[future][1]
        print("[%s/%s] Processing (%s)" % (start, total, id))
        start += 1
        try:
            data = future.result().decode("utf8")
        except Exception as exc:
            print("%s %r generated an exception: %s" % (id, url, exc))
        else:
            pdf = re.search(
                r"<meta .*?name=\"citation_pdf_url\".*?content=\"(.*?)\".*?\/>", data
            )
            with open("pdf-link/%s.txt" % id, "w", encoding="utf8") as f:
                if pdf:
                    f.write(pdf.group(1).strip() + "\n")
                else:
                    for pdf_link in re.findall(r"href\s*?=\s*?\"(.*?\.pdf)\"", data):
                        f.write(pdf_link.strip() + "\n")
