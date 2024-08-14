import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, timedelta

# Kamus untuk menerjemahkan nama bulan
bulan_mapping = {
    "Januari": "January",
    "Februari": "February",
    "Maret": "March",
    "April": "April",
    "Mei": "May",
    "Juni": "June",
    "Juli": "July",
    "Agustus": "August",
    "September": "September",
    "Oktober": "October",
    "November": "November",
    "Desember": "December"
}

# Global cache untuk elemen
cache = {
    'dropdown_komoditas': None,
    'jenis_pasar_dropdown': None,
    'provinsi_dropdown': None,
    'kabupaten_dropdown': None,
    'tanggal_button': None
}

# Variabel global untuk menyimpan status klik
is_initialized = False

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service('/usr/local/bin/chromedriver')  # Ubah path jika diperlukan
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def initialize_elements(driver):
    try:
        print("Initializing elements...")
        if not cache['dropdown_komoditas']:
            cache['dropdown_komoditas'] = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@id="ddbCategory"]//div[@class="dx-texteditor-input-container"]/input[@type="text"]'))
            )
        cache['dropdown_komoditas'].click()
        time.sleep(1)

        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//li[@role='treeitem' and contains(@aria-label, 'Beras') and @aria-level='1']"))
        )

        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        time.sleep(1)

        medium_beras_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//li[@role='treeitem' and contains(@aria-label, 'Beras Kualitas Bawah I') and @aria-level='2']"))
        )

        medium_beras_element.click()
        time.sleep(1)

        if not cache['jenis_pasar_dropdown']:
            cache['jenis_pasar_dropdown'] = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '(//input[@aria-autocomplete="list" and @aria-haspopup="listbox"])[1]'))
            )
        cache['jenis_pasar_dropdown'].click()
        time.sleep(1)

        pasar_modern_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "dx-item-content") and contains(text(), "Pasar Modern")]'))
        )
        pasar_modern_option.click()
        time.sleep(1)

        if not cache['provinsi_dropdown']:
            cache['provinsi_dropdown'] = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '(//input[@aria-autocomplete="list" and @aria-haspopup="listbox"])[2]'))
            )
        cache['provinsi_dropdown'].click()
        time.sleep(1)

        driver.execute_script("""
            var items = document.querySelectorAll('div.dx-scrollable-content .dx-item-content.dx-list-item-content');
            for (var i = 0; i < items.length; i++) {
                if (items[i].textContent.includes('Jawa Timur')) {
                    items[i].click();
                    break;
                }
            }
        """)

        if not cache['kabupaten_dropdown']:
            cache['kabupaten_dropdown'] = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '(//input[@aria-autocomplete="list" and @aria-haspopup="listbox"])[3]'))
            )
        cache['kabupaten_dropdown'].click()
        time.sleep(1)

        if not cache['tanggal_button']:
            cache['tanggal_button'] = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='dboDate']//div[@class='dx-texteditor-buttons-container']//div[@role='button']"))
            )
        print("Elements initialized.")
    except Exception as e:
        print(f"Error initializing elements: {e}")

def navigate_to_month(driver, target_date):
    target_date = datetime.strptime(target_date, '%Y-%m-%d')
    target_month = target_date.month
    target_year = target_date.year

    while True:
        try:
            current_month_year_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'dx-calendar-caption-button') and contains(@class, 'dx-button-has-text')]//span[@class='dx-button-text']"))
            )
            current_month_year = current_month_year_element.text.strip()

            if not current_month_year:
                print("Element text is empty, retrying...")
                continue

            try:
                current_month_str, current_year = current_month_year.split()
                current_year = int(current_year)
                current_month_str = current_month_str.capitalize()
                
                current_month_eng = bulan_mapping.get(current_month_str, current_month_str)
                current_month = datetime.strptime(current_month_eng, '%B').month
            except ValueError as ve:
                print(f"Error parsing month/year: {ve}")
                break

            if current_month == target_month and current_year == target_year:
                break

            if (current_year < target_year) or (current_year == target_year and current_month < target_month):
                chevron_next = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@role='button' and @aria-label='chevronright']"))
                )
                chevron_next.click()
                print("Navigating to next month.")
            else:
                chevron_prev = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@role='button' and @aria-label='chevronleft']"))
                )
                chevron_prev.click()
                print("Navigating to previous month.")
            
            time.sleep(1)
        except Exception as e:
            print(f"Error in navigate_to_month: {e}")
            break

