

def from_csv(file, separator):
    arr = []
  
    for chunk in file.chunks():
        rows = chunk.decode("utf-16").split("\n")
        for row in rows:
            if row:
                arr.append(row.split(separator))
    return arr
    # reader = csv.reader([chunk.decode() for chunk in file.chunks()])
    # print(reader)
    # for i in reader:
    #     print(i)
    # if file_content:
    #     return file_content.split(separator)
    # return None

