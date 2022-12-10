from smartystreets_python_sdk import StaticCredentials, exceptions, ClientBuilder
from smartystreets_python_sdk.us_street import Lookup as StreetLookup
from .config import get_smarty_auth_id, get_smarty_auth_token
from typing import Dict, Tuple

usa_alias = {'usa', 'USA', 'us', 'US', 'united states',
             'United States', 'united states of america', 'United States of America'}

def verify_address(address: Dict[str, str]) -> Tuple[bool, str, Dict[str, str]]:
    """
    return: check passed, comment, correct address
    """
    required_fields = ["description", 
                       "country",
                       "state",
                       "city",
                       "zip_code",
                       "street"]
    for field in required_fields:
        if field not in address:
            return False, "invalid_input", {}

    if address['country'] not in usa_alias:
        return True, "not usa address", address
    
    try:
        credentials = StaticCredentials(get_smarty_auth_id(), get_smarty_auth_token())
        client = ClientBuilder(credentials).with_licenses(["us-core-cloud"]).build_us_street_api_client()
    except:
        return True, "invalid smarty credentials", address

    lookup = StreetLookup()
    lookup.input_id = ""  # Optional ID from your system
    lookup.addressee = ""
    lookup.street = address['street']
    lookup.street2 = ""
    lookup.secondary = ""
    lookup.urbanization = ""  # Only applies to Puerto Rico addresses
    lookup.city = address['city']
    lookup.state = address['state']
    lookup.zipcode = address['zip_code']
    lookup.candidates = 3
    lookup.match = "invalid"

    try:
        client.send_lookup(lookup)
    except exceptions.SmartyException as err:
        print(err)
        True, f"smarty lookup error: {repr(err)}", address

    result = lookup.result
    if not result:
        print("No candidates. This means the address is not valid.")
        False, "invalid address", {}

    # result[0].analysis.dpv_match_code, Y, S, D -> valid, N -> invalid
    if result[0].analysis.dpv_match_code not in {'Y', 'S', 'D'}:
        return False, "invalid address", {}
    correct_address = {
        "description": address['description'],
        "country": address['country'], # only support USA
        "state": result[0].components.state_abbreviation,
        "city": result[0].components.default_city_name,
        "zip_code": result[0].components.zipcode,
        "street": result[0].delivery_line_1,
    }
    if result[0].analysis.dpv_match_code == 'Y':
        message = "valid address"
    else:
        message = "valid address with minor change"
    return True, message, correct_address

    
        




