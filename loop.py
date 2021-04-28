
total_size = 2
batch_size_count=100

for start_index in range(0, total_size, batch_size_count):
    end_index = total_size if start_index + batch_size_count > total_size else start_index + batch_size_count
    print(start_index, end_index)