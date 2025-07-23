"""
Hospital Recommendation Agent using SERP API
Finds and ranks hospitals based on medical conditions
"""
from typing import Optional, Dict, List
import streamlit as st
from config import config
from tools.serp_search_tool import SerpSearchTool

class HospitalAgent:
    """Agent for finding and ranking hospitals using SERP API"""
    
    def __init__(self):
        """Initialize the hospital recommendation agent"""
        try:
            self.serp_tool = SerpSearchTool()
            self.location = config.SEARCH_LOCATION
        except Exception as e:
            st.error(f"Failed to initialize Hospital Agent: {e}")
            self.serp_tool = None
    
    def find_hospitals(self, medical_report: Dict) -> Optional[Dict]:
        """
        Find top hospitals based on medical conditions
        
        Args:
            medical_report: Dictionary containing medical analysis
            
        Returns:
            Dictionary containing ranked hospital recommendations or None if failed
        """
        if not self.serp_tool or not medical_report:
            return None
            
        try:
            # Extract medical conditions
            conditions = self._extract_conditions(medical_report)
            
            # Build search queries and get hospitals
            all_hospitals = []
            for condition in conditions[:2]:  # Limit to 2 conditions to avoid too many API calls
                hospitals = self.serp_tool.search_hospitals(condition, self.location)
                if hospitals:
                    all_hospitals.extend(hospitals)
            
            # If no hospitals found from conditions, try fallback search
            if not all_hospitals:
                hospitals = self.serp_tool.search_hospitals("general medical care", self.location)
                if hospitals:
                    all_hospitals.extend(hospitals)
            
            # Rank and filter hospitals
            ranked_hospitals = self._rank_hospitals(all_hospitals)
            
            # Structure the recommendations
            recommendations = self._structure_recommendations(ranked_hospitals[:3])
            return recommendations
                
        except Exception as e:
            st.error(f"Error finding hospitals: {e}")
            return None
    
    def _extract_conditions(self, medical_report: Dict) -> List[str]:
        """Extract relevant medical conditions for hospital search"""
        conditions = []
        try:
            # Get primary findings from clinical impression
            if 'clinical_impression' in medical_report:
                findings = medical_report['clinical_impression'].get('primary_findings', [])
                conditions.extend([f.strip() for f in findings if f.strip()])
            
            # Get diagnoses
            if 'diagnoses' in medical_report:
                diagnoses = medical_report.get('diagnoses', [])
                conditions.extend([d.strip() for d in diagnoses if d.strip()])
            
            # Get findings
            if 'findings' in medical_report:
                findings = medical_report.get('findings', [])
                conditions.extend([f.strip() for f in findings if f.strip()])
            
            # Clean and filter conditions
            cleaned_conditions = []
            for condition in conditions:
                if condition and len(condition) > 3 and 'not specified' not in condition.lower():
                    cleaned_conditions.append(condition)
            
            # Ensure we have at least one condition
            if not cleaned_conditions:
                cleaned_conditions = ['general medical care']
                
            return cleaned_conditions[:3]  # Limit to 3 conditions
                
        except Exception as e:
            st.warning(f"Error extracting conditions: {e}")
            return ['general medical care']
    
    def _rank_hospitals(self, hospitals: List[Dict]) -> List[Dict]:
        """
        Rank hospitals based on multiple criteria
        
        Ranking factors:
        1. Position in search results (lower is better)
        2. Presence of keywords indicating quality
        3. Hospital name recognition
        """
        try:
            # Calculate ranking score for each hospital
            for hospital in hospitals:
                score = 0
                
                # Position score (lower position = higher score)
                position = hospital.get('position', 10)
                score += max(0, 10 - position)
                
                # Quality indicators in description
                description = hospital.get('description', '').lower()
                quality_keywords = ['best', 'top', 'leading', 'premier', 'advanced', 'specialized']
                for keyword in quality_keywords:
                    if keyword in description:
                        score += 2
                
                # Recognized hospital names
                name = hospital.get('name', '').lower()
                recognized_names = ['aiims', 'apollo', 'fortis', 'max', 'medanta', 'manipal', 'tata memorial']
                for recognized in recognized_names:
                    if recognized in name:
                        score += 3
                        break
                
                hospital['ranking_score'] = score
            
            # Sort by ranking score (highest first)
            ranked_hospitals = sorted(hospitals, key=lambda x: x.get('ranking_score', 0), reverse=True)
            
            # Remove duplicates by name
            seen_names = set()
            unique_hospitals = []
            for hospital in ranked_hospitals:
                name = hospital.get('name', '').lower()
                if name not in seen_names:
                    seen_names.add(name)
                    unique_hospitals.append(hospital)
            
            return unique_hospitals
            
        except Exception as e:
            st.warning(f"Error ranking hospitals: {e}")
            return hospitals  # Return unranked list if ranking fails
    
    def _structure_recommendations(self, hospitals: List[Dict]) -> Dict:
        """Structure the hospital recommendations"""
        recommendations = {
            'top_hospitals': [],
            'search_location': self.location,
            'total_found': len(hospitals)
        }
        
        try:
            for hospital in hospitals:
                hospital_info = {
                    'name': hospital.get('name', 'Name not available'),
                    'address': 'Address not available',  # SERP doesn't provide address directly
                    'phone': 'Contact hospital directly',
                    'rating': 'Not available',
                    'reviews': 'See website for reviews',
                    'description': hospital.get('description', 'No description available'),
                    'website': hospital.get('url', None),
                    'emergency': 'emergency' in hospital.get('description', '').lower() or 'trauma' in hospital.get('description', '').lower(),
                    'specialties': self._extract_specialties(hospital.get('description', ''))
                }
                recommendations['top_hospitals'].append(hospital_info)
                
        except Exception as e:
            st.error(f"Error structuring recommendations: {e}")
            recommendations['top_hospitals'] = [{
                'name': 'Error processing hospital information',
                'description': 'Please try again or search manually',
                'address': 'Not available',
                'phone': 'Not available',
                'rating': 'Not available',
                'reviews': 'Not available',
                'website': None,
                'emergency': False,
                'specialties': ['General Medicine']
            }]
            
        return recommendations
    
    def _extract_specialties(self, description: str) -> List[str]:
        """Extract medical specialties from hospital description"""
        specialties = []
        common_specialties = [
            'cardiology', 'orthopedics', 'neurology', 'oncology', 'pediatrics',
            'gynecology', 'urology', 'ent', 'ophthalmology', 'dermatology',
            'psychiatry', 'endocrinology', 'gastroenterology', 'pulmonology',
            'nephrology', 'rheumatology', 'emergency', 'trauma', 'surgery'
        ]
        
        description_lower = description.lower()
        for specialty in common_specialties:
            if specialty in description_lower:
                specialties.append(specialty.title())
                
        return specialties or ['General Medicine'] 