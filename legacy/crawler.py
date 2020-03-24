from tbselenium.tbdriver import TorBrowserDriver
from selenium.common.exceptions import WebDriverException as WebDriverException
class TorCrawler():

    def __init__(self, driver_path):
        self.driver = self.open_tor_browser(driver_path)


    def open_tor_browser(self,driver_path):
        driver = None
        try:
            driver = TorBrowserDriver(driver_path,
                                      tbb_logfile_path="./tor_browser_log.txt")
            print("[BROWSER_SUCCESS] Tor Browser Open Connectiong to Hidden Service ...")
        except WebDriverException:
            print("[BROWSER_ERROR] Tor Browser Open Error! Try Reopening ...")
        return driver

    def collect_main_page(self):
        self.driver.get("http://highkorea5ou4wcy.onion")
        html = self.driver.page_source
        scripts = self.driver.find_elements_by_tag_name("script")
        for script in scripts:
            print(script.get_attribute("src"))
        csses = self.driver.find_elements_by_tag_name("link")
        print(csses)




    def collect_related_file(self):
        """
        자바스크립트같은 연관 파일을 모두 가져온다.
        """

    def main(self):
        self.collect_main_page()



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--driver", "-d",
                        help="input tor browser driver path directory")
    args = parser.parse_args()

    crawling = TorCrawler(args.driver)
    crawling.main()
