import datetime

with open(r"C:\Python JW News\bible.txt") as f:
    bible = lines = f.readlines()

with open(r"C:\Python JW News\days.txt") as f:
    reading_links = lines = f.readlines()

x = datetime.datetime.now()

day_of_year = x.strftime("%j")

day = bible[int(day_of_year)].strip()

script = reading_links[int(day_of_year)].strip()

print(script)
print(day)


