import subprocess
import json
import os

class WoolworthsScraper:
    def __init__(self, department, base_url, headers_file):
        self.department = department
        self.base_url = base_url
        self.headers = self._load_headers(headers_file)
        self.page = 1
        self.in_stock = 'false'
        self.size = 48

    def _load_headers(self, headers_file):
        headers = {}
        with open(headers_file) as f:
            for line in f:
                parts = line.strip().split(':', 1)
                if len(parts) == 2:
                    headers[parts[0].strip()] = parts[1].strip()
        return headers

    def _construct_command(self):
        command = [
            'http',
            'GET',
            self.base_url,
            f"dasFilter=='Department;;{self.department};false'",
            f'target==browse',
            f'page=={self.page}',
            f'inStockProductsOnly=={self.in_stock}',
            f'size=={self.size}'
        ]
        header_args = [f"'{key}:{value}'" for key, value in self.headers.items()]
        return ' '.join(command + header_args)

    def _execute_command(self, command):
        # Make the tmp output directory
        os.makedirs(f'./data/.tmp/{self.department}', exist_ok=True)
        output_file = f'./data/.tmp/{self.department}/{self.department}_{self.page}.json'
        pipeline_command = f"{command} | jq '.' > {output_file}"
        print(f"Executing: {pipeline_command}")
        
        result = subprocess.run(pipeline_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            print(f"Error occurred: {result.stderr}")
            return None
        
        print(f"Command executed successfully. Output saved to {output_file}")
        return output_file

    def _is_response_empty(self, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        return len(data.get('products', {}).get('items', [])) == 0

    def scrape(self):
        while True:
            command = self._construct_command()
            temp_file = self._execute_command(command)
            
            if temp_file is None:
                print(f"Error occurred while scraping page {self.page}")
                break
            
            if self._is_response_empty(temp_file):
                print(f"Reached empty response at page {self.page}")
                os.remove(temp_file)
                break
            
            os.makedirs(f'./data/{self.department}', exist_ok=True)
            final_file = f'./data/{self.department}/{self.department}_{self.page}.json'
            os.rename(temp_file, final_file)
            print(f"Successfully scraped page {self.page}")
            self.page += 1

if __name__ == "__main__":
    base_url = 'https://www.woolworths.co.nz/api/v1/products'
    headers_file = 'headers'
    department = 'halloween'

    scraper = WoolworthsScraper(department, base_url, headers_file)
    scraper.scrape()
