def generate_logging_points(total_num: int, interval: int = 10) -> list[int]:
    """Generate a list of index points to log the progress of an iterative process.

    Parameters
    ----------
    total_num : int
        Total number of iterations  
    interval : int, optional
        Percent interval by which we will place the logging points, by default 10 (percent)

    Returns
    -------
    list[int]
        List of index points
    """    
    return [int(round(i / 100 * total_num)) for i in range(interval, 100 + interval, interval)]