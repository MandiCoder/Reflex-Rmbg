import json
import requests
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup




class WebDriver():

    def __init__(self) -> None:
        self.driver = self.iniciar_chrome()
    
    def iniciar_chrome(self):
        ruta = ChromeDriverManager().install()
        print(f'Path ChromeDriver: {ruta}')
        
        # OPCIONES DE CHROME
        options = Options()
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument('--disable-web-security')
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--window-size=300, 768')
        options.add_argument('--disable-notifications')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--no-sandbox')
        options.add_argument('--log-level=3')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--no-default-browser-check')
        options.add_argument('--no-first-run')
        options.add_argument('--no-proxy-server')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        exp_opt = [
            'enable-automation',
            'ignore-certificate-errors',
            'enable-logging'
        ]
        
        prefs = {
            'profile.default_content_setting_values.notifications' : 2,
            'intl.accept_languages' : ['es-ES', 'es'],
            'credentials_enable_service' : False
        }
        
        options.add_experimental_option('excludeSwitches', exp_opt)
        options.add_experimental_option('prefs', prefs)
        
        s = Service(ruta)
        driver = webdriver.Chrome(service=s, options=options)
        driver.set_window_position(0, 0)
        
        return driver
    
    # ******************************************************************** LOAD PAGES
    
    def load_page(self):
        self.driver.get('https://www.curseforge.com/minecraft/search?page=1&pageSize=20&sortBy=popularity&class=mc-mods&version=1.20.1')
        html = self.driver.page_source
        
        soup = BeautifulSoup(html, 'html.parser')
        elementos = soup.find_all(class_="project-card")
        
        for i in elementos:
            url_root = f"https://www.curseforge.com/{i.find('a').get('href')}"
            self.search_mod(url_root)
            
            
    
    
    def search_mod(self, url:str) -> dict:
        self.driver.get(url)
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
    
        script = soup.find('script', id='__NEXT_DATA__').text
        diccionario = json.loads(script)
        datos = diccionario['props']['pageProps']['searchResult']['data']
     
        full_data = {}
        
        for mod in datos: 
            url_avatar = mod['avatarUrl']
            description = mod['summary']
            name = mod['name']
            page_size = 5
            url_screenshots = f"https://www.curseforge.com/minecraft/mc-mods/{mod['slug']}/screenshots" 

            try:
                list_screenshots = self.get_screenshots(url_screenshots)
            except:
                pass
            
            id = mod['id']
            url = f"https://www.curseforge.com/api/v1/mods/{id}/files?pageIndex=0&pageSize={page_size}&sort=dateCreated&sortDescending=true&removeAlphas"

            dic_list = []
            
            resp = requests.get(url).json()
            for dat in resp['data']:
                if "Forge" in dat['gameVersions']:
                  
                    file_name = dat['fileName']
                    file_id = str(dat['id'])
                    id_format = f"{file_id[:4]}/{file_id[-3:]}"
                    url_download = f"https://mediafilez.forgecdn.net/files/{id_format}/{file_name}"    
                    
                    dic_list.append({
                        'url_download'    : url_download,
                        'game_version' : "_".join(dat['gameVersions'])
                    })
                    
            full_data[name] = {
                "dic_list" : dic_list,
                "list_screenshots" : list_screenshots,
                "description" : description,
                "url_avatar" : url_avatar,
            }
            
        return full_data

    def get_screenshots(self, url):
        self.driver.get(url)
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        img_tag = soup.find_all('img', alt='Screenshot thumbnail')

        url_list = []
        for i in img_tag:
            img_url = i['src']
            url_list.append(img_url)
        
        return url_list