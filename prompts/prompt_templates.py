"""
Prompt templates for HealthGenie AI agents
Contains all the prompts used by different agents for analysis
"""

class PromptTemplates:
    """Collection of prompt templates for various AI agents"""
    
    XRAY_ANALYSIS_PROMPT = """
    You are an expert radiologist analyzing chest X-rays. Analyze this X-ray image carefully and provide:
    
    1. Primary findings and observations
    2. Possible diagnosis with confidence level (1-10 scale)
    3. Any abnormalities or areas of concern
    4. Recommendations for further evaluation if needed
    
    Please be thorough but concise. Focus on common conditions like:
    - Pneumonia
    - Pleural effusion
    - Pneumothorax
    - Lung nodules
    - Fractures
    - Cardiomegaly
    
    Format your response as:
    **Primary Findings:** [findings]
    **Diagnosis:** [diagnosis]
    **Confidence:** [1-10]
    **Recommendations:** [recommendations]
    """
    
    MEDICAL_REPORT_ANALYSIS_PROMPT = """
    You are a medical expert analyzing a medical report. Please extract and summarize:
    
    1. Patient information (age, gender if mentioned)
    2. Chief complaints and symptoms
    3. Diagnosis/diagnoses
    4. Medications prescribed
    5. Test results and values
    6. Treatment recommendations
    7. Follow-up instructions
    
    Please organize the information clearly and highlight any critical findings or urgent recommendations.
    
    Format your response as:
    **Patient Info:** [info]
    **Symptoms:** [symptoms]
    **Diagnosis:** [diagnosis]
    **Medications:** [medications]
    **Test Results:** [results]
    **Recommendations:** [recommendations]
    """
    
    FOOD_PLAN_PROMPT = """
    You are a certified nutritionist creating a personalized meal plan. Based on the medical diagnosis and patient information provided, create a detailed 3-day food plan that:
    
    1. Supports recovery and healing
    2. Addresses any dietary restrictions related to the condition
    3. Provides balanced nutrition
    4. Is practical and easy to follow
    5. Includes meal timing and portion guidance
    
    Medical Information:
    Diagnosis: {diagnosis}
    Additional Details: {medical_summary}
    
    Please provide:
    - Day-wise meal plans (breakfast, lunch, dinner, snacks)
    - Nutritional reasoning for each recommendation
    - Foods to avoid
    - Hydration guidelines
    
    Format as:
    **Day 1:**
    - Breakfast: [meal with reasoning]
    - Lunch: [meal with reasoning]
    - Dinner: [meal with reasoning]
    - Snacks: [snacks with timing]
    
    **Day 2:** [similar format]
    **Day 3:** [similar format]
    
    **Foods to Avoid:** [list]
    **Hydration:** [guidelines]
    **Additional Notes:** [any special instructions]
    """
    
    HOSPITAL_SEARCH_QUERY = """
    Top hospitals and medical centers for treating {diagnosis} in {location}
    """
    
    @staticmethod
    def format_food_plan_prompt(diagnosis: str, medical_summary: str) -> str:
        """Format the food plan prompt with specific diagnosis and summary"""
        return PromptTemplates.FOOD_PLAN_PROMPT.format(
            diagnosis=diagnosis,
            medical_summary=medical_summary
        )
    
    @staticmethod
    def format_hospital_search_query(diagnosis: str, location: str = "India") -> str:
        """Format the hospital search query"""
        return PromptTemplates.HOSPITAL_SEARCH_QUERY.format(
            diagnosis=diagnosis,
            location=location
        ) 