from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time, os
import pandas as pd


# Initialize Selenium WebDriver
driver = webdriver.Chrome()  # Make sure ChromeDriver is in your PATH

# Load the team stats page URL
team_url = 'https://www.espn.com/soccer/team/stats/_/id/190/new-york-red-bulls'
driver.get(team_url)

# Wait for the content to load
time.sleep(3)

# Parse the page source with BeautifulSoup after it loads
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Close the browser
driver.quit()

# Retrieve the table with class 'Table'
table = soup.find('table', class_='Table')

# Check if the table was found
if table:
    # Find all rows in the table (Table__TR class for player rows)
    player_links = []
    rows = table.find_all('tr', class_='Table__TR')
    for row in rows:
        # Find the first anchor link with class 'AnchorLink' in each row
        anchor = row.find('a', class_='AnchorLink', href=True)
        if anchor:
            # Extract the player URL and append '/matches' after '/player'
            player_url = anchor['href'].replace('/player', '/player/matches')
            player_links.append(player_url)
    
    print(f"Found {len(player_links)} player links.")
else:
    print("Table with specified class not found.")

# Create an empty list to store all the DataFrames for each player
all_player_data = []

# Define a variable to hold the expected headers
expected_headers = []

# Iterate through each player link to retrieve match data
for idx, player_link in enumerate(player_links):
    # Re-initialize the browser for each player
    driver = webdriver.Chrome()
    driver.get(player_link)
    
    # Wait for the content to load
    time.sleep(3)
    
    # Parse the page source with BeautifulSoup after it loads
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        player_name_elements = soup.find_all('span', class_='min-w-0')
        if len(player_name_elements) >= 2:
            first_name = player_name_elements[0].text.strip()  
            last_name = player_name_elements[1].text.strip()
    except Exception as e:
        print(f"Could not find player name: {e}")
        first_name = ""
        last_name = ""

    # Close the browser
    driver.quit()

    # Locate the first table with the specific class structure
    table = soup.find('table', class_='Table Table--align-right')

    # Check if the table was found
    if table:
        # Extract headers for the first player and set as expected headers
        headers = [th.text.strip() for th in table.find('thead').find_all('th')] if table.find('thead') else []
        
        if idx == 0:
            expected_headers = headers  # Set expected headers for the first player

        # Now, create a mapping for the current player's header order
        header_mapping = {}
        for i, header in enumerate(headers):
            if header in expected_headers:
                expected_idx = expected_headers.index(header)
                header_mapping[i] = expected_idx
            else:
                # If the header is not in the expected headers, add it to the expected_headers list
                expected_headers.append(header)
                header_mapping[i] = len(expected_headers) - 1  # New column gets the last index

        # Initialize an empty list to hold the corrected rows of data
        data = []
        
        # Extract rows of data
        tbody = table.find('tbody')
        if tbody:
            for row in tbody.find_all('tr', class_='Table__TR'):
                row_data = [td.text.strip() for td in row.find_all('td')]
                
                # Initialize an empty row with None values for all columns
                reordered_data = [None] * len(expected_headers)
                
                # Map the row data to the expected header names based on header mapping
                for col_idx, mapped_idx in header_mapping.items():
                    reordered_data[mapped_idx] = row_data[col_idx]
                
                # Add the player name as the first entry in the row
                reordered_data.insert(0, first_name)
                reordered_data.insert(0, last_name)
                
                # Append the reordered row to the data list
                data.append(reordered_data)

        # Create a DataFrame from the reordered data
        df = pd.DataFrame(data, columns=['Last Name', 'First Name'] + expected_headers)
        
        # Append this player's data to the all_player_data list
        all_player_data.append(df)
        
        print(f"Data for {last_name} has been collected")
    else:
        print(f"Table with specified class not found for player: {last_name}")


# Once all the player data is collected, combine all DataFrames into one
final_df = pd.concat(all_player_data, ignore_index=True)

# Define the dictionary for renaming columns
rename_dict = {
    'G': 'Total Goals',
    'A': 'Assists',
    'SH': 'Shots on Target',
    'ST': 'Shots Taken',
    'FC': 'Fouls Committed',
    'FA': 'Fouls Against',
    'OF': 'Offsides',
    'YC': 'Yellow Cards',
    'RC': 'Red Cards',
    'CS': 'Clean Sheets',
    'SV': 'Saves',
    'GA': 'Goals Against'
}

# Rename the columns in final_df
final_df = final_df.rename(columns=rename_dict)


# Ensure the working directory is correct (the directory of your script)
script_dir = os.path.dirname(os.path.realpath(__file__))  # Get the current script directory
files_dir = os.path.join(script_dir, 'files')  # Define the 'files' directory

# Ensure the 'files' folder exists
if not os.path.exists(files_dir):
    os.makedirs(files_dir)

# Define the output file path (assuming the folder 'files' already exists)
output_file = os.path.join(files_dir, "season_stats_per_player.xlsx")

# Save the final combined DataFrame to Excel
final_df.to_excel(output_file, index=False)

print("All data has been successfully saved to 'season_stats_per_player.xlsx'")
