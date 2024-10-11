from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import random
import requests
import cloudscraper
import pandas as pd
import numpy as np
import re


# Initialize the data dictionary
data = {
    "url": [],
    "job_title": [],
    "job_type": [],
    "work_mode": [],
    "shift": [],
    "salary": [],
    "company_name": [],
    "company_rating": [],
    "location": [],
    "benefits": [],
    "description": []
}

# Initialize global counter
global_scraped_jobs_count = 0

def scrape_job_details(driver, job_url):
    global global_scraped_jobs_count
    time.sleep(random.uniform(1,5))
    driver.get(job_url)
    
    try:
        job_title = driver.find_element(By.XPATH, '//h1[contains(@class, "jobsearch-JobInfoHeader-title")]').text
    except:
        job_title = None
    
    # Company name extraction
    try:
        company_name = driver.find_element(By.XPATH, '//div[@data-company-name="true" or contains(@class, "css-hon9z8")]').text
    except:
        company_name = None

    # Location extraction
    try:
        location = driver.find_element(By.XPATH, '//div[@data-testid="inlineHeader-companyLocation"]//div').text
    except:
        location = None

    # Company rating extraction
    try:
        company_rating = driver.find_element(By.XPATH, '//div[contains(@class, "css-1unnuiz e37uo190")]').text
    except:
        company_rating = None

    # Salary extraction
    try:
        salary = driver.find_element(By.XPATH, '//span[contains(@class, "css-19j1a75") or contains(@class, "js-match-insights-provider-tvvxwd")]').text
    except:
        salary = None

    # Job type extraction
    try:
        job_type_element = driver.find_element(By.XPATH, '//div[@aria-label="Job type" and contains(@class, "js-match-insights-provider-16m282m e37uo190")]')
        if job_type_element:
            job_type = ' '.join(job_type_element.text.split('\n')[1:])  # Skip the first line if necessary
        else:
            job_type = None
    except Exception:
        job_type = None

    # Shift and schedule extraction
    try:
        shift_element = driver.find_element(By.XPATH, '//div[@aria-label="Shift and schedule" and contains(@class, "js-match-insights-provider-16m282m e37uo190")]')
        if shift_element:
            shift = ' '.join(shift_element.text.split('\n')[1:])  # Skip the first line
        else:
            shift = None
    except Exception:
        shift = None

    # Work mode extraction
    try:
        work_mode_element = driver.find_element(By.XPATH, '//div[contains(@class, "css-17cdm7w eu4oa1w0")]')
        if work_mode_element:
            work_mode = work_mode_element.text
        else:
            work_mode = None
    except Exception:
        work_mode = None

    # Benefits extraction
    try:
        benefits = driver.find_element(By.XPATH, '//div[@id="benefits"]').text
    except:
        benefits = None

    # Description extraction
    # Description extraction
    try:
        description_element = driver.find_element(By.XPATH, '//div[@id="jobDescriptionText" and contains(@class, "jobsearch-JobComponent-description")]')
        description = description_element.text if description_element else None
    except:
        description = None

    # Increment global counter
    global_scraped_jobs_count += 1

    # Append scraped data to the data dictionary
    data["url"].append(job_url)
    data["job_title"].append(job_title)
    data["job_type"].append(job_type)
    data["work_mode"].append(work_mode)
    data["shift"].append(shift)
    data["salary"].append(salary)
    data["company_name"].append(company_name)
    data["company_rating"].append(company_rating)
    data["location"].append(location)
    data["benefits"].append(benefits)
    data["description"].append(description)

    # Print how many jobs have been scraped globally
    print(f"Total jobs scraped: {global_scraped_jobs_count}\n")

driver = webdriver.Chrome()
base_urls = [
    "https://www.indeed.com/jobs?q=Accountant&start=",
    "https://www.indeed.com/jobs?q=Business+Analyst&start=",
    "https://www.indeed.com/jobs?q=Cyber+Security+Specialist&start=",
    "https://www.indeed.com/jobs?q=data+analyst&start=",
    "https://www.indeed.com/jobs?q=data+scientist&start=",
    "https://www.indeed.com/jobs?q=devops+engineer&start=",
    "https://www.indeed.com/jobs?q=financial+analyst&start=",
    "https://www.indeed.com/jobs?q=hr+assistant&start=",
    "https://www.indeed.com/jobs?q=IT+Project+Managment&start=",
    "https://www.indeed.com/jobs?q=machine+learning+engineer&start=",
    "https://www.indeed.com/jobs?q=qa+engineer&start=",
    "https://www.indeed.com/jobs?q=software+engineer&start=",
    "https://www.indeed.com/jobs?q=System+Administrator&start="
]

