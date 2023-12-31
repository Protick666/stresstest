import subprocess
import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from csv import reader
import logging
import time
from logging.handlers import RotatingFileHandler

split = 50
#logging.basicConfig(filename='timing.log', encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('log/my_log.log', maxBytes=5000000000000000000, backupCount=1000)
logger.addHandler(handler)
from pathlib import Path

source_dir = "/common/"
# dest_dir = "dest/"
machine_name = None

dest_pharah_dir = "/net/data/dns-ttl/ocsp_multi_ec2/"
rsa_loc = "/id_rsa"

dump_directory = "log/"
Path(dump_directory).mkdir(parents=True, exist_ok=True)

'''
New EC2
cat /etc/resolv.conf
apt install software-properties-common
add-apt-repository ppa:deadsnakes/ppa
apt install python3.8
apt install python3-pip
apt-get install git-core git-gui git-doc
apt-get install tcpdump
pip install selenium
apt install firefox
snap install firefox
apt install snapd
systemctl start snapd
'''

def start_tcp_dump(filename):
    #return
    p = subprocess.Popen(["tcpdump", "-w", "{}{}".format(source_dir, filename)], stdout=subprocess.PIPE)
    time.sleep(.5)
    return p

def end_tcp_dump(p):
    #return
    p.terminate()



def execute_cmd(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return output, error

from os import listdir
from os.path import isfile, join, getsize



cmd = "scp -i {} -P 2222 {} protick@pharah.cs.vt.edu:{}".format(rsa_loc, "hello.txt", dest_pharah_dir)
ans = execute_cmd(cmd)

def mv_files(filename):
    dir_to_look_at = source_dir[: -1]
    print("In the file with ", filename)
    files_to_move = [join(dir_to_look_at, f) for f in listdir(dir_to_look_at) if isfile(join(dir_to_look_at, f))]
    print("Pre ", files_to_move)
    files_to_move = [e for e in files_to_move if filename not in e]
    print("Post ", files_to_move)

    for file in files_to_move:
        cmd = "scp -i {} -P 2222 {} protick@pharah.cs.vt.edu:{}{}".format(rsa_loc, file, dest_pharah_dir, machine_name)
        ans = execute_cmd(cmd)
        print("Deleting ", file)
        print("Result ", ans[1])
        if ans[1] is None:
            cmd = "rm {}".format(file)
            execute_cmd(cmd)
            print("moved and deleted {}".format(file))



def get_options(browser_mode, ocsp_mode):
    from selenium.webdriver.firefox.options import Options
    options = Options()
    options.headless = True
    options.set_preference('security.pki.crlite_mode', 0)
    options.set_preference('security.tls.version.max', 3)
    return options

def get_websites():
    websites = []
    with open('data/top-1m.csv') as read_obj:
        csv_reader = reader(read_obj)
        index = 0
        for row in csv_reader:
            index = index + 1
            # if index == 1:
            #     continue
            websites.append(row[1])
    return websites


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

# mode = 1 (cold cache)
# mode = 2 (warm cache)
# mode = 3 (normal)

def get_browser(browser_mode, options, ocsp_mode):
    try:
        #print("lul")
        if browser_mode == 'firefox':
            #print("gul")
            browser = webdriver.Firefox(executable_path="drivers/geckodriver", options=options)
            #print("uu")
        elif browser_mode == 'chrome':
            browser = webdriver.Chrome(executable_path="drivers/chromedriver", options=options)
        elif browser_mode == 'edge':
            # 100.0.1156.1/edgedriver_linux64.zip
            browser = webdriver.Edge(executable_path="drivers/msedgedriver", options=options)
        #print("lul")
        return browser
    except Exception as e:
        print( "ola", e)

def load_website(browser, website):
    print("Loading ", website)
    browser.set_page_load_timeout(6)
    browser.get("https://{}".format(website))
    print(browser.title)
    time.sleep(.5)
    browser.quit()

def complete_chunk(chunk, browser_mode, filename, chunk_start_index, ocsp_mode, mode):
    temp_index = chunk_start_index - 1
    for website in chunk:
        try:
            temp_index = temp_index + 1
            options = get_options(browser_mode, ocsp_mode)
            browser = get_browser(browser_mode, options, ocsp_mode)
            logger.info('{}-{}, Rank: {}, Domain: {}, start: {}'.format(mode, ocsp_mode, temp_index, website, time.time()))
            load_website(browser, website)

            logger.info('{}-{}, Rank: {}, Domain: {}, end: {}'.format(mode, ocsp_mode, temp_index, website, time.time()))
        except Exception as e:
            try:
                browser.quit()
            except Exception as e:
                pass


def proc_chunk_entry(chunk, chunk_start_index, chunk_end_index, mode, browser_mode):
    # TODO add one -> all on : crlite also on
    for ocsp_mode in ['stapledon']:
        try:
            filename = "{}-{}-{}.pcap".format(ocsp_mode, chunk_start_index, chunk_end_index)
            print("File name", filename)
            p = start_tcp_dump(filename=filename)
            complete_chunk(chunk, browser_mode, filename, chunk_start_index, ocsp_mode=ocsp_mode, mode=mode)
            end_tcp_dump(p)
            mv_files(filename)
        except Exception as e:
            pass

def runner(browser_mode, mode):

    websites = get_websites()
    website_chunks = list(divide_chunks(websites, split))

    '''
        Name tcpdump
        mv files
        modes
    '''
    starting_chunk_index, ending_chunk_index = 0, len(website_chunks) - 1

    #
    while starting_chunk_index != ending_chunk_index:
        #print("in")
        next_index = starting_chunk_index + 1
        try:

            proc_chunk_entry(website_chunks[starting_chunk_index], starting_chunk_index * split + 1,
                             starting_chunk_index * split + split, mode, browser_mode)
        except Exception as e:
            print(e)
            pass
        # proc_chunk_entry(website_chunks[ending_chunk_index], ending_chunk_index * split + 1, min(ending_chunk_index * split + split, len(websites)), mode, browser_mode)

        starting_chunk_index = next_index
        # ending_chunk_index = ending_chunk_index - 1


parser = argparse.ArgumentParser()
parser.add_argument('--mode', type=str, required=True)
# parser.add_argument('--dest', type=str, required=True)
parser.add_argument('--name', type=str, required=True)
args = parser.parse_args()

# python3 browser_tester_firefox_ec2.py --mode normal  --name oregon


# print(args)

# dest_dir = args.dest
machine_name = args.name
runner('firefox', args.mode)

# dest_dir = 'dest/'
# runner('firefox', 'cold')

'''
    check if the commands work !!
    check if the pcap folder is there
'''

'''
run the containers
make log file
press yes


run 
python3 browser_tester_firefox_for_range.py --mode normal --dest /source/ --id 4

'''



