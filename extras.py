from time import sleep
from tqdm import tqdm
from random import randint


def seep_with_progress_bar(time: int, msg: str, random=True):

    if random:
        wait_time = randint(1, time)

    for _ in tqdm(range(wait_time), desc=msg, leave=True, unit='sec.'):
        sleep(1)
