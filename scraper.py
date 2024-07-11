import aiohttp, asyncio, json, time
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
    def __init__(self, skills, place, type):
        self.jobs = {}
        self.skills = skills
        self.place = place
        self.type = type
        self.user_agent = UserAgent()

        #Selenium optioms
        options = chromeoptions()
        options.add_argument('--incognito')
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
                
                try:
                    # Open the main page in Selenium
                    self.driver.get(url)
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.gws-plugins-horizon-jobs__tl-lif'))
                    )
                except Exception as e:
                    #print(f"Timeout waiting for the main page: {e}")
                    #print(self.driver.page_source)  # Print the page source for debugging
                    return

                # Clicking one job to load more jobs
                job_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.gws-plugins-horizon-jobs__tl-lif')
                job_elements[0].click()
                try: 
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'gws-plugins-horizon-jobs__job_details_page'))
                    )
                except Exception as e:
                    print(f"Timeout waiting for job details page: {e}")
                    #print(self.driver.page_source)  # Print the page source for debugging
                    return

                # Parsing the HTML with BeautifulSoup
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')

                try:
                    #Collecting all the jobs and extract their information with BS4
                    elements = soup.select('#gws-plugins-horizon-jobs__job_details_page ')

                    for element in elements:
                        try:
                            title = element.select_one('div.sH3zFd > h2').text.strip()
                        except:
                            title = 'Error'
                            print(f'Error on title: {e}')
                        try:
                            company = element.select_one('div.nJlQNd.sMzDkb').text.strip()
                        except:
                            company = 'Error'
                        try:
                            place = element.select_one('div.tJ9zfc > div:nth-child(2)').text.strip()
                        except:
                            place = 'Not mentioned'
                        try:
                            salary = element.select_one('div.I2Cbhb.bSuYSc > span.LL4CDc').text.strip()
                        except:
                            salary = 'Not mentioned'
                        try:
                            shedule = element.select_one('span.LL4CDc[aria-label*="Tipo"]').text.strip()
                        except:
                            shedule = 'Not mentioned'
                        try:
                            published = element.select_one('span.LL4CDc[aria-label^="Publicado"]').text.strip()
                        except:
                            published = 'Weeks ago'
                        try:
                            description = element.select_one('#gws-plugins-horizon-jobs__job_details_page > div > div:nth-child(5) > g-expandable-container > div > div > div > span').text.strip() #Long description
                        except:
                            description = element.select_one('#gws-plugins-horizon-jobs__job_details_page > div > div:nth-child(5) > g-expandable-container > div > div > span').text.strip() #Short description

                        try:
                            link_container = element.select_one('div.B8oxKe.BQC79e.xXyUwe')
                            job_urls = []
                            links = link_container.find_all('a') if link_container else []
                            for link in links:
                                job_urls.append(link.get('href'))
                        except:
                            job_urls = 'Error'
                        
                        #Saving the jobs on a dictionary
                        self.jobs[title] = {
                            'Company': company,
                            'Place': place,
                            'Salary': salary,
                            'type': shedule,
                            'Published': published,
                            'URLs': job_urls,
                            'Description': description
                        }

                except Exception as e:
                    print(f"Error occurred while getting job: {e}")


            except aiohttp.ClientResponseError as e:
                print(f"Failed to access the page. ClientResponseError: {e}")

    # Async function
    async def get_all_jobs(self):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector()) as session:
            queries = f'{self.skills},{self.place}'
            url = f'https://www.google.com/search?q={queries.replace(",", "+").replace(" ", "+")}&oq=trab&ibp=htl;jobs&sa=X#htivrt=jobs&fpstate=tldetail&htichips=employment_type:{self.type}&htischips=employment_type;{self.type}'
            print(url)
            await self.get_info(session, url)

            # If no jobs found for the city, try without the city
            if not self.jobs:
                queries = f'{self.skills}'
                url = f'https://www.google.com/search?q={queries.replace(",", "+").replace(" ", "+")}&oq=trab&ibp=htl;jobs&sa=X#htivrt=jobs&fpstate=tldetail&htichips=employment_type:{self.type}&htischips=employment_type;{self.type}'
                print(f"Retrying without '{self.place}', new url: {url}")
                await self.get_info(session, url)
        
    # Saving the results on a JSON file [jobs.json]
    def save_to_json(self, output_file='jobs.json'):
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(self.jobs, json_file, indent=4, ensure_ascii=False)

# Main function
async def main(skills,place, type):
    scraper = JobScraper(skills, place, type)
    await scraper.get_all_jobs()
    scraper.save_to_json()
    scraper.driver.quit()

# ------------------ T E S T I N G -----------
if __name__ == "__main__":
    inicio = time.time()
    print('Loading...')

    # User parameters [skills - type - place]:
    qskills = 'python'   #Jobs Skills [example: python sql], just write the main words.
    qplace = 'Canada'    #City of the job [example: CDMX] , if you don't insert an option the scraper would show the trending jobs.
    qtype = 'FULLTIME' #Type of job [FULLTIME or PARTTIME], if you don't insert an option the scraper would show the trending jobs.

    asyncio.run(main(skills=qskills, place=qplace, type=qtype))

    fin = time.time()
    print(f"Complete: {fin - inicio} seconds")
