from selenium  import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

options = Options()
options.add_argument("--start-maximized")   
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options) 

url = "https://www.flipkart.com/search?q=mobile"
driver.get(url)
time.sleep(3)

product_data = []

for page in range(1, 11): 
    print(f"\n📄 Scraping page {page} ...")
    products = driver.find_elements(By.XPATH, '//div[contains(@class,"_75nlfW")]')
    count = 1
    for product in products:
        try:
            name = product.find_element(By.XPATH, './/div[contains(@class,"KzDlHZ")]').text
            price = product.find_element(By.XPATH, './/div[contains(@class,"Nx9bqj _4b5DiR")]').text
            if price.startswith('₹'):
                price = price[1:].replace(',','')
            try:
                rating = product.find_element(By.XPATH, './/span[contains(@class,"Wphh3N")]').text
                # 2,159 Ratings & 122 Reviews
                parts = rating.replace('&', '').split()
                total_ratings = parts[0].replace(',', '') if len(parts) > 0 else '0'
                total_reviews = parts[2].replace(',', '') if len(parts) > 2 else '0'
            except:
                total_ratings = '0'
                total_reviews = '0'
            specifications = product.find_elements(By.XPATH, './/ul[contains(@class,"G4BRas")]/li')
            specs = [spec.text for spec in specifications]  
            specs = ', '.join(specs)
            print(f"Name: {name}, Price: {price}, Rating: {total_ratings}", f"Specifications: {specs}")
            product_data.append([name,price,total_ratings, total_reviews,specs])
        except Exception as e:
            print("skipping item due to error:", e)
            continue  
        count += 1
        if count ==20:
            break
        print(f"Processed {count} products on page {page}")
    next_button = driver.find_element(By.XPATH, "//a[@class='_9QVEpD']")
    next_button.click()
    time.sleep(3)
driver.quit()  
print("Sample product_data row:", product_data[0] if product_data else "No data collected")

df = pd.DataFrame(product_data, columns=["Name", "Price", "Total_Ratings","Total_Reviews" ,"Specifications"])
# convert to numeric
df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
df["Total_Ratings"] = pd.to_numeric(df["Total_Ratings"], errors="coerce")
df["Total_Reviews"] = pd.to_numeric(df["Total_Reviews"], errors="coerce")
# extract brand name
df["Brand"] = df["Name"].str.split().str[0]


# create price ranges for dashboard charts
bins = [0, 10000, 20000, 30000, 40000, 60000, 100000]
labels = ["0-10K", "10K-20K", "20K-30K", "30K-40K", "40K-60K", "60K+"]
df["Price_Range"] = pd.cut(df["Price"], bins=bins, labels=labels, include_lowest=True)

# reorder columns
df = df[["Brand", "Name", "Price", "Price_Range", "Total_Ratings", "Total_Reviews", "Specifications"]]

# save dashboard-ready Excel
output_file = "flipkart_mobile_dashboard.xlsx"
df.to_excel(output_file, index=False)
print(f"\n✅ Dashboard-ready data saved to {output_file}!")
print("\nSample rows:\n", df.head())

