
size = 8
for l in range(1, (size + size)):
    start_col = max(0, l - size)
    count = min(l, (size - start_col), size)
    for j in range(0, count):
        y_ = size - (min(size, l) - j - 1)
        x_ = start_col + j
        print(x_, y_)