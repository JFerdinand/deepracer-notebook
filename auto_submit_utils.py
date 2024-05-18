import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.service import Service


error = 'ERROR: '
GLOBAL_WAIT_TIME: int = 15
SUBMISSION_WAIT_TIME: int = 15

def start_selenium(creds, url, model_name, iam_role=True):
    good = True
    retry_count = 0
    print("==========Start Selenium webdriver==========")
    # Start Selenium webdriver
    browserProfile = webdriver.ChromeOptions()
    browserProfile.add_argument('--headless')
    browserProfile.add_argument('--no-sandbox')
    browserProfile.add_argument('--disable-dev-shm-usage')
    browserProfile.add_argument('--disable-gpu')
    browserProfile.add_argument('--remote-debugging-port=9222')
    browserProfile.add_argument('--single-process')
    browserProfile.add_experimental_option(
        'prefs', {'intl.accept_languages': 'en,en_US'})
    ser = Service()
    ser.path = r'D:\document\DeepRacer\chromedriver.exe'
    driver = webdriver.Chrome(options=browserProfile, service=ser)
    wait = WebDriverWait(driver, GLOBAL_WAIT_TIME)
    pending = WebDriverWait(driver, SUBMISSION_WAIT_TIME)
    driver.maximize_window()

    def login(creds, iam_role=True):
        print(time.ctime() + ' | Logging in..')

        if not iam_role:
            driver.get('https://console.aws.amazon.com')
            time.sleep(2)
            elem_username = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='email']")))
            elem_username.clear()
            elem_username.send_keys(creds[0])
            elem_submit = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@id='next_button']")))
            elem_submit.click()

            check_captcha()

            elem_password = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='password']")))
            elem_password.clear()
            elem_password.send_keys(creds[1])

            elem_submit = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@id='signin_button']")))
            elem_submit.click()
            print("==========login success==========")

        else:
            driver.get('https://%s.signin.aws.amazon.com/console' %creds[0])
            time.sleep(2)
            elem_username = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='username']")))
            elem_username.clear()
            elem_username.send_keys(creds[1])

            elem_password = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='password']")))
            elem_password.clear()
            elem_password.send_keys(creds[2])

            elem_submit = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='input_signin_button']/a")))
            elem_submit.click()
            print("==========login success==========")

    def check_captcha():
        # Checks if there is a captcha so a human can enter the letters
        # TODO: Create an AI that can read the captcha and enter the letters automatically lol
        print('Looking for CAPTHCA prompt...')
        try:
            time.sleep(2)
            captcha_image = driver.find_element(By.XPATH, "//img[@id='captcha_image']")
        except NoSuchElementException:
            print("No CAPTCHA found.")
        else:
            input('CAPTCHA found. Please complete the CAPTCHA. Then press ENTER to continue...')


    # Log in
    try:
        print("==========Start login==========")
        login(creds, iam_role=iam_role)
    except:
        print(error + 'Login Failed. Check credentials.')
        good = False

    # Go to race url
    if good:
        try:
            print("===========Go to sub account url==========")
            time.sleep(10)
            driver.get("https://us-east-1.console.aws.amazon.com/deepracer/home?region=us-east-1#welcome")
            print(f"======sub account url======={driver.title}")
            time.sleep(15)
            elem_username = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='email']")))
            print(f"======email======={elem_username}")
            elem_username.clear()
            elem_username.send_keys('18068840660@163.com')
            elem_password = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='password']")))
            elem_password.clear()
            elem_password.send_keys('QAZwsx123!@#')
            elem_submit = driver.find_elements(By.XPATH, "//button[@type='submit']")[9]
            print(elem_submit)
            elem_submit.click()
            print("===========Go to race url==========")
            time.sleep(10)
            driver.get(url)
            print(f"===========Get race url title=========={driver}")
            time.sleep(15)
        except Exception:
            print(Exception)
            print(error + 'Failed finding "Race again" button. Check the url.')
            good = False

    while good:
        while True:

            # Choose model and submit it
            try:
                print("===========Choose model step1==========")
                dropdown = wait.until(EC.presence_of_element_located((By.XPATH,"//span[contains(text(), 'Choose a model')]")))
                print(f"===========dropdown=========={dropdown}")
                dropdown.click()
                print("===========Choose model step2==========")
                choose_model = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '%s')]/ancestor::li" %model_name)))
                choose_model.click()
                print("===========Choose model Success==========")
            except Exception:
                print(error + 'Failed to select model with name "%s"' %model_name)
                break

            # Click the submit buttom
            try:
                print("===========Click the submit button===========")

                enter_race = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@data-analytics='submit_to_leaderboard_accept']")))
                enter_race.click()

                # Check to see if model submitted successfully
                time.sleep(2)
                check_eval = wait.until(EC.presence_of_element_located((By.XPATH,"//span[contains(text(), 'Under evaluation')]")))
                check_eval = check_eval.text
                if check_eval != 'Under evaluation':
                    print(error + 'Model Submission Failed')
                    break
            except Exception:
                print(error + 'Model Submission Failed')
                break
            
        # Retry if failed
        retry_count += 1

        # Break if failed too many attempts
        if retry_count == 20:
            print(time.ctime() + ' | Failed %s time(s). Stopping.' %retry_count)
            driver.quit()
            break

        try:
            driver.get(url)
        except:
            driver.quit()
            break

        # Log back in if logged out
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='input_signin_button']/a")))
            print(time.ctime() + ' | Logged out. Attempting to login again..')

            try:
                login(creds)
            except Exception:
                print(time.ctime() + ' | ERROR: Login Failed')
                driver.quit()
                break

        except Exception:
            print(time.ctime() + ' | Failed %s time(s). Retrying..' %retry_count)

