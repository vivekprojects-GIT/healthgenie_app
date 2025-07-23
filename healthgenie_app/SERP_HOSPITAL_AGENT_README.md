# Intelligent SERP Hospital Agent

## 🏥 **Overview**
The `SerpHospitalAgent` is an advanced hospital recommendation system that uses SERP API to intelligently find the best hospitals based on patient medical conditions. Unlike basic hospital search, this agent analyzes medical context, determines required specialties, assesses urgency, and ranks hospitals by medical relevance.

## 🧠 **Key Features**

### 1. **Medical Condition Analysis**
- Extracts conditions from X-ray analysis, medical reports, and clinical impressions
- Processes and cleans medical terminology
- Identifies severity levels (mild, moderate, severe, critical)
- Determines urgency (routine, urgent)

### 2. **Specialty Mapping**
- Maps conditions to required medical specialties:
  - **Cardiac**: cardiology, heart, cardiovascular
  - **Pulmonary**: pulmonology, lung, respiratory
  - **Orthopedic**: orthopedics, bone, joint, spine
  - **Neurological**: neurology, brain, stroke
  - **Oncology**: cancer, tumor, chemotherapy
  - **Emergency**: trauma, critical care
  - And more...

### 3. **Intelligent Search Strategy**
- Generates multiple targeted search queries
- Condition-specific searches: "best hospitals for [condition]"
- Specialty-specific searches: "top cardiology hospitals"
- Emergency searches: "24/7 emergency care centers"
- Premium hospital searches: "AIIMS Apollo Fortis"

### 4. **Advanced Hospital Ranking**
Hospitals are scored based on:
- **Search position** (lower = better)
- **Premium hospital status** (+25 points for AIIMS, Apollo, etc.)
- **Specialty matching** (+15 points per specialty match)
- **Condition keyword matching** (+8 points per keyword)
- **Emergency capabilities** (+12 points for urgent cases)
- **Quality indicators** (+5 points for "best", "top", "leading")
- **Technology features** (+3 points for "state-of-the-art")

### 5. **Enhanced Hospital Information**
Each recommendation includes:
- **Relevance score** - How well it matches patient needs
- **Why recommended** - Specific reasons for recommendation
- **Medical specialties** - Available specialties
- **Emergency services** - 24/7 emergency capability
- **Quality indicators** - Accreditation, awards, technology
- **Search context** - Which search query found this hospital

## 🔧 **Technical Implementation**

### Class Structure
```python
class SerpHospitalAgent:
    def __init__(self):
        # Initialize SERP tool and medical knowledge bases
        
    def find_best_hospitals(self, medical_analysis: Dict) -> Dict:
        # Main method to find best hospitals
        
    def _analyze_medical_conditions(self, medical_analysis: Dict) -> Dict:
        # Analyze medical conditions and create search strategy
        
    def _execute_intelligent_search(self, search_strategy: Dict) -> List[Dict]:
        # Execute multiple targeted searches
        
    def _rank_hospitals_by_medical_relevance(self, hospitals: List[Dict], search_strategy: Dict) -> List[Dict]:
        # Rank hospitals based on medical relevance
```

### Key Methods

#### `find_best_hospitals(medical_analysis)`
Main entry point that:
1. Analyzes medical conditions
2. Executes intelligent search
3. Ranks hospitals by relevance
4. Structures recommendations

#### `_analyze_medical_conditions(medical_analysis)`
Processes medical data to determine:
- Primary conditions
- Required specialties  
- Severity and urgency levels
- Intelligent search terms

#### `_rank_hospitals_by_medical_relevance(hospitals, search_strategy)`
Sophisticated ranking algorithm considering:
- Medical specialty matching
- Condition-specific relevance
- Hospital quality and reputation
- Emergency capabilities

## 📊 **Data Flow**

```
Medical Analysis Input
         ↓
Condition Analysis & Processing
         ↓
Specialty Identification
         ↓
Search Strategy Generation
         ↓
Multiple SERP API Searches
         ↓
Hospital Ranking & Scoring
         ↓
Enhanced Recommendations Output
```