def select_kabupaten(driver, kabupaten_name):
    try:
        if not cache['kabupaten_dropdown']:
            cache['kabupaten_dropdown'] = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '(//input[@aria-autocomplete="list" and @aria-haspopup="listbox"])[3]'))
            )
        
        cache['kabupaten_dropdown'].click()
        time.sleep(1)  

        script = f"""
            var items = document.querySelectorAll('div.dx-scrollable-content .dx-item-content.dx-list-item-content');
            for (var i = 0; i < items.length; i++) {{
                if (items[i].textContent.trim().includes('{kabupaten_name}')) {{
                    items[i].scrollIntoView(); 
                    items[i].click();
                    return 'Clicked';
                }}
            }}
            return 'Not Found';
        """
        result = driver.execute_script(script)
        
        if result == 'Clicked':
            print(f"Clicked on kabupaten: {kabupaten_name}")
        else:
            print(f"Kabupaten {kabupaten_name} not found in the dropdown.")

        time.sleep(1)  

    except Exception as e:
        print(f"Error in select_kabupaten: {e}")

def fetch_price(driver, date, kabupaten_name):
    global cache, is_initialized

    driver.get('https://www.bi.go.id/hargapangan#')

    try:
        if not is_initialized:
            initialize_elements(driver)
            is_initialized = True

        select_kabupaten(driver, kabupaten_name)
        
        print("Clicking tanggal button...")
        cache['tanggal_button'].click()
        time.sleep(1)

        navigate_to_month(driver, date)
        tanggal_yang_diinginkan = datetime.strptime(date, '%Y-%m-%d')
        tanggal_data_value = tanggal_yang_diinginkan.strftime('%Y/%m/%d')

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//td[@data-value='{tanggal_data_value}']"))
        )

        script = f"""
            var cell = document.querySelector('td[data-value="{tanggal_data_value}"]');
            if (cell) {{
                cell.click();
                return 'Clicked';
            }} else {{
                return 'Not Found';
            }}
        """
        result = driver.execute_script(script)
        print(f"Script result: {result}")

        if result != 'Clicked':
            raise Exception("Tanggal tidak ditemukan atau tidak dapat diklik.")

        print("Clicking 'Tampilkan' button...")
        tombol_tampilkan = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@id="devextreme11"]'))
        )
        tombol_tampilkan.click()
        time.sleep(1)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//td[@aria-describedby="dx-col-2"][@style="text-align: right;"]'))
        )

        harga_element = driver.find_element(By.XPATH, '//td[@aria-describedby="dx-col-2"][@style="text-align: right;"]')
        return harga_element.text.strip()

    except Exception as e:
        print(f"Error in fetch_price: {e}")
        return None

def crawl_data_for_all_kabupaten(start_date, end_date):
    driver = get_driver()
    kabupaten_list = [
        "Surabaya", "Malang", "Kediri", "Jember", "Banyuwangi", "Madiun", 
        "Probolinggo", "Sumenep", "Bangkalan", "Jombang", "Pasuruan", 
        "Situbondo", "Bojonegoro", "Ngawi", "Nganjuk", "Bondowoso", 
        "Sampang", "Gresik", "Tuban", "Magetan", "Trenggalek", 
        "Mojokerto", "Lamongan", "Ponorogo", "Blitar", "Lumajang", 
        "Tulungagung", "Pamekasan", "Sidoarjo", "Batu", "Pacitan"
    ]
    
    for kabupaten in kabupaten_list:
        print(f"Processing kabupaten: {kabupaten}")

        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

        file_name = f"data_{kabupaten}_beras_quality_bawah_1.csv"
        with open(file_name, 'w') as file:
            file.write("Date,Kabupaten,Price\n")
            
            while current_date <= end_date_obj:
                date_str = current_date.strftime('%Y-%m-%d')
                print(f"Fetching data for date: {date_str}")

                try:
                    price = fetch_price(driver, date_str, kabupaten)
                    if price:
                        print(f"Price for {kabupaten} on {date_str}: {price}")
                        file.write(f"{date_str},{kabupaten},{price}\n")
                    else:
                        print(f"No price data found for {kabupaten} on {date_str}")

                except Exception as e:
                    print(f"Error fetching data for {kabupaten} on {date_str}: {e}")

                current_date += timedelta(days=1)

        print(f"Completed processing kabupaten: {kabupaten}")

    driver.quit()

# Menjalankan proses crawling dengan rentang tanggal yang diinginkan
crawl_data_for_all_kabupaten('2019-08-01', '2024-08-01')
