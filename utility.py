import numpy as np


def line_to_set(line):
    line = line[0:-1]  # remove '\n'
    set_list = []
    if len(line)==0:
        pass
    else:
        line = line.split(',')
        for item in line:
            set_list.append(int(item))
    return set_list


def log_factorial(n):
    s = 0
    if n >= 2:
        for i in range(2, n+1):
            s += np.log2(i)
    return s


def x_log2_x(x):
    if x < 1e-20:
        return 0
    else:
        return x * np.log2(x)


def length_single(freq, N):
    # the number of bits for coding a single variable
    if 1 <= freq <= N-1:
        return N * np.log2(N) - freq * np.log2(freq) - (N-freq) * np.log2(N - freq)
    else:
        return 0


def write_set_to_file(set_list, f_target):
    if len(set_list) > 0:
        for i in range(len(set_list) - 1):
            f_target.write(str(set_list[i]) + ',')
        f_target.write(str(set_list[-1]) + '\n')
    else:
        f_target.write('\n')