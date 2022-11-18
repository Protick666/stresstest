import subprocess
import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from csv import reader

split = 5

source_dir = "pcap/"
dest_dir = "dest/"


def start_tcp_dump(filename):
    return
    p = subprocess.Popen(["sudo" ,"tcpdump", "-w", "{}{}".format(source_dir, filename)], stdout=subprocess.PIPE)
    time.sleep(.5)
    return p

def end_tcp_dump(p):
    return
    p.terminate()

def execute_cmd(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return output, error

def mv_files(filename):
    return
    cmd = "mv {}{} {}".format(source_dir, filename, dest_dir)
    ans = execute_cmd(cmd)
    if ans[1] is None:
        cmd = "rm {}{}".format(source_dir, filename)
        execute_cmd(cmd)


def get_options(browser_mode):
    if browser_mode == 'firefox':
        from selenium.webdriver.firefox.options import Options
        options = Options()
        options.headless = True
        options.set_preference('security.pki.crlite_mode', 0)
        #options.set_preference("network.dns.forceResolve", "1.1.1.1")
        # profile = webdriver.FirefoxProfile()
        # profile.set_preference('security.pki.crlite_mode', 0)
        # options.set_preference('security.pki.crlite_mode', 0)
        # options.set_preference('security.ssl.enable_ocsp_stapling', False)
        return options
    elif browser_mode == 'opera':
        from selenium.webdriver.chrome.options import Options
        options = Options()
        return options
    elif browser_mode == 'chrome':
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_experimental_option(
            'prefs', {
                'ssl.rev_checking.enabled': 'true'
            }
        )
        options.headless = True
        return options
    elif browser_mode == 'edge':
        from selenium.webdriver.edge.options import Options
        options = Options()
        # options.add_experimental_option("EnableOnlineRevocationChecks", True)
        options.headless = True
        return options


def get_websites():
    websites = []
    with open('data/top-1m.csv') as read_obj:
        csv_reader = reader(read_obj)
        index = 0
        for row in csv_reader:
            index = index + 1
            if index == 1:
                continue
            websites.append(row[1])
    return websites


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

# mode = 1 (cold cache)
# mode = 2 (warm cache)
# mode = 3 (normal)

def get_browser(browser_mode, options):
    try:
        print("lul")
        if browser_mode == 'firefox':
            print("gul")
            browser = webdriver.Firefox(executable_path="drivers/geckodriver", options=options)
            print("uu")
        elif browser_mode == 'chrome':
            browser = webdriver.Chrome(executable_path="drivers/chromedriver", options=options)
        elif browser_mode == 'edge':
            # 100.0.1156.1/edgedriver_linux64.zip
            browser = webdriver.Edge(executable_path="drivers/msedgedriver", options=options)
        print("lul")
        return browser
    except Exception as e:
        print("ku", e)

def load_website(browser, website):
    browser.set_page_load_timeout(4)
    a = browser.get("https://{}".format(website))
    time.sleep(.5)
    browser.quit()

def complete_chunk(chunk, browser_mode, filename):
    for website in chunk:
        try:
            print("1")
            options = get_options(browser_mode)
            print("2")
            browser = get_browser(browser_mode, options)
            print("3")
            load_website(browser, website)
            print("4")
            # print("Done with {} - {}".format(website, index))

        except Exception as e:
            print("mama")
            print(e, website)
            try:
                browser.quit()
            except Exception as e:
                pass


def runner(browser_mode, mode):
    websites = get_websites()
    website_chunks = list(divide_chunks(websites, split))

    # 6367
    '''
        Name tcpdump
        mv files
        modes
    '''

    import random
    #websites = random.sample(websites, 50)

    chunk_start_index = 1
    for chunk in website_chunks:
        try:
            filename = "{}-{}.pcap".format(chunk_start_index, chunk_start_index + split - 1)
            if mode == 'normal' or mode == 'cold':
                p = start_tcp_dump(filename=filename)
                complete_chunk(chunk, browser_mode, filename)
                end_tcp_dump(p)
                mv_files(filename)
            elif mode == 'warm':
                complete_chunk(chunk, browser_mode, filename)
                p = start_tcp_dump(filename=filename)
                complete_chunk(chunk, browser_mode, filename)
                end_tcp_dump(p)
                mv_files(filename)

            chunk_start_index = chunk_start_index + split
        except Exception as e:
            pass

# parser = argparse.ArgumentParser()
# parser.add_argument('--mode', type=str, required=True)
# parser.add_argument('--dest', type=str, required=True)
# args = parser.parse_args()
# print(args)
# dest_dir = args.dest
# runner('firefox', args.mode)

dest_dir = 'dest/'
runner('firefox', 'cold')




