import unittest
import asyncio
from scraper import JobScraper
import aiohttp

class TestJobScraper(unittest.TestCase):
    async def run_scraper(self, skills, place, job_type):
        scraper = JobScraper(skills, place, job_type)
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector()) as session:
            queries = f'{skills},{place}'
            url = f'https://www.google.com/search?q={queries.replace(",", "+").replace(" ", "+")}&oq=trab&ibp=htl;jobs&sa=X#htivrt=jobs&fpstate=tldetail&htichips=employment_type:{job_type}&htischips=employment_type;{job_type}'
            await scraper.get_info(session, url)
        scraper.driver.quit()
        return scraper.jobs #Run the scraper

# this function extract the skills for the job
    def test_get_info(self):
        skills = ""
        place = ""
        job_type = "FULLTIME"

        jobs = asyncio.run(self.run_scraper(skills, place, job_type))

        # It verifies of there is a dictoniary, if not will give an error
        self.assertIsInstance(jobs, dict)
        self.assertTrue(len(jobs) > 0, "No jobs found")
        
        #print the jobs
        print("Jobs data:\n", jobs)

if __name__ == '__main__':
    unittest.main()

