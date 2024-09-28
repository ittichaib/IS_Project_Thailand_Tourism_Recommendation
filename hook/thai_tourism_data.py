import os
import requests
from typing import List, Optional
from dotenv import load_dotenv
from typing import Optional, List, Dict

# Load environment variables from .env file
load_dotenv()

class Category:
    def __init__(self, category_id: int, name: str, icon: Optional[str] = None):
        self.category_id = category_id
        self.name = name
        self.icon = icon

class ShaType:
    def __init__(self, type_id: int, name: str):
        self.type_id = type_id
        self.name = name

class Sha:
    def __init__(self, name: str, detail: str, thumbnail_url: str, sha_type: ShaType, sha_category: Category):
        self.name = name
        self.detail = detail
        self.thumbnail_url = thumbnail_url
        self.sha_type = sha_type
        self.sha_category = sha_category

class Location:
    def __init__(self, address: str, province: Dict[str, int], district: Dict[str, int], sub_district: Dict[str, int], postcode: str):
        self.address = address
        self.province = province
        self.district = district
        self.sub_district = sub_district
        self.postcode = postcode

class ThaiTourismData:
    def __init__(self, place_id: int, name: str, introduction: str, category: Category,
                 sha: Sha, latitude: float, longitude: float, location: Location,
                 thumbnail_url: List[str], tags: List[str], distance: float,
                 created_at: str, updated_at: str):
        self.place_id = place_id
        self.name = name
        self.introduction = introduction
        self.category = category
        self.sha = sha
        self.latitude = latitude
        self.longitude = longitude
        self.location = location
        self.thumbnail_url = thumbnail_url
        self.tags = tags
        self.distance = distance
        self.created_at = created_at
        self.updated_at = updated_at

class ThaiTourismAPI:
    # BASE_URL = "https://tatapi.tourismthailand.org/tatapi/v5/places"
    BASE_URL = "https://tatdataapi.io/api/v2/places"

    def __init__(self, language: str):
        self.api_key = os.getenv('TAT_API_KEY')  # Load the API key from environment variables
        self.api_key_v2 = os.getenv('TAT_API_KEY_V2')
        if not self.api_key_v2:
            raise ValueError("API key not found. Please set the TAT_API_KEY_V2 environment variable.")
        if not self.api_key:
            raise ValueError("API key not found. Please set the TAT_API_KEY environment variable.")
        self.session = requests.Session()
        self.language = language

    def fetch_search_location(self, keyword: str, location: str, categorycodes: str,
                              province_name: str, radius: int, number_of_result: int,
                              page_number: int, destination: str, filter_by_update_date: str) -> List[ThaiTourismData]:
        url = f"{self.BASE_URL}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept-Language": self.language,
            "x-api-key": self.api_key_v2
        }
        params = {
            "keyword": keyword,
            # "location": location,
            "categorycodes": categorycodes,
            "provinceName": province_name,
            "radius": radius,
            "numberOfResult": number_of_result,
            "pagenumber": page_number,
            "destination": destination,
            # "filterByUpdateDate": filter_by_update_date
        }

        try:
            # Make the request with SSL verification enabled
            response = self.session.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an error for bad responses

            # Extract the JSON response
            places_data = response.json().get("data", [])
            print(places_data)
            return [ThaiTourismData(
                place_id=place["placeId"],
                name=place["name"],
                introduction=place.get("introduction", ""),  # Use .get() for optional fields
                category=Category(
                    category_id=place["category"]["categoryId"],
                    name=place["category"]["name"]
                ),
                sha=Sha(
                    name=place["sha"]["name"],
                    detail=place["sha"].get("detail", ""),  # Optional field
                    thumbnail_url=place["sha"]["thumbnailUrl"],
                    sha_type=ShaType(
                        type_id=place["sha"]["type"]["typeId"],
                        name=place["sha"]["type"]["name"]
                    ),
                    sha_category=Category(
                        category_id=place["sha"]["category"]["categoryId"],
                        name=place["sha"]["category"]["name"],
                        icon=place["sha"]["category"].get("icon", "")  # Optional field
                    )
                ),
                latitude=place["latitude"],
                longitude=place["longitude"],
                location=Location(
                    address=place["location"]["address"],
                    province={
                        "provinceId": place["location"]["province"]["provinceId"],
                        "name": place["location"]["province"]["name"]
                    },
                    district={
                        "districtId": place["location"]["district"]["districtId"],
                        "name": place["location"]["district"]["name"]
                    },
                    sub_district={
                        "subDistrictId": place["location"]["subDistrict"]["subDistrictId"],
                        "name": place["location"]["subDistrict"]["name"]
                    },
                    postcode=place["location"]["postcode"]
                ),
                thumbnail_url=place.get("thumbnailUrl", []),  # Optional field as list
                tags=place.get("tags", []),  # Optional field as list
                distance=place["distance"],
                created_at=place["createdAt"],
                updated_at=place["updatedAt"]
            ) for place in places_data]

        except requests.exceptions.SSLError as e:
            print("SSL Error: ", e)
            return []
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed: ", e)
            return []
    
if __name__ == "__main__":
    # Example usage:
    thai_tourism_api = ThaiTourismAPI("EN")
    
    # Define the search parameters
    search_params = {
        "keyword": "กาญจนบุรี",  # Example keyword for Kanchanaburi
        "location": "13.6904831,100.5226014",
        "categorycodes": "RESTAURANT",
        "province_name": "Kanchanaburi",
        "radius": 20,
        "number_of_result": 10,
        "page_number": 1,
        "destination": "Kanchanaburi",
        "filter_by_update_date": "2019/09/01-2021/12/31"
    }

    # Fetch search locations based on the parameters
    recommended_places = thai_tourism_api.fetch_search_location(**search_params)

    for place in recommended_places:
        print(f"Place Name: {place.place_name}, Province: {place.province}, Latitude: {place.latitude}, Longitude: {place.longitude}")
