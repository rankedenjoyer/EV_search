import scrape.constants as const
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
class Scrape(webdriver.Chrome):
    def __init__(self):
        self.path = Service(r'C:\Users\ASUS TUF\Downloads\chromedriver_win32\chromedriver.exe')
        self.op = webdriver.ChromeOptions()
        self.op.add_experimental_option("detach", True)
        super(Scrape, self).__init__(service=self.path, options=self.op)

    def land_first_page(self):
        self.get(const.BASE_URL)

    def get_esports(self):
        self.implicitly_wait(3)
        self.find_element(By.XPATH, '//a[@href="/sports/esports"]').click()

    def get_name(self):
        teams = self.find_elements(By.XPATH, '//div[@data-testid="price-button-name"]/span[1]')
        new_teams = []
        for name in teams:
            new_teams.append(name.text)
        return new_teams

    def get_event(self):
        events = self.find_elements(By.XPATH, '//div[@data-testid="sports-event-subtitle"]')
        store_events = []
        for event in events:
            store_events.append(event.text)
        return store_events
    def get_odds(self):
        odds = self.find_elements(By.XPATH, '//div[@class="price-button-odds-price"]/span[1]')
        new_odds = []
        for odd in odds:
            temp = float(odd.text)
            if temp >= 2:
                temp = '+' + str(int((temp - 1) * 100))
            else:
                temp = str(int(-100 / (temp - 1)))
            new_odds.append(temp)
        return new_odds

    def land_calculator(self):
        self.get(const.CAL_URL)

    def choose_method(self):
        self.find_element(By.XPATH, '//input[@id="RadioButtonListDevigMethod_4"]').click()

    def add_leg_odds(self, event_odds):
        box = self.find_element(By.XPATH, '//input[@name="TextBoxLegOdds"]')
        box.clear()
        box.send_keys(str('/'.join(event_odds)))

    def add_final_odds(self, odd):
        box = self.find_element(By.XPATH, '//input[@name="TextBoxFinalOdds"]')
        box.clear()
        box.send_keys(odd)

    def calculate(self):
        button = self.find_element(By.XPATH, '//input[@id="ButtonCalculate"]')
        self.execute_script("arguments[0].click();", button)
    def get_EV(self):
        summary = self.find_element(By.XPATH, '//span[@id="LabelOutput"]').text
        summary = summary.split()
        pos = summary.index("EV%")
        if float(summary[pos + 2]) > 0:
            message = summary[pos] + summary[pos + 1] + summary[pos + 2] + summary[pos + 3]
            return message
        return 0








