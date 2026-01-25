
driver.get('https://wol.jw.org')

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

text_list = []

for link in soup.find_all("div", {"class":"tabContent active"}):
    header = link.h2.text.strip()
    scripture = link.p.text.strip()
    notes = link.p.next_sibling.next_sibling.text.strip()

    text_dict = {}
    text_dict['Date'] = header
    text_dict['Script'] = scripture
    text_dict['Notes'] = notes

    text_list.append(text_dict)