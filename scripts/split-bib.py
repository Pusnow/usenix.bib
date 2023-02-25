import re



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
