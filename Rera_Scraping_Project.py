# Required pip installs (install in terminal or PyCharm):
# pip install selenium
# pip install webdriver-manager

from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options
options = Options()
options.add_argument("--start-maximized")

# Auto-download ChromeDriver and use it
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 20)

# Step 1: Open the project list page
driver.get("https://rera.odisha.gov.in/projects/project-list")
time.sleep(4)

# Handle pop-up if it appears
try:
    ok_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='OK']")))
    ok_button.click()
    time.sleep(2)
except:
    pass  # No pop-up appeared

# Wait until projects load
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "project-card")))
time.sleep(2)

# Step 2: Loop over first 6 project details
projects_data = []

for i in range(6):
    # Re-find buttons on each iteration due to page refresh/navigation
    view_buttons = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")

    # Scroll to the button and click
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", view_buttons[i])
    time.sleep(1)
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'View Details')]")))
        view_buttons[i].click()
    except:
        # fallback click with JS
        driver.execute_script("arguments[0].click();", view_buttons[i])

    time.sleep(4)  # wait for details page to load

    # Extract overview details
    try:
        rera_no_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//label[text()='RERA Regd. No.']/following::strong")))
        rera_no = rera_no_elem.text.strip()
    except:
        rera_no = ""

    try:
        project_name_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//label[text()='Project Name']/following::strong")))
        project_name = project_name_elem.text.strip()
    except:
        project_name = ""

    # Click promoter details tab
    try:
        promoter_tab = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(text(), 'Promoter Details')]")))
        promoter_tab.click()
        time.sleep(5)  # wait for tab content to load
    except:
        pass

    # Extract promoter name with fallback
    try:
        promoter_name_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//label[text()='Company Name']/following-sibling::strong")))
        promoter_name = promoter_name_elem.text.strip()
    except:
        try:
            promoter_name_elem = driver.find_element(
                By.XPATH, "//label[text()='Propietory Name']/following-sibling::strong")
            promoter_name = promoter_name_elem.text.strip()
        except:
            promoter_name = "--"

    # Extract promoter address with fallback
    try:
        promoter_address_elem = driver.find_element(
            By.XPATH, "//label[text()='Registered Office Address']/following-sibling::strong")
        promoter_address = promoter_address_elem.text.strip()
    except:
        try:
            promoter_address_elem = driver.find_element(
                By.XPATH, "//label[text()='Current Residence Address']/following-sibling::strong")
            promoter_address = promoter_address_elem.text.strip()
        except:
            promoter_address = "--"

    try:
        gst_no_elem = driver.find_element(
            By.XPATH, "//label[text()='GST No.']/following::strong")
        gst_no = gst_no_elem.text.strip()
    except:
        gst_no = "--"

    # Save data to list
    project = {
        "RERA Regd. No": rera_no,
        "Project Name": project_name,
        "Promoter Name": promoter_name,
        "Promoter Address": promoter_address,
        "GST No": gst_no
    }
    projects_data.append(project)

    # Go back to project list
    driver.back()
    time.sleep(4)

    # Handle pop-up again if any
    try:
        ok_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='OK']")))
        ok_button.click()
        time.sleep(2)
    except:
        pass

    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "project-card")))
    time.sleep(2)

# Close driver
driver.quit()

# Print results
for idx, project in enumerate(projects_data):
    print(f"\nProject {idx + 1}:")
    for key, value in project.items():
        print(f"{key}: {value}")
