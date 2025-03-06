import json
import random
import asyncio
import aiohttp
import argparse

import pandas as pd

from logger import LogCenter 
from user_agent import USER_AGENTS
from referer import REFERERS

pd.set_option('display.max_columns', 12)
pd.set_option('display.max_colwidth', 20)
pd.set_option('display.max_rows', 30)
pd.set_option('display.width', 0)


logger = LogCenter(__name__)

BASE_URL: str = "https://www.whitepages.com"

HEADERS: dict[str, str] = {
    'Content-Type': 'application/ld+json',
    'User-Agent': random.choice(USER_AGENTS),
    'Referer': random.choice(REFERERS),
}

TARGET_INFORMATION = {
    'url': [],
    'aliases': [],
    'address': [],
    'telephone': [],
    'relatives': [],
    'occupation': [],
    'description': [],
    'works_for': [],
    'given_name': [],
    'family_name': [],
    'contained_in': [],
}

def check_file_extension(fname):
    """Takes a filename that is provided by the user and performs a check 
    if the file extension is allowed before returning the filename. Otherwise
    raises a TypeError.

    Parameter fname: The filename w/ extension provided by the user. """
    accepted_ext = ['.json', '.csv', '.xlsx']
    if not any(fname.endswith(ext) for ext in accepted_ext):
        raise argparse.ArgumentTypeError(f"The file must end with the following extension: {', '.join(accepted_ext)}")
    return fname
    
async def data_processor(list_of_targets: list[dict], fname: str | None = None):
    """Takes a list of dictionaries and a file name as the parameters
    if user exports data to one of the following extensions 
    [.json, .csv, .xlsx]. A file will be created within the 'whitepages'
    folder. Otherwise displays the found data as a dataframe.

    Parameter list_of_targets: a list of dictionaries containing found data.
    Parameter fname: The file name and extension provided by the user."""
    for x in range(len(list_of_targets)):
        target = list_of_targets[x]['item']
        TARGET_INFORMATION['url'].append(BASE_URL + target.get('url', None))
        TARGET_INFORMATION['aliases'].append(target.get('alternateName', None))
        TARGET_INFORMATION['given_name'].append(target.get('givenName', None))
        TARGET_INFORMATION['family_name'].append(target.get('familyName', None))
        target_address = target.get('address', None)
        target_works_for = target.get('worksFor', None)
        target_occupation = target.get('hasOccupation', None)
        target_contained_in = target.get('containedInPlace', None)
        if target_address:
            street_address = target_address[0].get('streetAddress', '')
            address_locality = target_address[0].get('addressLocality', '')
            address_region = target_address[0].get('addressRegion', '')
            address_country = target_address[0].get('addressCountry', '')
            TARGET_INFORMATION['address'].append(
                street_address + " " + address_locality + " " + address_region + " " + address_country)
        if target_works_for:
            TARGET_INFORMATION['works_for'].append(target_works_for.get('legalName', None))
        if target_occupation:
            TARGET_INFORMATION['occupation'].append(target_occupation.get('name', None))
        if target_contained_in:
            place = target_contained_in[0]['name']
            country = target_contained_in[0]['address']['addressCountry']
            state = target_contained_in[0]['address']['addressRegion']
            TARGET_INFORMATION['contained_in'].append(place + " " + state + " " + country)
        
        relatives = []
        target_relatives = target.get('relatedTo', None)
        for y in range(len(target_relatives)):
            relatives.append(target_relatives[y]['name'])
        TARGET_INFORMATION['relatives'].append(relatives)
        TARGET_INFORMATION['telephone'].append(target.get('telephone', None))
        TARGET_INFORMATION['description'].append(target.get('description', None))
    
    df = pd.DataFrame.from_dict(TARGET_INFORMATION, orient='index').transpose()
    
    if not fname:
        return df
    elif fname.endswith('.json'):
        await to_json(TARGET_INFORMATION, fname)
    elif fname.endswith('.csv'):
        await to_csv(df, fname)
    elif fname.endswith('.xlsx'):
        await to_xlsx(df, fname)

async def search_by_name(
    first_name: str, 
    last_name: str, 
    city: None | str = None, 
    state: None | str = None
) -> dict:
    """Search target via whitepages by means of first_name, 
    last_name and optionally by city and state. Returns a dictionary
    containing found data. Otherwise displays the status_code when upon failure.
    
    Parameter first_name: A string provided by the user (required using -n flag).
    Parameter last_name: A string provided by the user (required using -n flag).
    Parameter city: A string provided by the user (optional using -ei flag).
    Parameter state: A string provided by the user (optional using -ei flag)"""
    search_by_name = BASE_URL + f"/name/{first_name}-{last_name}"
    search_by_city_state = BASE_URL + f"/name/{first_name}-{last_name}/{city}-{state}"
    url = search_by_city_state if city and state else search_by_name

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                logger.error(f"Network issue found: {resp.status}")
            else:
                logger.info(f"Success! status: {resp.status}")
                text_data = await resp.text()
                json_start = text_data.find('</style><script type="application/ld+json">')
                json_end = text_data.find('</script>', json_start)
                cleaned_json_string = text_data[json_start+43:json_end]
                json_dict = json.loads(cleaned_json_string)
                return json_dict