total_pages =  50
all_job_urls = []
for base_url in base_urls:
    for page in range(total_pages):
        print(f"Start Scraping for {base_url[30:-7]}")
        start_value = page * 10
        url = f"{base_url}{start_value}"
    
        driver.get(url)
        
        time.sleep(3)  # Consider using WebDriverWait for a more robust approach
        job_cards = driver.find_elements(By.CSS_SELECTOR, 'a[data-jk]')
    
        for card in job_cards:
            job_id = card.get_attribute('data-jk')
            job_url = f"https://www.indeed.com/viewjob?jk={job_id}"
            all_job_urls.append(job_url)
    
        print(f"Collected URLs from page {page + 1}")
    print(f"Stoped Scraping for {base_url[30:-7]}\n\n")


seen = set()
result = []
for item in all_job_urls:
    if item not in seen:
        seen.add(item)
        result.append(item)

# Iterate over each job URL and scrape details
for job_url in result:
    scrape_job_details(driver, job_url)
driver.quit()
print('The End')
df = pd.DataFrame(data=data)
df.to_csv("Non_Cleaned_Indeed_Jobs.csv", index = False)




def clean_rating(rating):
    try:
        return float(str(rating)[:3])
    except ValueError:
        return None  # Return None for non-numeric values
    
def clean_benefits(benefit):
    if str(benefit).startswith("Benefits"):
        return str(benefit)[45:-16].strip().replace("\n", ",")
    else:
        return benefit
        

def clean_salary(salary):
    if pd.isna(salary):
        return pd.Series([None, None, None])
    
    salary = salary.replace(",", "")
    salary_range = re.findall(r'\d+[,.]*\d*', salary)
    
    if len(salary_range) == 1:  # If there's only one number, put it in both start and end
        start_salary = salary_range[0]
        end_salary = salary_range[0]
    elif len(salary_range) == 2:
        start_salary, end_salary = salary_range
    else:
        start_salary, end_salary = None, None
    
    # Extract the type (year, month, week, day, hour)
    salary_type = None
    salary_lower = salary.lower()  # Lowercase salary for case-insensitive matching
    if 'year' in salary_lower:
        salary_type = 'year'
    elif 'month' in salary_lower:
        salary_type = 'month'
    elif 'week' in salary_lower:
        salary_type = 'week'
    elif 'day' in salary_lower:
        salary_type = 'day'
    elif 'hour' in salary_lower:
        salary_type = 'hour'
    
    return pd.Series([start_salary, end_salary, salary_type])

def clean_job_titles(title):
    if not isinstance(title, str):
        return 'Unknown', 'Unknown'
    
    lower_title = title.lower()
    
    # Define job titles and patterns
    job_patterns = {
        'IT Project Manager': r'\b(it project|project) (manager|management|coordinator)\b',
        'Project Manager': r'\bproject (manager|management|coordinator)\b',
        'Accountant': r'\baccountant\b',
        'Business Analyst': r'\bbusiness analyst\b',
        'Cyber Security Specialist': r'\b(cyber\s*security|cybersecurity|information\s*security|infosec)\b',
        'Data Analyst': r'\bdata analyst\b',
        'DevOps Engineer': r'\bdevops\b',
        'Financial Analyst': r'\bfinancial analyst\b',
        'HR Assistant': r'\b(hr\s*assistant|human\s*resources\s*assistant|hr\s*admin|hr\s*coordinator)\b',
        'Machine Learning Engineer': r'\b(machine learning|ml)\b',
        'QA Engineer': r'\b(q[a-z]?|quality|test)\s*engineer\b',
        'Software Engineer': r'\bsoftware engineer\b',
        'System Administrator': r'\b(system\s*administrator|sysadmin|system\s*admin|it administrator)\b',
        'Data Scientist': r'\b(data\s*science|data\s*scientist)\b'
    }
    
    # Default to Unknown for both title and level
    cleaned_title = 'Unknown'
    level = 'Unknown'
    
    # Check for job titles and assign levels
    for title_key, pattern in job_patterns.items():
        if re.search(pattern, lower_title):
            cleaned_title = title_key
            
            if re.search(r'\bsr|senior\b', lower_title):
                level = 'Senior'
            elif re.search(r'\b(middle|mid|mid-level)\b', lower_title):
                level = 'Middle'
            elif re.search(r'\b(junior|jr)\b', lower_title):
                level = 'Junior'
            break

    return cleaned_title, level



