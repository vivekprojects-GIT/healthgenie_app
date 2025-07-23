"""
Food Plan Agent using Gemini API
Creates personalized 3-day meal plans based on medical diagnosis and reports
"""
import google.generativeai as genai
from typing import Optional, Dict, List
import streamlit as st
from config import config

class FoodPlanAgent:
    """Agent for creating personalized food plans using Gemini API"""
    
    def __init__(self):
        """Initialize the food plan agent with Gemini configuration"""
        try:
            genai.configure(api_key=config.GOOGLE_AI_API_KEY)
            self.model = genai.GenerativeModel(config.MODEL_NAME)
            self.meal_plan_prompt = """
            As a clinical nutritionist, analyze the medical report findings and create a personalized 3-day meal plan. 
            Consider the following aspects:

            1. Medical Context:
            - Primary diagnosis and conditions
            - Any dietary restrictions or allergies
            - Medications that may interact with foods

            2. Nutritional Requirements:
            - Macro and micronutrient needs
            - Specific nutrients to increase/avoid
            - Caloric requirements

            3. Create a detailed 3-day meal plan with:
            - Breakfast, lunch, dinner, and 2 snacks
            - Portion sizes and preparation methods
            - Alternative options for each meal
            - Timing recommendations

            4. Additional Guidelines:
            - Foods that help manage the condition
            - Foods to avoid
            - Hydration recommendations
            - Supplement suggestions (if needed)

            Format the response as a structured meal plan with clear sections and bullet points.
            Include scientific reasoning for key recommendations.
            """
        except Exception as e:
            st.error(f"Failed to initialize Food Plan Agent: {e}")
            self.model = None
    
    def generate_meal_plan(self, medical_report: Dict) -> Optional[Dict]:
        """
        Generate personalized meal plan based on medical analysis
        
        Args:
            medical_report: Dictionary containing medical analysis results
            
        Returns:
            Dictionary containing structured meal plan or None if failed
        """
        if not self.model or not medical_report:
            return None
            
        try:
            # Extract relevant medical information
            medical_context = self._extract_medical_context(medical_report)
            
            # Generate meal plan
            prompt = self._format_meal_plan_prompt(medical_context)
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                st.error("No meal plan generated")
                return None
            
            # Structure the meal plan
            meal_plan = self._structure_meal_plan(response.text)
            return meal_plan
                
        except Exception as e:
            st.error(f"Error creating meal plan: {e}")
            return None
            
    def _extract_medical_context(self, medical_report: Dict) -> Dict:
        """Extract relevant medical information for meal planning"""
        context = {
            'conditions': [],
            'restrictions': [],
            'medications': [],
            'allergies': []
        }
        
        try:
            # Extract from clinical impression
            if 'clinical_impression' in medical_report:
                findings = medical_report['clinical_impression'].get('primary_findings', [])
                context['conditions'].extend(findings)
            
            # Extract from recommendations
            if 'recommendations' in medical_report:
                for rec in medical_report.get('recommendations', []):
                    if 'diet' in rec.lower() or 'food' in rec.lower():
                        context['restrictions'].append(rec)
            
            # Ensure we have at least basic context
            if not any(context.values()):
                context['conditions'] = ['General health maintenance']
                
        except Exception as e:
            st.warning(f"Error extracting medical context: {e}")
            context['conditions'] = ['General health maintenance']
            
        return context
        
    def _format_meal_plan_prompt(self, medical_context: Dict) -> str:
        """Format the meal plan prompt with medical context"""
        conditions = '\n'.join(f"- {c}" for c in medical_context['conditions'])
        restrictions = '\n'.join(f"- {r}" for r in medical_context['restrictions'])
        
        prompt = f"""
        {self.meal_plan_prompt}

        Medical Conditions:
        {conditions}

        Dietary Restrictions:
        {restrictions or '- None specified'}
        """
        return prompt
        
    def _structure_meal_plan(self, response_text: str) -> Dict:
        """Structure the meal plan response into organized sections"""
        meal_plan = {
            'nutritional_requirements': {
                'macros': [],
                'micros': [],
                'calories': None
            },
            'daily_plans': {
                'day1': {'breakfast': [], 'lunch': [], 'dinner': [], 'snacks': []},
                'day2': {'breakfast': [], 'lunch': [], 'dinner': [], 'snacks': []},
                'day3': {'breakfast': [], 'lunch': [], 'dinner': [], 'snacks': []}
            },
            'guidelines': {
                'recommended_foods': [],
                'foods_to_avoid': [],
                'hydration': None,
                'supplements': []
            }
        }
        
        try:
            current_section = None
            current_day = None
            current_meal = None
            
            for line in response_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Identify sections
                lower_line = line.lower()
                if 'day' in lower_line and ':' in line:
                    current_day = f"day{line[3]}" if line[3].isdigit() else None
                    continue
                elif any(meal in lower_line for meal in ['breakfast', 'lunch', 'dinner', 'snacks']):
                    for meal in ['breakfast', 'lunch', 'dinner', 'snacks']:
                        if meal in lower_line:
                            current_meal = meal
                            break
                    continue
                elif 'nutritional requirements' in lower_line:
                    current_section = 'nutritional_requirements'
                    current_day = None
                    current_meal = None
                    continue
                elif 'guidelines' in lower_line:
                    current_section = 'guidelines'
                    current_day = None
                    current_meal = None
                    continue
                
                # Process content
                if line.startswith(('-', '*', '•')):
                    clean_line = line.lstrip('-*• ').strip()
                    if current_day and current_meal:
                        meal_plan['daily_plans'][current_day][current_meal].append(clean_line)
                    elif current_section == 'nutritional_requirements':
                        if 'calorie' in lower_line:
                            meal_plan['nutritional_requirements']['calories'] = clean_line
                        elif 'protein' in lower_line or 'fat' in lower_line or 'carb' in lower_line:
                            meal_plan['nutritional_requirements']['macros'].append(clean_line)
                        else:
                            meal_plan['nutritional_requirements']['micros'].append(clean_line)
                    elif current_section == 'guidelines':
                        if 'avoid' in lower_line:
                            meal_plan['guidelines']['foods_to_avoid'].append(clean_line)
                        elif 'hydration' in lower_line or 'water' in lower_line:
                            meal_plan['guidelines']['hydration'] = clean_line
                        elif 'supplement' in lower_line:
                            meal_plan['guidelines']['supplements'].append(clean_line)
                        else:
                            meal_plan['guidelines']['recommended_foods'].append(clean_line)
            
            # Ensure all sections have content
            for day in meal_plan['daily_plans']:
                for meal in meal_plan['daily_plans'][day]:
                    if not meal_plan['daily_plans'][day][meal]:
                        meal_plan['daily_plans'][day][meal] = ['Meal details to be customized']
            
            if not meal_plan['nutritional_requirements']['calories']:
                meal_plan['nutritional_requirements']['calories'] = 'To be determined based on individual factors'
            
            if not meal_plan['guidelines']['hydration']:
                meal_plan['guidelines']['hydration'] = 'Maintain adequate hydration throughout the day'
                
            return meal_plan
            
        except Exception as e:
            st.error(f"Error structuring meal plan: {e}")
            return {
                'nutritional_requirements': {
                    'general': ['Please consult a nutritionist for personalized requirements']
                },
                'daily_plans': {
                    'general': ['Unable to generate detailed meal plan']
                },
                'guidelines': {
                    'general': ['Consult healthcare provider for dietary guidelines']
                }
            } 