async def to_xlsx(df, fname):
    """Takes in a Pandas DataFrame (provided a status of 200 achieved AND if user
    requests for .xlsx to be written), As well as the filename w/ extension provided 
    by the user. Using the pandas library/package to write .xlsx file.
    
    *Library/Package Required: pandas and openpyxl*
    
    Parameter df: A Pandas DataFrame containing the found data.
    Parameter fname: A string, the filename w/ extension provided by the user."""
    logger.info(f"Please be patient the data gets written to a .xlsx file.")
    df.to_excel(fname)
    logger.info("Writing Complete!")

async def to_csv(df, fname):
    """Takes in a Pandas DataFrame (provided a status of 200 achieved AND if user
    requests for a .csv file to be written), As well as the filename w/ extension provided 
    by the user. Using the pandas library/package to write .csv file.
    
    Parameter df: A Pandas Dataframe containing the found data.
    Parameter fname: A string, the filename w/ extension provided by the user."""
    logger.info(f"Please be patient the data gets written to a .csv file.")
    df.to_csv(fname)
    logger.info("Writing Complete!")

async def to_json(adict: dict, fname: str):
    """Takes in a dictionary (provided a status of 200 was achieved AND if the user
    requests for a .json file to be written), As well as the filename w/ extension
    provided by the user.
    
    Parameter adict: A dictionary containing the found data.
    Parameter fname: A string, the filename w/ extension provided by the user."""
    with open(f'{fname}', 'w') as f:
        logger.info("Dumping json response..")
        json_dump = json.dump(adict, f, indent=4, sort_keys=True)
        logger.info("Dump Complete!")

async def judge_dredd(APP_DATA: dict):
    """The Judge. The final bastion of sanity.
    
    Parameter APP_DATA: A dictionary, contains the user data inserted at the terminal."""
    assert isinstance(APP_DATA['first_name'], str), "First name needs to be a string."
    assert isinstance(APP_DATA['last_name'], str), "Last name needs to be a string."
    if APP_DATA['city'] or APP_DATA['state']:
        assert isinstance(APP_DATA['city'], str), "City needs to be a string."
        assert isinstance(APP_DATA['state'], str), "State needs to be a string."

async def main(APP_DATA: dict, args: argparse.Namespace | None = None):
    """Takes in a dictionary and a Namespace datatype
    makes several checks before displaying/writing data.
    
    Parameter APP_DATA: A dictionary containing the application data used throughout the program.
    Parameter args: a Namespace data type containing the arguments that was passed to the program."""
    all_good = False
    
    while not all_good:
        if APP_DATA['first_name']:
            if APP_DATA['first_name'].isnumeric():
                logger.warning("First name must be a string: ")
                APP_DATA['first_name'] = input('Please enter first name.')
                continue
        if APP_DATA['last_name']:
            if APP_DATA['last_name'].isnumeric():
                logger.warning("Last name must be a string: ")
                APP_DATA['last_name'] = input("Please enter last name.")
                continue
        if APP_DATA['city']:
            if APP_DATA['city'].isnumeric():
                logger.info('City must be a string.')
                APP_DATA['city'] = input("Please enter a city: ")
                continue
        if APP_DATA['state']:
            if APP_DATA['state'].isnumeric():
                logger.info("State must be a string.")
                APP_DATA['state'] = input("Please enter a state: ")
                continue
        logger.info("Saving information")
        
        logger.info("All good")
        all_good = True
    
    logger.info("Performing assertion..the last bastion.")
    await judge_dredd(APP_DATA) 
    
    logger.info("Continuing, Now searching..")

    target = await search_by_name(
        APP_DATA['first_name'],
        APP_DATA['last_name'],
        APP_DATA['city'],
        APP_DATA['state'])
        
    list_of_targets = target[0]['itemListElement']
    
    logger.info("Complete..")

    if args.json_file:
        await data_processor(list_of_targets, args.json_file)
    elif args.csv_file:
        await data_processor(list_of_targets, args.csv_file)
    elif args.xlsx_file:
        await data_processor(list_of_targets, args.xlsx_file)
    else:
        df = await data_processor(list_of_targets)
        logger.info(f"\n{df}")
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Search information on person via WhitePages.")

    parser.add_argument(
        '-n', 
        '--name', 
        nargs=2,
        metavar=('FIRSTNAME', 'LASTNAME'),
        help='Provide first name and last name.)', 
        required=True)

    parser.add_argument(
        '-ei',
        '--extra_information',
        nargs=2,
        metavar=('CITY', 'STATE'),
        help='Provide a city and state',
        required=False)

    parser.add_argument(
        '-json', 
        '--json_file',
        metavar='JSONFILE', 
        help='Write found data to a JSON file.', 
        type=check_file_extension,
        required=False)

    parser.add_argument(
        '-csv',
        '--csv_file',
        metavar='CSVFILE',
        help='Write found data to a CSV file.',
        type=check_file_extension,
        required=False)

    parser.add_argument(
        '-xlsx',
        '--xlsx_file',
        metavar='XLSXFILE',
        help='Write found data to a XLSX file.',
        type=check_file_extension,
        required=False)

    args = parser.parse_args()

    first_name, last_name = args.name
    city, state = args.extra_information if args.extra_information else (None, None)

    APP_DATA = {
        "first_name": first_name,
        "last_name": last_name,
        "city": city,
        "state": state,
    }

    asyncio.run(main(APP_DATA, args))