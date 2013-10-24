import random

def chance(num,denom):
    if num > 0 and denom > 0:
        return random.randrange(denom) < num
    else:
        return False

def rand_range_signed(max_magnitude):
    v = random.randrange(max_magnitude+1)
    if v != 0 and random.randrange(2) == 0:
        v = -v
    return v

def rand_diff(max_magnitude_x, max_magnitude_y):
    xd = rand_range_signed(max_magnitude_x)
    yd = rand_range_signed(max_magnitude_y)
    return (xd, yd)

def rand_range(min, span):
    return min + random.randrange(span + 1)

def rand_success(chance):
    assert 0.0 <= chance <= 1.0, 'chance param %s must satisfy: 0.0 <= chance <= 1.0' % chance
    return random.random() <= chance

def read_file(filename):    
    f = file(filename, 'r')     
    s = f.read()
    f.close()
    return s

def read_file_lines(filename):    
    s = read_file(filename)
    return s.splitlines()
