import time
import random
# from features.chrome_driver.utils import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumwire import webdriver as wire_webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

class HEYGEN_DRIVER_:

    def __init__(self, driver, profile): 
        self.driver = driver
        self.profile = profile
        self.actions = ActionChains(driver)


    # Check If user logedin
    def isLogedin(self):
        try:
            avatar_nav_page = "//*[contains(@class, 'home-layout-nav')]"
            self.wait_and_presence_verify(avatar_nav_page, waitRange=(2,4), timout=7)
            return True
        except Exception as e:
            return False

    
    def random_time_sleep(self, a, b):
        time.sleep(random.uniform(a, b))
        return
    


    # Loging To Heygen Acciunt
    def login(self):
        try:
            USERNAME_INPUT = "//input[@id='username']"
            PASSWORD_INPUT = "//input[@id='password']"
            SIGNIN_BUTTON  = "//*[text()='Sign In']"

            user_obj = self.wait_and_presence_verify(USERNAME_INPUT, waitRange=(1,2), timout=15)
            self.fill_inputs(self.profile['username'], user_obj)

            pass_obj = self.wait_and_presence_verify(PASSWORD_INPUT, waitRange=(1,2), timout=10)
            self.fill_inputs(self.profile['password'], pass_obj)
            
            self.wait_and_presence_verify(SIGNIN_BUTTON, waitRange=(1,2), timout=10).click()
            self.random_time_sleep(2, 3)

        except Exception as e:
            raise Exception(f"Login Failed! {e}")

    
    # Wait For Presence of Element on screen | return obj
    def wait_and_presence_verify(self, xpath=None, waitRange=(0.01, 0.04), timout=20 ):
        self.random_time_sleep(waitRange[0], waitRange[1])
        WebDriverWait(self.driver, timeout=timout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return self.driver.find_element(By.XPATH, xpath)


    # Wait For Element to be clickable | return obj
    def wait_and_clickable_verify(self, xpath=None, waitRange=(0.01, 0.04), timout=20):
        self.random_time_sleep(waitRange[0], waitRange[1])
        WebDriverWait(self.driver, timeout=timout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        return self.driver.find_element(By.XPATH, xpath)


    # Fill inputs feild & adding some delay time in range (random)
    def fill_inputs(self, value, element, waitRange=(0.04, 0.06)):
        element.click()
        for i in value:
            element.send_keys(i)
            self.random_time_sleep(waitRange[0], waitRange[1])


    # Go to Avatar Photo page
    def open_avatar_photo_page(self):  
        try:
            avatar_nav_page_photo = "//*[text()='Photo Avatar']"
            self.wait_and_presence_verify(avatar_nav_page_photo).click()
        except Exception as e:
            raise Exception(f"Opening Avatar Photo Page Failed! {e}")      


    # Go to Avatar Video page
    def open_avatar_video_page(self):
        try:
            avatar_nav_page_video = "//*[text()='Video Avatar']"
            self.wait_and_presence_verify(avatar_nav_page_video).click()
        except Exception as e:
            raise Exception(f"Opening Avatar Video Page Failed! {e}")  


    # Upload Photo Avatar using selenium driver
    def upload_photo_avatar(self, avatar_name, avatar_path):
        try:
            create_photo_avator = "//*[text()='Create Photo Avatar']"
            upload_photo_avator = "//*[contains(@src, 'generate-photo-avatar-by-upload2') ]"
            upload_photo_input  = "//input[contains(@accept, 'image/png,image/jpeg,image/jpg,image/webp') ]"
            upload_photo_button = "//div[@class='rc-dialog-body']//*[text()= 'Upload' ]"
            avart_photo_name    = "//input[contains(@placeholder, 'name your avatar?') ]"
            reviews_avatar_tab  = "//h1[text()= 'Review Uploads' ]"
            continue_button     = "//*[@class='rc-dialog-body']//*[text()= 'Continue' ]"

            self.wait_and_presence_verify(create_photo_avator).click()
            self.wait_and_clickable_verify(upload_photo_avator).click()
            self.wait_and_presence_verify(upload_photo_input)
            self.driver.find_element(By.XPATH, upload_photo_input).send_keys(avatar_path)
            self.wait_and_clickable_verify(upload_photo_button, waitRange=(2,3)).click()
            self.wait_and_clickable_verify(reviews_avatar_tab, waitRange=(1,2)).click()
            self.wait_and_clickable_verify(continue_button, waitRange=(2,3)).click()
            name_obj = self.wait_and_clickable_verify(avart_photo_name)
            self.fill_inputs(avatar_name, name_obj)
            self.wait_and_clickable_verify(continue_button, waitRange=(2,3)).click()

        except Exception as e:
            raise Exception(f"Upload Avatar Failed! {e}")


    
    # Select Avator from Avator Page for Video Creation (App)
    def use_avatar_app(self, avatar_name, avatar_plattype='portait'):
        try:
            target_asset = None
            avatar_obj  = "//div[@class='css-13mekmm']"
            click_avator = "//div[@class='css-rtwtac']"
            avatar_ai_studio = "//*[@class='rc-dialog-body']//*[text()= 'Create with AI Studio' ]"
            avatar_Landscpe_type  = "//*[text()= 'Landscape' ]"
            avatar_portrait_type  = "//*[text()= 'Portrait' ]"
            
            total_avators = self.driver.find_elements(By.XPATH, avatar_obj)
            for index, i in enumerate(total_avators):
                try:
                    if i.find_element(By.XPATH, f".//*[text()='{avatar_name}']"): target_asset = total_avators[index]
                except: pass
        
            if target_asset: target_asset.click()
            else: return False
            
            self.wait_and_clickable_verify(click_avator, waitRange=(0.9,1.5)).click()
            element = self.wait_and_presence_verify(avatar_ai_studio, waitRange=(2,3))
            self.actions.move_to_element(element).perform()
            self.wait_and_presence_verify(avatar_portrait_type if 'port' in avatar_plattype else avatar_Landscpe_type, waitRange=(3,4)).click()
            return True
        except Exception as e:
            raise Exception(f"Use Avatar Failed! {e}")



    # Open Script Tab on webapp for writing script for video (App)
    def open_script_tab_app(self):
        try:
            script_tab  = "//*[text()= 'Script']"
            self.wait_and_presence_verify(script_tab, waitRange=(2,3)).click()
        except Exception as e:
            raise Exception(f"Open Script Tab Failed! {e}")
        

    # Add Script on webapp for video (App)
    def add_script_app(self, script):
        try:
            script_input = "//div[@role='textbox' and @contenteditable='true']"
            text_box = self.wait_and_presence_verify(script_input, timout=25)
            text_box.send_keys(Keys.CONTROL + "a")
            text_box.send_keys(Keys.BACKSPACE)
            text_box.send_keys(script)
        except Exception as e:
            raise Exception(f"Add Script Failed! {e}")


    # Delete Element on Webapp (App)
    def delete_obj_app(self, obj_xpath):
        try:
            delete_elem = "//*[text()= 'Delete']"
            element = self.wait_and_presence_verify(obj_xpath, timout=10)
            self.actions.click(element).context_click(element).perform()
            element = self.wait_and_presence_verify(delete_elem, timout=10).click()
        except Exception as e:
            raise Exception(f"Delete Failed! {e}")



    # Play Audio on Webapp (App)
    def play_avatar_vid_app(self):
        try:
            update_audio = "//button//iconpark-icon[@name='play-s']"
            audios = self.wait_and_clickable_verify(update_audio, timout=6, waitRange=(2,3))
            audios = self.driver.find_elements(By.XPATH, update_audio)
            try: self.actions.move_to_element(audios[0]).perform()
            except: pass
            try: self.actions.click(audios[0])
            except: audios[0].click()
        except Exception as e:
            raise Exception(f"Play Video Failed! {e}")


    # Select Audios Assests from list of Assets (App)
    def select_asset_app(self, name):
        try:
            upload_audio = "//button//iconpark-icon[@name='upload-asset']"
            uploaded_assets = "//div[@class='rc-tooltip-content']//div[@class='rc-tooltip-inner']/div/div[2]//div[contains(@class, 'canClick')]"
            self.driver.find_elements(By.XPATH, upload_audio)[1].click()
            self.random_time_sleep(1,2)
            assets = self.driver.find_elements(By.XPATH, uploaded_assets)
            for index, i in enumerate(assets): 
                if name in i.text: i.find_element(By.XPATH, './/div').click()
        except Exception as e:
            raise Exception(f"Asset Selection Failed! {e}")

