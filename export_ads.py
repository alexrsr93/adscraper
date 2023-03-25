import csv 

def generate_csv(rows, filename, column_index, column_values): 
    with open(filename, 'w', newline='') as csvfile: 
        writer = csv.writer(csvfile)
        for row in rows:
            for i, value in zip(column_index, column_values):
                row[i] = value
            writer.writerow(row)
    