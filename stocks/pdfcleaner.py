
import csv

russell3k = "membership-russell-3000.text"
out_file = "russell3000.csv"

with open(russell3k, "r") as f:
    data = f.read().split("\n")

with open(out_file, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)

    for line in data:
        if line.startswith("As of ") or \
            line.startswith("As of ") or \
            line.startswith("Russell 3000") or \
            line.startswith("Index membership") or \
            line.startswith("Company Ticker"):
            pass

        elif line.startswith("For more information about Russell Indexes call us"):
            break
        else:
            ticker = line.split()[-1]
            company = " ".join(line.split()[0:-1])
            writer.writerow((ticker, company))
