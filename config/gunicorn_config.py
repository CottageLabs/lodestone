import multiprocessing

bind = "127.0.0.1:5030"
workers = multiprocessing.cpu_count() * 8 + 1
proc_name = 'lodestone'
max_requests = 1000