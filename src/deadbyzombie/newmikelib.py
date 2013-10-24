def sign(val):
    if float(val) == 0.0: return 1.0
    else: return val / abs(val)
