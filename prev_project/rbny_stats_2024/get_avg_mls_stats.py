from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd
import os

# Set up the driver
driver = webdriver.Chrome()
driver.get("https://www.newyorkredbulls.com/stats/#season=2024&competition=mls-regular-season&club=399&statType=general&position=all")  # Replace with the actual URL of the MLS stats page

# Wait for the page to load completely
driver.implicitly_wait(10)

try:
    # Wait for the table body to be present
    table_body = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "short-name"))
    )

    # Extract data rows from the table
    data_rows = []
    while True:
        try:
            # Re-fetch the table body and rows to avoid stale references
            table_body = driver.find_element(By.CSS_SELECTOR, "table.mls-o-table tbody.mls-o-table__body")
            rows = table_body.find_elements(By.CSS_SELECTOR, "tr.mls-o-table__row")

            for row in rows:
                row_data = []
                cells = row.find_elements(By.CSS_SELECTOR, "td.mls-o-table__cell")
                for cell in cells:
                    # Skip cell if it has the class "club"
                    if "club" in cell.get_attribute("class"):
                        continue

                    # Get the text content and strip whitespace
                    cell_text = cell.get_attribute('innerHTML')

                    # If cell_text contains HTML for player name, extract just the name
                    if '<div class="short-name">' in cell_text:
                        start_index = cell_text.index('short-name">') + len('short-name">')
                        end_index = cell_text.index('</div>', start_index)
                        player_name = cell_text[start_index:end_index]
                        row_data.append(player_name)  # Append the player name
                    else:
                        # Append the cell text as is (for other columns)
                        row_data.append(cell_text.strip())

                # Append the row data to the data_rows list
                data_rows.append(row_data)
            break  # Exit the while loop if successful

        except StaleElementReferenceException:
            # Retry if a stale reference is encountered
            continue

    # Print the final data rows extracted from the table
    print("Data rows:", data_rows)

    # Define the column headers
    headers = [
        "Player",
        "Games Played",
        "Games Started",
        "Mins",
        "Total Sub On",
        "Goals",
        "Accurate Pass %",
        "Assists",
        "Total Scoring Attempts",
        "On target Scoring Attempts",
        "Total Attacking Assists",
        "Expected Goals",
        "Fouls",
        "Fouls Suffered",
        "Offside",
        "Yellow Cards",
        "Red Cards"
    ]

    # Create a DataFrame from the data rows
    df = pd.DataFrame(data_rows, columns=headers)

    
    
    # Ensure the working directory is correct (the directory of your script)
    script_dir = os.path.dirname(os.path.realpath(__file__))  # Get the current script directory
    files_dir = os.path.join(script_dir, 'files')  # Define the 'files' directory

    # Ensure the 'files' folder exists
    if not os.path.exists(files_dir):
        os.makedirs(files_dir)

    # Define the output file path knowing that the folder 'files' already exists
    output_file = os.path.join(files_dir, "avg_mls_stats.xlsx")



    df.to_excel(output_file, index=False)
    print(f"Data successfully written to {output_file}")

except Exception as e:
    print("An error occurred:", e)

finally:
    # Close the WebDriver
    driver.quit()