df.drop_duplicates(inplace = True)
df["company_rating"] = df["company_rating"].apply(clean_rating).astype(float)
df["benefits"] = df["benefits"].apply(clean_benefits)
df['title'], df['level'] = zip(*df['job_title'].apply(clean_job_titles))
df[['start_salary', 'end_salary', 'salary_type']] = df['salary'].apply(clean_salary)
df.drop(df[df['title'] == 'Unknown'].index, inplace=True)

df.to_csv('Indeed_Jobs.csv',index=False)

# Updated salary parsing function to handle "per day"
def parse_salary(salary_str):
    if pd.isna(salary_str):
        return None
    
    # Extract numbers from the salary string
    salary_range = re.findall(r'[\d,]+', salary_str)
    
    # Convert the salary to a float and take the average if it's a range
    if len(salary_range) == 2:
        lower = float(salary_range[0].replace(',', ''))
        upper = float(salary_range[1].replace(',', ''))
        avg_salary = (lower + upper) / 2
    elif len(salary_range) == 1:
        avg_salary = float(salary_range[0].replace(',', ''))
    else:
        return None
    
    # Check the salary period (hourly, daily, weekly, monthly, yearly)
    salary_str_lower = salary_str.lower()
    
    if 'hour' in salary_str_lower:
        avg_salary *= 2080  # Convert hourly salary to yearly (2080 hours per year)
    elif 'day' in salary_str_lower:
        avg_salary *= 260   # Convert daily salary to yearly (260 working days per year)
    elif 'week' in salary_str_lower:
        avg_salary *= 52    # Convert weekly salary to yearly (52 weeks per year)
    elif 'month' in salary_str_lower:
        avg_salary *= 12    # Convert monthly salary to yearly (12 months per year)
    # If it's already per year, we don't need to convert
    
    return avg_salary

# Apply the parsing function to the salary column
df['parsed_salary'] = df['salary'].apply(parse_salary)

# Fill missing salaries based on the job title's median salary
df['parsed_salary'] = df.groupby(['job_title'])['parsed_salary'].transform(lambda x: x.fillna(x.median()))

# If there are still NaN values, fill remaining missing values with overall median salary
df['parsed_salary'].fillna(df['parsed_salary'].median(), inplace=True)

df['level'].replace('Unknown', np.nan, inplace=True)

df.drop(columns=['url', 'level', 'job_title', 'work_mode', 'shift', 'description', 'start_salary', 'end_salary', 'salary_type', 'benefits', 'salary'], inplace=True)

def fill_missing_with_ratio(df, column):
    # Drop NaN values and calculate the distribution of existing values
    value_counts = df[column].value_counts(normalize=True)
    
    # Get the missing indices
    missing_indices = df[df[column].isna()].index
    
    # Randomly choose values for the missing entries based on the existing distribution
    imputed_values = np.random.choice(value_counts.index, size=len(missing_indices), p=value_counts.values)
    
    # Fill the missing values
    df.loc[missing_indices, column] = imputed_values
    
    return df

# Apply the function to fill missing company_rating values
df = fill_missing_with_ratio(df, 'company_rating')

df['job_type'] = df['job_type'].replace({
    'Permanent Full-time': 'Full-time',
    'Full-time PRN': 'Full-time',
    'Full-time Permanent': 'Full-time',
    'Temporary Part-time': 'Part-time',
    'Part-time Contract': 'Part-time',
    'Permanent Part-time': 'Part-time'})

df = df[(df['job_type'] == 'Full-time') | (df['job_type'] == 'Part-time') | df['job_type'].isnull()]

def fill_missing_with_ratio(df, column):
    # Drop NaN values and calculate the distribution of existing values
    value_counts = df[column].value_counts(normalize=True)
    
    # Get the missing indices
    missing_indices = df[df[column].isna()].index
    
    # Randomly choose values for the missing entries based on the existing distribution
    imputed_values = np.random.choice(value_counts.index, size=len(missing_indices), p=value_counts.values)
    
    # Fill the missing values
    df.loc[missing_indices, column] = imputed_values
    
    return df

# Apply the function to fill missing company_rating values
df = fill_missing_with_ratio(df, 'job_type')

# Function to extract city and state
def extract_city_state(location):
    if location == "Remote":
        return location # Exclude Remote cases
    
    parts = location.split(',')
    # Trim whitespace from parts
    parts = [part.strip() for part in parts]
    
    if len(parts) == 1:
        city = parts[0]
    elif len(parts) == 2:
        city = parts[0]
    elif len(parts) == 3:
        city = parts[1]
    else:
        return None
    
    return city

# Apply the function to the DataFrame
df[['location']] = df['location'].apply(lambda loc: pd.Series(extract_city_state(loc)))

df = df.dropna()

df.to_csv('visualization_data.csv', index = False)