## 🎯 **Example Usage**

```python
from agents.serp_hospital_agent import SerpHospitalAgent

# Initialize agent
hospital_agent = SerpHospitalAgent()

# Medical analysis from combined X-ray and report
medical_analysis = {
    'clinical_impression': {
        'primary_findings': ['chest pain', 'cardiac abnormality'],
        'severity': 'moderate'
    },
    'findings': ['elevated cardiac enzymes'],
    'diagnoses': ['possible myocardial infarction']
}

# Find best hospitals
recommendations = hospital_agent.find_best_hospitals(medical_analysis)

# Results include:
# - Top 5 ranked hospitals
# - Medical context and search strategy
# - Detailed hospital information
# - Recommendation explanations
```

## 📋 **Output Structure**

```python
{
    'top_hospitals': [
        {
            'rank': 1,
            'name': 'AIIMS New Delhi',
            'description': 'Premier medical institute...',
            'relevance_score': 85,
            'why_recommended': 'Premier healthcare institution; Specialized in cardiac',
            'specialties': ['Cardiology', 'Emergency Medicine'],
            'emergency_services': True,
            'quality_indicators': ['Accredited', 'Advanced Technology'],
            'website': 'https://...'
        }
    ],
    'search_context': {
        'conditions': ['chest pain', 'cardiac abnormality'],
        'specialties': ['cardiac'],
        'severity': 'moderate',
        'urgency': 'routine',
        'search_location': 'India'
    },
    'total_found': 15,
    'recommendation_basis': 'Based on conditions: chest pain, cardiac abnormality; Requiring specialties: cardiac'
}
```

## 🚀 **Advantages Over Basic Search**

### Basic Hospital Agent:
- Simple keyword search
- Basic ranking by position
- Limited medical context
- Generic recommendations

### Intelligent SERP Hospital Agent:
- ✅ **Medical condition analysis**
- ✅ **Specialty-specific search**
- ✅ **Severity-based prioritization**
- ✅ **Multi-factor ranking algorithm**
- ✅ **Premium hospital recognition**
- ✅ **Emergency capability assessment**
- ✅ **Detailed recommendation explanations**
- ✅ **Quality indicator extraction**

## 🔍 **Search Strategy Examples**

### For Cardiac Conditions:
- "best cardiology hospitals India"
- "top cardiac specialists India"
- "AIIMS Apollo Fortis cardiac care India"
- "best hospitals for heart disease India"

### For Emergency Cases:
- "best emergency hospitals India"
- "top trauma centers India"
- "24/7 emergency care India"

### For Cancer Cases:
- "best oncology hospitals India"
- "top cancer treatment centers India"
- "Tata Memorial cancer specialists India"

## 📈 **Performance Features**

- **Duplicate removal** - Eliminates duplicate hospitals
- **API optimization** - Limits to 6 search queries max
- **Error handling** - Graceful fallbacks for failed searches
- **Caching-ready** - Structured for future caching implementation
- **Scalable** - Easy to add new specialties and conditions

## 🎛️ **Configuration**

The agent uses configuration from `config.py`:
- `SEARCH_LOCATION` - Default search location
- `SERP_API_KEY` - SERP API credentials
- Premium hospital lists can be customized

## 🔧 **Integration**

The agent integrates with:
- **HealthcareController** - Main orchestration
- **SerpSearchTool** - SERP API interface
- **Streamlit UI** - Enhanced display components

## 📱 **UI Enhancements**

The new agent provides rich UI components:
- **Medical context display** - Shows conditions, specialties, severity
- **Hospital ranking scores** - Visual relevance indicators
- **Recommendation explanations** - Why each hospital is suggested
- **Quality indicators** - Accreditation, technology, awards
- **Emergency service flags** - Clear emergency capability indicators

This intelligent approach ensures patients get the most relevant hospital recommendations based on their specific medical needs rather than generic search results. 