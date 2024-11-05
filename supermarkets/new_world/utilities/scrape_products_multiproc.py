import subprocess
import pathlib
import datetime
import json
import os
import agolia
import sys
from multiprocessing import Process, Queue

class NewWorldScraper:
    def __init__(self, department, base_url, headers_file):
        self.department = department
        self.base_url = base_url
        self.headers = self._load_headers(headers_file)
        self.batch_size = 10
        self.data_dir = pathlib.Path('./data/')
        self.tmp_dir = pathlib.Path('./data/.tmp/')
        self.formatted_date = datetime.datetime.now().strftime("%Y-%m-%d")

    def _load_headers(self, headers_file):
        headers = {}
        with open(headers_file) as f:
            for line in f:
                parts = line.strip().split(':', 1)
                if len(parts) == 2:
                    headers[parts[0].strip()] = parts[1].strip()
        return headers

    def _construct_command(self, page):
        agolia_query = agolia.generate_query(self.department, page)
        command = ['http', 'POST', self.base_url]
        header_args = [f"'{key}:{value}'" for key, value in self.headers.items()]
        return ' '.join(command + header_args + agolia_query)

    def _execute_command(self, command, page):
        os.makedirs(f'{self.tmp_dir}/{self.formatted_date}/{self.department}', exist_ok=True)
        tmp_file = f'{self.tmp_dir}/{self.formatted_date}/{self.department}/{self.department}_{page}.json'
        pipeline_command = f"{command} | jq '.' > '{tmp_file}'"
        print(f"Executing: {pipeline_command}")
        
        result = subprocess.run(pipeline_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            print(f"Error occurred: {result.stderr}")
            return None
        
        print(f"Command executed successfully. Output saved to {tmp_file}")
        return tmp_file

    def _is_response_empty(self, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        return len(data.get('products', [])) == 0

    def scrape_range(self, start_page, queue):
        page = start_page
        while True:
            command = self._construct_command(page)
            tmp_file = self._execute_command(command, page)
            
            if tmp_file is None:
                print(f"Error occurred while scraping page {page}")
                queue.put(None)
                break
            
            if self._is_response_empty(tmp_file):
                print(f"Reached empty response at page {page}")
                os.remove(tmp_file)
                queue.put(None)
                break
            
            os.makedirs(f'{self.data_dir}/{self.formatted_date}/{self.department}', exist_ok=True)
            final_file = f'{self.data_dir}/{self.formatted_date}/{self.department}/{self.department}_{page}.json'
            os.rename(temp_file, final_file)
            print(f"Successfully scraped page {page}")
            queue.put(page)
            page += self.batch_size

def scraper_process(scraper, start_page, queue):
    scraper.scrape_range(start_page, queue)

if __name__ == "__main__":
    base_url = "https://api-prod.newworld.co.nz/v1/edge/search/paginated/products"
    headers_file = 'headers'

    departments = []
    with open('product_departments.json', 'r') as f:
        _ = json.load(f)
        for department in _['Departments']:
            departments.append(department)

    for department in departments:
        scraper = NewWorldScraper(department, base_url, headers_file)

        processes = []
        queues = []

        for i in range(scraper.batch_size):
            queue = Queue()
            process = Process(target=scraper_process, args=(scraper, i, queue))
            processes.append(process)
            queues.append(queue)
            process.start()

        # Wait for all processes to finish
        for process in processes:
            process.join()

        # Check if any process encountered an empty response
        should_stop = False
        for queue in queues:
            if queue.get() is None:
                should_stop = True
                break

        if should_stop:
            print("Scraping completed. Empty response encountered.")
        else:
            print("Scraping completed successfully.")
