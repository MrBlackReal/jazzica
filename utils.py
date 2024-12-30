import time

def get_random_entry(input: list):
    """
    Most simple method to ever exist
    """
    return input[int(time.time()) % len(input)]