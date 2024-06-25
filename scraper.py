import aiohttp, asyncio
import json, time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as chromeoptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class JobScraper:
    def __init__(self, skills,):
        self.jobs = {}
        self.skills = skills
        self.user_agent = UserAgent()
        options = chromeoptions()
        options.add_argument('--headless')  
        options.add_argument('--disable-gpu')  
        options.add_argument('--no-sandbox')  
        options.add_argument('--disable-dev-shm-usage')  
        options.add_argument(f'user-agent={self.user_agent.random}')  
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    async def get_info(self, session, url):
        async with session.get(url, headers={'User-Agent': self.user_agent.random}) as response:
            try:
                response.raise_for_status()
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')

                elements = soup.select('div.gws-plugins-horizon-jobs__tl-lif')
                if not elements:
                    print("No job elements found")
                    return

                # Open the main page in Selenium
                self.driver.get(url)
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.gws-plugins-horizon-jobs__tl-lif'))
                )

                # Clicking one job to load the jobs
                job_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.gws-plugins-horizon-jobs__tl-lif')
                job_elements[0].click()
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.ID, 'gws-plugins-horizon-jobs__job_details_page'))
                )

                # Extracting HTML and parsing with BeautifulSoup
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')

                # Getting the links and job description with Selenium
                try:

                    '''# Debug: Print the page source to verify if it's updated
                    with open(f"page_source_{index}.html", "w", encoding="utf-8") as f:
                        f.write(page_source)'''
                    
                    elements = soup.select('#gws-plugins-horizon-jobs__job_details_page ')

                    for element in elements:

                        try:
                            title = element.select_one('div.sH3zFd > h2').text.strip()
                        except Exception as e:
                            title = 'Error'
                            print(f'Error on title: {e}')
                        try:
                            company = element.select_one('div.nJlQNd.sMzDkb').text.strip()
                        except Exception as e:
                            company = 'Error'
                            #print(f'Error on company: {e}')
                        try:
                            place = element.select_one('div.tJ9zfc > div:nth-child(2)').text.strip()
                        except Exception as e:
                            place = 'Not mentioned'
                            #print(f'Error on place: {e}')
                        try:
                            salary = element.select_one('div.I2Cbhb.bSuYSc > span.LL4CDc').text.strip()
                        except Exception as e:
                            salary = 'Not mentioned'
                            #print(f'Error on salary: {e}')
                        try:
                            shedule = element.select_one('span.LL4CDc[aria-label*="Tipo"]').text.strip()
                        except Exception as e:
                            shedule = 'Not mentioned'
                            #print(f'Error on shedule: {e}')
                        try:
                            published = element.select_one('span.LL4CDc[aria-label^="Publicado"]').text.strip()
                        except Exception as e:
                            published = 'Weeks ago'
                            #print(f'Error on published date: {e}')
                        try:
                            description = element.select_one('#gws-plugins-horizon-jobs__job_details_page > div > div:nth-child(5) > g-expandable-container > div > div > div > span').text.strip()
                        except Exception as e:
                            description = element.select_one('#gws-plugins-horizon-jobs__job_details_page > div > div:nth-child(5) > g-expandable-container > div > div > span').text.strip()
                            #print(f'Error on description: {e}')

                        try:
                            link_container = element.select_one('div.B8oxKe.BQC79e.xXyUwe')
                            job_urls = []
                            links = link_container.find_all('a') if link_container else []
                            for link in links:
                                job_urls.append(link.get('href'))
                            
                        except Exception as e:
                            job_urls = 'Error'
                            #print(f'Error on published date: {e}')
                        

                        self.jobs[title] = {
                            'Company': company,
                            'Place': place,
                            'Salary': salary,
                            'Schedule': shedule,
                            'Published': published,
                            'URLs': job_urls,
                            'Description': description
                        }

                except Exception as e:
                    print(f"Error occurred while getting job: {e}")


            except aiohttp.ClientResponseError as e:
                print(f"Failed to access the page. ClientResponseError: {e}")

    # Async function to complete all the tasks
    async def get_all_jobs(self):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=1)) as session:
            queries = f'{self.skills}'
            url = f'https://www.google.com/search?q={queries.replace(" ", "+")}&&oq=trab&ibp=htl;jobs&sa=X'
            print(url)
            await self.get_info(session, url)
    
    # Saving the results on a JSON file
    def save_to_json(self, output_file='jobs.json'):
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(self.jobs, json_file, indent=4, ensure_ascii=False)

# Main function
async def main(skills):
    scraper = JobScraper(skills)
    await scraper.get_all_jobs()
    scraper.save_to_json()
    scraper.driver.quit()

# ------------------ T E S T I N G -----------
'''if __name__ == "__main__":
    inicio = time.time()
    print('Loading...')

    # User parameters
    qskills = 'java python'  

    asyncio.run(main(skills=qskills))

    fin = time.time()
    print(f"Complete: {fin - inicio} seconds")'''
