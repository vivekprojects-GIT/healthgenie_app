"""
SERP Hospital Search Agent
Advanced hospital recommendation system using SERP API with intelligent condition-based search
"""
from typing import Optional, Dict, List, Tuple
import streamlit as st
from config import config
from tools.serp_search_tool import SerpSearchTool
import re

class SerpHospitalAgent:
    """Advanced agent for finding hospitals using SERP API with intelligent search strategies"""
    
    def __init__(self):
        """Initialize the SERP hospital search agent"""
        try:
            self.serp_tool = SerpSearchTool()
            self.location = config.SEARCH_LOCATION
            
            # Medical specialty mapping for targeted searches
            self.specialty_keywords = {
                'cardiac': ['cardiology', 'heart', 'cardiac', 'cardiovascular', 'coronary'],
                'pulmonary': ['pulmonology', 'lung', 'respiratory', 'chest', 'breathing'],
                'orthopedic': ['orthopedics', 'bone', 'joint', 'spine', 'fracture'],
                'neurological': ['neurology', 'brain', 'neuro', 'stroke', 'nervous'],
                'oncology': ['cancer', 'oncology', 'tumor', 'malignancy', 'chemotherapy'],
                'gastro': ['gastroenterology', 'stomach', 'liver', 'digestive', 'intestine'],
                'emergency': ['emergency', 'trauma', 'critical', 'urgent', 'accident'],
                'pediatric': ['pediatric', 'children', 'child', 'infant', 'kids'],
                'gynecology': ['gynecology', 'women', 'pregnancy', 'obstetrics', 'maternity']
            }
            
            # Condition severity indicators
            self.severity_indicators = {
                'critical': ['severe', 'critical', 'acute', 'emergency', 'urgent', 'life-threatening'],
                'moderate': ['moderate', 'significant', 'notable', 'concerning'],
                'mild': ['mild', 'minor', 'slight', 'early', 'initial']
            }
            
            # Top-tier hospital names for quality ranking
            self.premium_hospitals = [
                'aiims', 'apollo', 'fortis', 'max', 'medanta', 'manipal', 
                'tata memorial', 'pgimer', 'christian medical college',
                'sankara nethralaya', 'narayana health', 'aster'
            ]
            
        except Exception as e:
            st.error(f"Failed to initialize SERP Hospital Agent: {e}")
            self.serp_tool = None
    
    def find_best_hospitals(self, medical_analysis: Dict) -> Optional[Dict]:
        """
        Find best hospitals based on comprehensive medical analysis
        
        Args:
            medical_analysis: Complete medical analysis from combined results
            
        Returns:
            Dictionary with ranked hospital recommendations
        """
        if not self.serp_tool or not medical_analysis:
            return None
            
        try:
            # Analyze medical conditions and extract search parameters
            search_strategy = self._analyze_medical_conditions(medical_analysis)
            
            # Execute intelligent hospital search
            hospital_results = self._execute_intelligent_search(search_strategy)
            
            # Rank hospitals based on medical relevance
            ranked_hospitals = self._rank_hospitals_by_medical_relevance(
                hospital_results, search_strategy
            )
            
            # Structure final recommendations
            recommendations = self._structure_medical_recommendations(
                ranked_hospitals, search_strategy
            )
            
            return recommendations
            
        except Exception as e:
            st.error(f"Error in SERP hospital search: {e}")
            return None
    
    def _analyze_medical_conditions(self, medical_analysis: Dict) -> Dict:
        """Analyze medical conditions to determine optimal search strategy"""
        strategy = {
            'primary_conditions': [],
            'specialties': [],
            'severity': 'moderate',
            'urgency': 'routine',
            'search_terms': [],
            'condition_keywords': []
        }
        
        try:
            # Extract conditions from various sources
            all_conditions = []
            
            # From clinical impression
            if 'clinical_impression' in medical_analysis:
                clinical = medical_analysis['clinical_impression']
                all_conditions.extend(clinical.get('primary_findings', []))
                
                # Extract severity
                severity = clinical.get('severity', 'moderate')
                if severity and severity != 'Not specified':
                    strategy['severity'] = severity.lower()
            
            # From findings and diagnoses
            all_conditions.extend(medical_analysis.get('findings', []))
            all_conditions.extend(medical_analysis.get('diagnoses', []))
            
            # Clean and process conditions
            processed_conditions = self._process_medical_conditions(all_conditions)
            strategy['primary_conditions'] = processed_conditions
            
            # Determine medical specialties needed
            strategy['specialties'] = self._identify_required_specialties(processed_conditions)
            
            # Determine urgency level
            strategy['urgency'] = self._assess_urgency(processed_conditions, strategy['severity'])
            
            # Generate intelligent search terms
            strategy['search_terms'] = self._generate_search_terms(
                processed_conditions, strategy['specialties'], strategy['urgency']
            )
            
            # Extract condition-specific keywords
            strategy['condition_keywords'] = self._extract_condition_keywords(processed_conditions)
            
            return strategy
            
        except Exception as e:
            st.warning(f"Error analyzing medical conditions: {e}")
            return {
                'primary_conditions': ['general medical care'],
                'specialties': ['general'],
                'severity': 'moderate',
                'urgency': 'routine',
                'search_terms': [f'best hospitals {self.location}'],
                'condition_keywords': []
            }
    
    def _process_medical_conditions(self, raw_conditions: List[str]) -> List[str]:
        """Process and clean medical conditions"""
        processed = []
        
        for condition in raw_conditions:
            if not condition or len(condition.strip()) < 3:
                continue
                
            condition = condition.strip().lower()
            
            # Skip generic terms
            skip_terms = [
                'not specified', 'analysis completed', 'see detailed',
                'medical report', 'x-ray analysis', 'further evaluation'
            ]
            
            if any(skip in condition for skip in skip_terms):
                continue
            
            # Clean up condition text
            condition = re.sub(r'\s+', ' ', condition)  # Remove extra spaces
            condition = condition.strip('.-*• ')  # Remove bullet points and punctuation
            
            if len(condition) > 3:
                processed.append(condition)
        
        return processed[:5]  # Limit to top 5 conditions
    
    def _identify_required_specialties(self, conditions: List[str]) -> List[str]:
        """Identify medical specialties based on conditions"""
        specialties = set()
        
        for condition in conditions:
            condition_lower = condition.lower()
            
            for specialty, keywords in self.specialty_keywords.items():
                if any(keyword in condition_lower for keyword in keywords):
                    specialties.add(specialty)
        
        # If no specific specialty found, determine from condition context
        if not specialties:
            for condition in conditions:
                condition_lower = condition.lower()
                
                if any(word in condition_lower for word in ['pain', 'ache', 'swelling']):
                    specialties.add('general')
                elif any(word in condition_lower for word in ['infection', 'fever']):
                    specialties.add('general')
        
        return list(specialties) if specialties else ['general']
    
    def _assess_urgency(self, conditions: List[str], severity: str) -> str:
        """Assess urgency level based on conditions and severity"""
        if severity in ['severe', 'critical']:
            return 'urgent'
        
        # Check for urgent condition keywords
        urgent_keywords = [
            'emergency', 'urgent', 'acute', 'severe', 'critical',
            'heart attack', 'stroke', 'trauma', 'bleeding'
        ]
        
        for condition in conditions:
            condition_lower = condition.lower()
            if any(keyword in condition_lower for keyword in urgent_keywords):
                return 'urgent'
        
        return 'routine'
    
    def _generate_search_terms(self, conditions: List[str], specialties: List[str], urgency: str) -> List[str]:
        """Generate intelligent search terms for hospital search"""
        search_terms = []
        
        try:
            # Base search terms
            if urgency == 'urgent':
                base_terms = ['best emergency hospitals', 'top trauma centers', '24/7 emergency care']
            else:
                base_terms = ['best hospitals', 'top medical centers', 'leading healthcare']
            
            # Add location to base terms
            for term in base_terms:
                search_terms.append(f"{term} {self.location}")
            
            # Specialty-specific searches
            for specialty in specialties[:2]:  # Limit to top 2 specialties
                if specialty != 'general':
                    search_terms.append(f"best {specialty} hospitals {self.location}")
                    search_terms.append(f"top {specialty} specialists {self.location}")
            
            # Condition-specific searches
            for condition in conditions[:2]:  # Limit to top 2 conditions
                # Clean condition for search
                clean_condition = re.sub(r'[^\w\s]', '', condition)
                search_terms.append(f"best hospitals for {clean_condition} {self.location}")
            
            # Premium hospital searches
            premium_search = f"AIIMS Apollo Fortis Max Medanta {self.location}"
            search_terms.append(premium_search)
            
            return search_terms[:6]  # Limit to 6 search terms to avoid API limits
            
        except Exception as e:
            st.warning(f"Error generating search terms: {e}")
            return [f"best hospitals {self.location}"]
    
    def _extract_condition_keywords(self, conditions: List[str]) -> List[str]:
        """Extract relevant keywords from conditions for hospital matching"""
        keywords = set()
        
        for condition in conditions:
            # Split condition into words and extract meaningful terms
            words = re.findall(r'\b\w{4,}\b', condition.lower())  # Words with 4+ characters
            keywords.update(words)
        
        # Remove common medical terms that don't help with hospital selection
        exclude_words = {
            'patient', 'medical', 'condition', 'diagnosis', 'treatment',
            'analysis', 'report', 'finding', 'result', 'examination'
        }
        
        filtered_keywords = [kw for kw in keywords if kw not in exclude_words]
        return filtered_keywords[:10]  # Limit to top 10 keywords
    
    def _execute_intelligent_search(self, search_strategy: Dict) -> List[Dict]:
        """Execute intelligent hospital search using multiple strategies"""
        all_hospitals = []
        
        try:
            # Check if SERP API key is valid
            if not self.serp_tool or config.SERP_API_KEY == "your_serp_api_key_here":
                st.warning("⚠️ SERP API key not configured. Using fallback hospital recommendations.")
                return self._get_fallback_hospitals(search_strategy)
            
            # Execute searches for each search term
            for search_term in search_strategy['search_terms']:
                try:
                    hospitals = self.serp_tool.search_hospitals(search_term, self.location)
                    if hospitals:
                        # Tag hospitals with search context
                        for hospital in hospitals:
                            hospital['search_context'] = search_term
                            hospital['search_strategy'] = search_strategy
                        all_hospitals.extend(hospitals)
                except Exception as e:
                    st.warning(f"Search failed for term '{search_term}': {e}")
                    continue
            
            # If no hospitals found from API, use fallback
            if not all_hospitals:
                st.info("No hospitals found via SERP API. Using fallback recommendations.")
                return self._get_fallback_hospitals(search_strategy)
            
            # Remove duplicates based on hospital name
            unique_hospitals = self._remove_duplicate_hospitals(all_hospitals)
            
            return unique_hospitals
            
        except Exception as e:
            st.error(f"Error executing hospital search: {e}")
            st.info("Using fallback hospital recommendations.")
            return self._get_fallback_hospitals(search_strategy)
    
    def _get_fallback_hospitals(self, search_strategy: Dict) -> List[Dict]:
        """Provide fallback hospital recommendations when SERP API is unavailable"""
        try:
            conditions = search_strategy.get('primary_conditions', [])
            specialties = search_strategy.get('specialties', [])
            urgency = search_strategy.get('urgency', 'routine')
            
            # Premium hospitals in India with specialties
            fallback_hospitals = []
            
            # Define hospital database with specialties
            hospital_db = [
                {
                    'name': 'All India Institute of Medical Sciences (AIIMS), New Delhi',
                    'description': 'Premier medical institute with comprehensive healthcare services, advanced medical technology, and expert specialists across all medical fields.',
                    'specialties': ['Cardiology', 'Neurology', 'Oncology', 'Orthopedics', 'Emergency Medicine', 'Pulmonology'],
                    'emergency': True,
                    'position': 1,
                    'url': 'https://www.aiims.edu',
                    'premium': True
                },
                {
                    'name': 'Apollo Hospitals, Chennai',
                    'description': 'Leading private healthcare provider with state-of-the-art facilities, internationally trained doctors, and comprehensive medical services.',
                    'specialties': ['Cardiology', 'Oncology', 'Neurology', 'Orthopedics', 'Gastroenterology'],
                    'emergency': True,
                    'position': 2,
                    'url': 'https://www.apollohospitals.com',
                    'premium': True
                },
                {
                    'name': 'Fortis Healthcare',
                    'description': 'Multi-specialty healthcare chain with advanced medical technology, experienced doctors, and patient-centric care across India.',
                    'specialties': ['Cardiology', 'Neurology', 'Orthopedics', 'Emergency Medicine', 'Pulmonology'],
                    'emergency': True,
                    'position': 3,
                    'url': 'https://www.fortishealthcare.com',
                    'premium': True
                },
                {
                    'name': 'Max Healthcare',
                    'description': 'Premium healthcare provider with cutting-edge medical technology, internationally accredited facilities, and expert medical professionals.',
                    'specialties': ['Cardiology', 'Oncology', 'Neurology', 'Orthopedics', 'Gastroenterology'],
                    'emergency': True,
                    'position': 4,
                    'url': 'https://www.maxhealthcare.in',
                    'premium': True
                },
                {
                    'name': 'Medanta - The Medicity, Gurgaon',
                    'description': 'Multi-super specialty hospital with world-class infrastructure, advanced medical equipment, and renowned medical experts.',
                    'specialties': ['Cardiology', 'Neurology', 'Oncology', 'Orthopedics', 'Emergency Medicine'],
                    'emergency': True,
                    'position': 5,
                    'url': 'https://www.medanta.org',
                    'premium': True
                }
            ]
            
            # Score hospitals based on specialty matching
            for hospital in hospital_db:
                score = 50  # Base score for premium hospitals
                
                # Specialty matching
                hospital_specialties = [s.lower() for s in hospital['specialties']]
                for specialty in specialties:
                    if specialty in hospital_specialties or any(specialty in hs for hs in hospital_specialties):
                        score += 15
                
                # Emergency capability for urgent cases
                if urgency == 'urgent' and hospital['emergency']:
                    score += 12
                
                # Premium hospital bonus
                if hospital['premium']:
                    score += 25
                
                hospital['relevance_score'] = score
                hospital['search_context'] = 'Fallback recommendations'
                hospital['search_strategy'] = search_strategy
                
                fallback_hospitals.append(hospital)
            
            # Sort by relevance score
            fallback_hospitals.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return fallback_hospitals
            
        except Exception as e:
            st.error(f"Error generating fallback hospitals: {e}")
            return []
    
    def _remove_duplicate_hospitals(self, hospitals: List[Dict]) -> List[Dict]:
        """Remove duplicate hospitals based on name similarity"""
        unique_hospitals = []
        seen_names = set()
        
        for hospital in hospitals:
            name = hospital.get('name', '').lower().strip()
            
            # Create a normalized name for comparison
            normalized_name = re.sub(r'[^\w\s]', '', name)
            normalized_name = re.sub(r'\s+', ' ', normalized_name).strip()
            
            if normalized_name and normalized_name not in seen_names:
                seen_names.add(normalized_name)
                unique_hospitals.append(hospital)
        
        return unique_hospitals
    
    def _rank_hospitals_by_medical_relevance(self, hospitals: List[Dict], search_strategy: Dict) -> List[Dict]:
        """Rank hospitals based on medical relevance and quality"""
        try:
            for hospital in hospitals:
                score = 0
                name = hospital.get('name', '').lower()
                description = hospital.get('description', '').lower()
                
                # Base score from search position (lower position = higher score)
                position = hospital.get('position', 10)
                score += max(0, 15 - position)
                
                # Premium hospital bonus
                for premium in self.premium_hospitals:
                    if premium in name:
                        score += 25
                        break
                
                # Specialty matching score
                for specialty in search_strategy.get('specialties', []):
                    if specialty in description or specialty in name:
                        score += 15
                
                # Condition keyword matching
                for keyword in search_strategy.get('condition_keywords', []):
                    if keyword in description:
                        score += 8
                
                # Urgency-based scoring
                if search_strategy.get('urgency') == 'urgent':
                    urgent_terms = ['emergency', '24/7', 'trauma', 'critical care', 'icu']
                    for term in urgent_terms:
                        if term in description:
                            score += 12
                
                # Quality indicators
                quality_terms = [
                    'best', 'top', 'leading', 'premier', 'advanced', 'renowned',
                    'excellence', 'award-winning', 'accredited', 'certified'
                ]
                for term in quality_terms:
                    if term in description:
                        score += 5
                
                # Technology and facilities
                tech_terms = [
                    'latest technology', 'state-of-the-art', 'modern equipment',
                    'robotic surgery', 'digital', 'advanced imaging'
                ]
                for term in tech_terms:
                    if term in description:
                        score += 3
                
                hospital['relevance_score'] = score
            
            # Sort by relevance score (highest first)
            ranked_hospitals = sorted(hospitals, key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            return ranked_hospitals
            
        except Exception as e:
            st.warning(f"Error ranking hospitals: {e}")
            return hospitals
    
    def _structure_medical_recommendations(self, hospitals: List[Dict], search_strategy: Dict) -> Dict:
        """Structure hospital recommendations with medical context"""
        recommendations = {
            'top_hospitals': [],
            'search_context': {
                'conditions': search_strategy.get('primary_conditions', []),
                'specialties': search_strategy.get('specialties', []),
                'severity': search_strategy.get('severity', 'moderate'),
                'urgency': search_strategy.get('urgency', 'routine'),
                'search_location': self.location
            },
            'total_found': len(hospitals),
            'recommendation_basis': self._generate_recommendation_basis(search_strategy)
        }
        
        try:
            # Process top hospitals (limit to 5)
            for i, hospital in enumerate(hospitals[:5], 1):
                hospital_info = {
                    'rank': i,
                    'name': hospital.get('name', 'Hospital name not available'),
                    'description': hospital.get('description', 'No description available'),
                    'website': hospital.get('url', None),
                    'relevance_score': hospital.get('relevance_score', 0),
                    'search_context': hospital.get('search_context', 'General search'),
                    'why_recommended': self._generate_recommendation_reason(hospital, search_strategy),
                    'specialties': self._extract_hospital_specialties(hospital.get('description', '')),
                    'emergency_services': self._assess_emergency_services(hospital),
                    'quality_indicators': self._extract_quality_indicators(hospital)
                }
                
                recommendations['top_hospitals'].append(hospital_info)
                
        except Exception as e:
            st.error(f"Error structuring recommendations: {e}")
            recommendations['top_hospitals'] = [{
                'rank': 1,
                'name': 'Error processing hospital information',
                'description': 'Please try again or consult healthcare provider',
                'website': None,
                'relevance_score': 0,
                'search_context': 'Error',
                'why_recommended': 'System error occurred',
                'specialties': ['General Medicine'],
                'emergency_services': False,
                'quality_indicators': []
            }]
        
        return recommendations
    
    def _generate_recommendation_basis(self, search_strategy: Dict) -> str:
        """Generate explanation for recommendation basis"""
        conditions = search_strategy.get('primary_conditions', [])
        specialties = search_strategy.get('specialties', [])
        severity = search_strategy.get('severity', 'moderate')
        urgency = search_strategy.get('urgency', 'routine')
        
        basis_parts = []
        
        if conditions:
            basis_parts.append(f"Based on conditions: {', '.join(conditions[:2])}")
        
        if specialties and 'general' not in specialties:
            basis_parts.append(f"Requiring specialties: {', '.join(specialties)}")
        
        if urgency == 'urgent':
            basis_parts.append("Prioritizing emergency-capable hospitals")
        elif severity == 'severe':
            basis_parts.append("Focusing on top-tier medical centers")
        
        return "; ".join(basis_parts) if basis_parts else "General hospital recommendations"
    
    def _generate_recommendation_reason(self, hospital: Dict, search_strategy: Dict) -> str:
        """Generate specific reason why this hospital is recommended"""
        reasons = []
        
        name = hospital.get('name', '').lower()
        description = hospital.get('description', '').lower()
        score = hospital.get('relevance_score', 0)
        
        # Premium hospital
        for premium in self.premium_hospitals:
            if premium in name:
                reasons.append(f"Premier healthcare institution")
                break
        
        # Specialty match
        for specialty in search_strategy.get('specialties', []):
            if specialty in description or specialty in name:
                reasons.append(f"Specialized in {specialty}")
                break
        
        # High relevance score
        if score > 50:
            reasons.append("High relevance match for your conditions")
        elif score > 30:
            reasons.append("Good match for your medical needs")
        
        # Emergency capability
        if search_strategy.get('urgency') == 'urgent':
            if any(term in description for term in ['emergency', '24/7', 'trauma']):
                reasons.append("Emergency services available")
        
        return "; ".join(reasons) if reasons else "Quality healthcare provider"
    
    def _extract_hospital_specialties(self, description: str) -> List[str]:
        """Extract medical specialties from hospital description"""
        specialties = []
        description_lower = description.lower()
        
        specialty_terms = {
            'Cardiology': ['cardiology', 'heart', 'cardiac'],
            'Orthopedics': ['orthopedics', 'bone', 'joint', 'spine'],
            'Neurology': ['neurology', 'brain', 'neuro'],
            'Oncology': ['oncology', 'cancer', 'tumor'],
            'Pediatrics': ['pediatric', 'children'],
            'Emergency Medicine': ['emergency', 'trauma', 'critical care'],
            'Gastroenterology': ['gastroenterology', 'digestive'],
            'Pulmonology': ['pulmonology', 'respiratory', 'lung']
        }
        
        for specialty, keywords in specialty_terms.items():
            if any(keyword in description_lower for keyword in keywords):
                specialties.append(specialty)
        
        return specialties if specialties else ['General Medicine']
    
    def _assess_emergency_services(self, hospital: Dict) -> bool:
        """Assess if hospital has emergency services"""
        description = hospital.get('description', '').lower()
        name = hospital.get('name', '').lower()
        
        emergency_indicators = [
            'emergency', '24/7', 'trauma', 'critical care', 'icu',
            'round the clock', 'emergency department'
        ]
        
        return any(indicator in description or indicator in name for indicator in emergency_indicators)
    
    def _extract_quality_indicators(self, hospital: Dict) -> List[str]:
        """Extract quality indicators from hospital information"""
        indicators = []
        description = hospital.get('description', '').lower()
        
        quality_terms = {
            'Accredited': ['accredited', 'certified', 'iso certified'],
            'Award Winning': ['award', 'winner', 'recognition'],
            'Advanced Technology': ['advanced', 'state-of-the-art', 'modern equipment'],
            'Experienced Staff': ['experienced', 'expert', 'specialist'],
            'Research Center': ['research', 'clinical trials', 'innovation']
        }
        
        for indicator, keywords in quality_terms.items():
            if any(keyword in description for keyword in keywords):
                indicators.append(indicator)
        
        return indicators 