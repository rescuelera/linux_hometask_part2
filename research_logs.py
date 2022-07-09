from pathlib import Path
import argparse
from os import listdir
from os.path import isfile, join
import json

parser = argparse.ArgumentParser(description='Process some logs.')
parser.add_argument('--folder', type=Path, default=None,
                    help='folder with logs')
parser.add_argument('--file', type=Path, default=None,
                    help='log file path')
args = parser.parse_args()

if args.folder is None and args.file is None:
    raise ValueError("Укажите либо файл, либо папку")

if args.folder is not None and args.file is not None:
    raise ValueError("Укажите либо файл, либо папку. Что-нибудь одно")

if args.file is not None:
    filename_list = [args.file]
else:
    folder_path: Path = args.folder
    filename_list = [f for f in listdir(args.folder) if isfile(join(args.folder, f)) and f.endswith(".log")]

ip_dict = {}
ip_long_time = {}

ip_time_max = [-1, -1, -1]
all_information = {}
request_counts = {}
total_request_count = 0
for filename in filename_list:
    with open(filename) as infile:
        for input_line in infile:
            if input_line == "":
                continue
            input_cols = input_line.split()
            ip_time = input_cols[-1]
            ip_time_number = int(ip_time)
            min_time = min(ip_time_max)
            if min_time < ip_time_number:
                method = input_cols[5].strip('"')
                time_information = input_cols[3].strip('[')
                all_information[
                    ip_time_number] = f"{method} {input_cols[6]} {input_cols[0]} {input_cols[-1]} {time_information}"
                if min_time in all_information:
                    del all_information[min_time]
                ip_time_max.remove(min_time)
                ip_time_max.append(ip_time_number)
            ip = input_cols[0]
            if ip in ip_dict:
                ip_dict[ip] += 1
            else:
                ip_dict[ip] = 1
            method = input_cols[5].strip('"')
            total_request_count += 1
            if method in request_counts:
                request_counts[method] += 1
            else:
                request_counts[method] = 1

all_information_list = []
for k, v in all_information.items():
    all_information_list.append(f"{k}: {v}")
all_information_list_str = '\n'.join(all_information_list)

ip_top = []
for _ in range(3):
    ip_max = max(ip_dict, key=ip_dict.get)
    ip_top.append(ip_max)
    del ip_dict[ip_max]

long_request = ["метод, url, ip, длительность, дату и время запроса",
                "метод, url, ip, длительность, дату и время запроса"]
ip_top_list = '\n'.join(ip_top)
ip_time_list = '\n'.join([str(t) for t in ip_time_max])
long_request_list = '\n'.join(long_request)
request_counts_list = []
for k, v in request_counts.items():
    request_counts_list.append(f"{k}: {v}")
request_counts_list_string = '\n'.join(request_counts_list)

result = f"""
Отчёт:
общее количество выполненных запросов: {total_request_count}
количество запросов по HTTP-методам:
{request_counts_list_string}
топ 3 IP адресов, с которых были сделаны запросы:
{ip_top_list}
топ 3 самых долгих запросов: 
{all_information_list_str}
"""
print(result)
result_dict = {"total_requests": total_request_count,
               "requests": request_counts,
               "top_3_ip_adresses": ip_top,
               "top_3_longest_requests": all_information

               }

with open("report.json", "w") as file:
    file.write(json.dumps(result_dict, indent="\t"))
