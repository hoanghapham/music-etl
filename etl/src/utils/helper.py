from typing import Callable
from logging import Logger
from pydantic import BaseModel
import json
import os
from logging import Logger

def generate_intervals(total_num: int, interval: int = 10) -> list[int]:
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

def iter_execute(
        func: Callable, 
        iterable: list, 
        logger: Logger = None, 
        logging_interval: int = 20, 
        message_template: str = "Processed {} of {} items ({}%)") -> list:
    """Iterate throught an iterable and execute the function

    Parameters
    ----------
    func : Callable
        A function to be executed against the iterable
    iterable : list
        a list of input objects for the function
    logger : Logger
    loggin_interval : int
        Represents the interval that the logging message will be printed. 
        By default, the logger will print a message once every 20% of the total iterations.
    message_template : str
        Template of the logging message.

    Returns
    -------
    list
        List containing the results of the func call.
    """

    results = []
    iter_num = len(iterable)
    logging_points = generate_intervals(iter_num, logging_interval)
    
    for i, item in enumerate(iterable, start=1):
        result = func(item)
        
        if result is not None:
            if isinstance(result, list):
                results += result
            else:
                results.append(result)

        if logger is not None:
            if i in logging_points:
                pct = round(i / iter_num * 100, 0)
                logger.info(message_template.format(i, iter_num, pct))
    
    return results


def write_json(
        data: list[BaseModel] | BaseModel, 
        output_path: str, 
        new_line_delimited: bool = False,
        logger = Logger
    ):
        """Write a JSON representation of the objects

        Parameters
        ----------
        data : a list of BaseModel, or a BaseModel instance
        output_path : str
            Full destination path.
        new_line_delimited: bool
            If True, write JSON in new-line delimited format
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if isinstance(data, BaseModel):
            with open(output_path, 'w') as f:
                json.dump(data.dict(), f)
        
        elif isinstance(data, list):

            if len(data) == 0:
                if logger is not None:
                    logger.warn(f"No data to write.")
                
            else:
                json_data = [i.dict() for i in data]
                
                with open(output_path, 'w') as f:
                    if new_line_delimited:
                        for line in json_data:
                            json.dump(line, f)
                            f.write('\n')
                    else:
                        json.dump(json_data, f)