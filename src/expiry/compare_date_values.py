
from datetime import datetime

dates = ["21.02.05", "21.01.07"]

print("Comparing dates:\n")

for value in dates:
    parsed = datetime.strptime(value, "%y.%m.%d")
    print(value, "->", parsed.strftime("%Y-%m-%d"))

date1 = datetime.strptime(dates[0], "%y.%m.%d")
date2 = datetime.strptime(dates[1], "%y.%m.%d")

print("\nEarlier date:", min(date1, date2).strftime("%Y-%m-%d"))
print("Later date:", max(date1, date2).strftime("%Y-%m-%d"))
