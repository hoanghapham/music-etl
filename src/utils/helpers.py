def generate_logging_points(total_num: int, interval: int = 10):
    return [int(round(i / 100 * total_num)) for i in range(interval, 100 + interval, interval)]