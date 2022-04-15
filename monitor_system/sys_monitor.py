import psutil

def monitor_cpu(event, interval:float):
    print("Start monitoring CPU utilization.")
    
    while not event.wait(interval):
        cpu_per_list = psutil.cpu_percent(percpu=True)
        cpu_pers = " ".join([f"{v:8.2f}%" for v in cpu_per_list])
        print(f"CPU Utilization Rate: {cpu_pers}")
    print("Finish monitoring CPU utilization.")
    
if __name__ == "__main__":
    from multiprocessing import Process, Event
    mon_event = Event()
    interval = 1.0
    
    p1 = Process(target=monitor_cpu, args=(mon_event, interval,))
    p1.start()
    for i in range(100000000):
        _ = i + i
    mon_event.set()
    p1.join()