"""
SERP API tool for hospital search functionality
"""
import requests
import json
from typing import List, Dict, Optional
from config import config

class SerpSearchTool:
    """Tool for searching hospitals using SERP API"""
    
    def __init__(self):
        self.api_key = config.SERP_API_KEY
        self.base_url = "https://serpapi.com/search.json"
    
    def search_hospitals(self, diagnosis: str, location: str = "India") -> List[Dict]:
        """
        Search for hospitals treating specific condition
        
        Args:
            diagnosis: Medical condition/diagnosis
            location: Location to search in
            
        Returns:
            List of hospital information dictionaries
        """
        try:
            # Check if API key is configured
            if not self.api_key or self.api_key == "your_serp_api_key_here":
                print("SERP API key not configured. Using fallback hospitals.")
                return self._get_fallback_hospitals(diagnosis, location)
            
            # Construct search query
            query = f"best hospitals for {diagnosis} treatment in {location}"
            
            # SERP API parameters
            params = {
                "q": query,
                "api_key": self.api_key,
                "engine": "google",
                "num": config.MAX_HOSPITALS,
                "location": location
            }
            
            # Make API request
            response = requests.get(self.base_url, params=params, timeout=10)
            
            # Handle different HTTP status codes
            if response.status_code == 401:
                print("SERP API key is invalid or expired. Using fallback hospitals.")
                return self._get_fallback_hospitals(diagnosis, location)
            elif response.status_code == 429:
                print("SERP API rate limit exceeded. Using fallback hospitals.")
                return self._get_fallback_hospitals(diagnosis, location)
            elif response.status_code != 200:
                print(f"SERP API returned status code {response.status_code}. Using fallback hospitals.")
                return self._get_fallback_hospitals(diagnosis, location)
            
            data = response.json()
            hospitals = []
            
            # Extract organic results
            organic_results = data.get("organic_results", [])
            
            if not organic_results:
                print("No hospital results found from SERP API. Using fallback hospitals.")
                return self._get_fallback_hospitals(diagnosis, location)
            
            for result in organic_results[:config.MAX_HOSPITALS]:
                hospital_info = {
                    "name": result.get("title", "Unknown Hospital"),
                    "description": result.get("snippet", "No description available"),
                    "url": result.get("link", "#"),
                    "position": result.get("position", 0)
                }
                hospitals.append(hospital_info)
            
            return hospitals
            
        except requests.exceptions.Timeout:
            print("SERP API request timed out. Using fallback hospitals.")
            return self._get_fallback_hospitals(diagnosis, location)
        except requests.exceptions.ConnectionError:
            print("Failed to connect to SERP API. Using fallback hospitals.")
            return self._get_fallback_hospitals(diagnosis, location)
        except requests.exceptions.RequestException as e:
            print(f"SERP API request error: {e}. Using fallback hospitals.")
            return self._get_fallback_hospitals(diagnosis, location)
        except json.JSONDecodeError:
            print("Invalid JSON response from SERP API. Using fallback hospitals.")
            return self._get_fallback_hospitals(diagnosis, location)
        except Exception as e:
            print(f"Unexpected error with SERP API: {e}. Using fallback hospitals.")
            return self._get_fallback_hospitals(diagnosis, location)
    
    def _get_fallback_hospitals(self, diagnosis: str, location: str) -> List[Dict]:
        """
        Provide fallback hospital list when API fails
        
        Args:
            diagnosis: Medical condition
            location: Location
            
        Returns:
            List of fallback hospitals
        """
        fallback_hospitals = [
            {
                "name": "All India Institute of Medical Sciences (AIIMS), New Delhi",
                "description": "Premier medical institute offering comprehensive healthcare services",
                "url": "https://www.aiims.edu/",
                "position": 1
            },
            {
                "name": "Apollo Hospitals",
                "description": "Leading healthcare provider with multiple locations across India",
                "url": "https://www.apollohospitals.com/",
                "position": 2
            },
            {
                "name": "Fortis Healthcare",
                "description": "Multi-specialty healthcare provider with advanced medical facilities",
                "url": "https://www.fortishealthcare.com/",
                "position": 3
            },
            {
                "name": "Max Healthcare",
                "description": "Premium healthcare network with state-of-the-art facilities",
                "url": "https://www.maxhealthcare.in/",
                "position": 4
            },
            {
                "name": "Medanta - The Medicity",
                "description": "Multi-super specialty hospital with advanced medical technology",
                "url": "https://www.medanta.org/",
                "position": 5
            }
        ]
        
        return fallback_hospitals
    
    def search_specialist_doctors(self, diagnosis: str, location: str = "India") -> List[Dict]:
        """
        Search for specialist doctors for specific condition
        
        Args:
            diagnosis: Medical condition
            location: Location to search in
            
        Returns:
            List of doctor information
        """
        try:
            query = f"best doctors specialists for {diagnosis} in {location}"
            
            params = {
                "q": query,
                "api_key": self.api_key,
                "engine": "google",
                "num": 5,
                "location": location
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            doctors = []
            
            organic_results = data.get("organic_results", [])
            
            for result in organic_results[:5]:
                doctor_info = {
                    "name": result.get("title", "Specialist Doctor"),
                    "description": result.get("snippet", "Medical specialist"),
                    "url": result.get("link", "#")
                }
                doctors.append(doctor_info)
            
            return doctors
            
        except Exception as e:
            print(f"Error searching for doctors: {e}")
            return []
    
    def validate_api_key(self) -> bool:
        """
        Validate SERP API key
        
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            params = {
                "q": "test",
                "api_key": self.api_key,
                "engine": "google",
                "num": 1
            }
            
            response = requests.get(self.base_url, params=params)
            return response.status_code == 200
            
        except Exception:
            return False 