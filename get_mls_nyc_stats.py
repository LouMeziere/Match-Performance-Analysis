from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd

# Set up the driver
driver = webdriver.Chrome()
driver.get("https://www.newyorkcityfc.com/stats/#season=2024&competition=mls-regular-season&club=9668&statType=general&position=all")  # Replace with the actual URL of the MLS stats page

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

    # Save the DataFrame to an Excel file
    output_file = "mls_nyc_stats.xlsx"

    df.to_excel(output_file, index=False)
    print(f"Data successfully written to {output_file}")

except Exception as e:
    print("An error occurred:", e)

finally:
    # Close the WebDriver
    driver.quit()


nyc_player_roles = {
    "A. Martínez": "Attacker", "Santiago Rodríguez": "Midfielder", "H. Wolf": "Attacker",
    "M. Bakrar": "Attacker", "A. Ojeda": "Attacker", "A. Perea": "Midfielder",
    "J. Fernández": "Attacker", "K. Parks": "Midfielder", "T. Gray": "Defender",
    "M. Ilenic": "Defender", "M. Jones": "Attacker", "Talles Magno": "Attacker",
    "Thiago": "Defender", "M. Moralez": "Midfielder", "K. O'Toole": "Attacker",
    "J. Sands": "Midfielder", "J. Arroyave": "Midfielder", "A. Baiera": "Defender",
    "M. Carrizo": "Midfielder", "P. Elias": "Midfielder", "Rio Hope-Gund": "Defender",
    "A. Jasson": "Midfielder", "N. Acevedo": "Midfielder", "Thiago Andrade": "Attacker",
    "L. Barraza": "Goalkeeper", "N. Benalcazar": "Defender", "J. Denis": "Attacker",
    "M. Freese": "Goalkeeper", "J. Haak": "Midfielder", "C. McFarlane": "Defender",
    "J. Mijatović": "Attacker", "C. Mizell": "Goalkeeper", "A. Morales": "Midfielder",
    "S. Owusu": "Defender", "M. Pellegrini": "Midfielder", "A. Rando": "Goalkeeper",
    "B. Risa": "Defender", "T. Romero": "Goalkeeper", "G. Segal": "Attacker",
    "J. Shore": "Midfielder", "S. Tanasijević": "Defender", "S. Turnbull": "Defender",
    "Z. Yañez": "Attacker"
}

nyc_season_stats = pd.read_excel('mls_nyc_stats.xlsx')
# Add role column based on the player names and player_roles
nyc_season_stats['Role'] = nyc_season_stats['Player'].map(nyc_player_roles)
