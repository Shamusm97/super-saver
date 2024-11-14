import argparse
import sys
import json
from multiprocessing import Process, Queue
import pathlib

# Import your scraper classes
from scrapers import PaknSaveScraper, NewWorldScraper, WoolworthsScraper

def parse_arguments():
    parser = argparse.ArgumentParser(description='Supermarket Product Scraper')
    parser.add_argument(
        '--store',
        type=str,
        required=True,
        choices=['paknsave', 'newworld', 'woolworths'],
        help='Store to scrape from'
    )
    parser.add_argument(
        '--department',
        type=str,
        required=True,
        help='Department to scrape products from or "all" to scrape all departments'
    )
    parser.add_argument(
        '--processes',
        type=int,
        default=10,
        help='Number of parallel processes to use (default: 10)'
    )

    return parser.parse_args()

def load_departments(store):
    # Get the directory where the module is located
    module_dir = pathlib.Path(__file__).parent
    departments_file = module_dir / f'{store}_departments.json'

    if not departments_file.exists():
        print(f"Error: Departments file '{departments_file}' does not exist")
        sys.exit(1)

    try:
        with open(departments_file) as f:
            data = json.load(f)
            departments = data.get('Departments', [])
            if not departments:
                print("Error: No departments found in the JSON file")
                sys.exit(1)
            return departments
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {departments_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading departments file: {e}")
        sys.exit(1)

def run_scraper(scraper_class, department, start_page, queue):
    scraper = scraper_class(department)
    scraper.scrape_range(start_page, queue)

def scrape_department(scraper_class, department, num_processes):
    processes = []
    queues = []

    # Start multiple processes with different starting pages
    for i in range(num_processes):
        queue = Queue()
        process = Process(
            target=run_scraper,
            args=(
                scraper_class,
                department,
                i,  # Each process starts at a different page
                queue
            )
        )
        processes.append(process)
        queues.append(queue)
        process.start()

    # Wait for all processes to complete
    for process in processes:
        process.join()

    # Check results from all queues
    completed_pages = set()
    for queue in queues:
        while not queue.empty():
            page = queue.get()
            if page is not None:
                completed_pages.add(page)

    return len(completed_pages)

def main():
    args = parse_arguments()

    # Get departments to scrape
    departments = []
    if args.department.lower() == 'all':
        departments = load_departments(args.store)
    else:
        departments = [args.department]

    # Map store names to scraper classes
    scrapers = {
        'paknsave': PaknSaveScraper,
        'newworld': NewWorldScraper,
        'woolworths': WoolworthsScraper
    }

    scraper_class = scrapers[args.store]

    total_departments = len(departments)
    print(f"Starting scraping for {total_departments} department(s) from {args.store}")

    # Process each department
    total_pages = 0
    for i, department in enumerate(departments, 1):
        print(f"\nProcessing department {i}/{total_departments}: {department}")
        pages = scrape_department(
            scraper_class,
            department,
            args.processes
        )
        total_pages += pages
        print(f"Completed {department}: {pages} pages scraped")

    print(f"\nScraping completed.")
    print(f"Successfully scraped {total_pages} total pages across {total_departments} departments from {args.store}")

if __name__ == '__main__':
    main()
