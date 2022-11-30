from time import sleep
from tqdm import tqdm
from random import randint
from yaspin import yaspin


def seep_with_progress_bar(time: int, msg: str, random=True):

    if random:
        wait_time = randint(1, time)
    else:
        wait_time = time

    # with yaspin(text=msg) as spinner:
    sleep(wait_time)
        # spinner.ok('Done')

    # for _ in tqdm(range(wait_time), desc=msg, leave=True, unit='sec.'):
    #     sleep(1)
