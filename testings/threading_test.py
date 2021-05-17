import time
import threading


start = time.perf_counter()


def do_something():
    print('Sleeping for 1 second')
    time.sleep(1)
    print('Done sleeping')


t1 = threading.Thread(target=do_something)
t2 = threading.Thread(target=do_something)

t1.start()
t2.start()

t1.join()
t2.join()

end = time.perf_counter()

print(f'Total time taken = {round(end-start,2)}')
