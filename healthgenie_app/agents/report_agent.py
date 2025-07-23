"""
Medical Report Analysis Agent using Gemini Vision API
Analyzes medical reports and extracts key information
"""
import google.generativeai as genai
from typing import Optional, Dict
import streamlit as st
from config import config

class ReportAgent:
    """Agent for analyzing medical reports using Gemini Vision API"""
    
    def __init__(self):
        """Initialize the report agent with Gemini configuration"""
        try:
            genai.configure(api_key=config.GOOGLE_AI_API_KEY)
            self.model = genai.GenerativeModel(config.MODEL_NAME)
            self.prompt = """
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
        except Exception as e:
            st.error(f"Failed to initialize Report Agent: {e}")
            self.model = None
    
    def analyze_report(self, image_bytes: bytes) -> Optional[Dict]:
        """
        Analyze medical report image and extract key information
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Dictionary containing extracted information or None if failed
        """
        if not self.model:
            return None
            
        try:
            # Prepare image for Gemini
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_bytes
            }
            
            # Generate content with image and prompt
            response = self.model.generate_content([self.prompt, image_part])
            
            if not response or not response.text:
                st.error("No response received from the model")
                return None
            
            # Structure the analysis
            analysis_results = self._structure_report_analysis(response.text)
            
            return analysis_results
                
        except Exception as e:
            st.error(f"Error analyzing medical report: {e}")
            return None
            
    def _structure_report_analysis(self, text: str) -> Dict:
        """Structure the report analysis into organized sections"""
        analysis = {
            'findings': [],
            'diagnoses': [],
            'medications': [],
            'test_results': [],
            'patient_info': None,
            'symptoms': [],
            'recommendations': []
        }
        
        try:
            current_section = None
            
            for line in text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Identify sections
                lower_line = line.lower()
                if 'patient info' in lower_line:
                    current_section = 'patient_info'
                    content = line.split(':', 1)[1].strip() if ':' in line else ''
                    if content:
                        analysis['patient_info'] = content
                    continue
                elif 'symptoms' in lower_line:
                    current_section = 'symptoms'
                    continue
                elif 'diagnosis' in lower_line:
                    current_section = 'diagnoses'
                    continue
                elif 'medications' in lower_line:
                    current_section = 'medications'
                    continue
                elif 'test results' in lower_line:
                    current_section = 'test_results'
                    continue
                elif 'recommendations' in lower_line:
                    current_section = 'recommendations'
                    continue
                
                # Process content based on section
                if current_section and line.startswith(('-', '*', '•')):
                    clean_line = line.lstrip('-*• ').strip()
                    if current_section in ['symptoms', 'diagnoses', 'medications', 'test_results', 'recommendations']:
                        analysis[current_section].append(clean_line)
                elif current_section and not line.startswith('**'):
                    # Continue content from previous line
                    if current_section in ['symptoms', 'diagnoses', 'medications', 'test_results', 'recommendations']:
                        analysis[current_section].append(line)
            
            # Add to findings for compatibility
            analysis['findings'] = analysis['symptoms'] + analysis['diagnoses']
            
            # Ensure we have some content
            if not any(analysis[key] for key in ['findings', 'diagnoses', 'symptoms']):
                analysis['findings'] = ['Medical report processed - see full analysis']
                
            return analysis
            
        except Exception as e:
            st.error(f"Error structuring report analysis: {e}")
            return {
                'findings': ['Error processing medical report'],
                'diagnoses': [],
                'medications': [],
                'test_results': [],
                'patient_info': 'Error processing patient information',
                'symptoms': [],
                'recommendations': ['Please consult with healthcare provider']
            }
    
    def extract_text_from_report(self, image_bytes: bytes) -> Optional[str]:
        """
        Extract raw text from medical report using OCR
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Extracted text or None if failed
        """
        if not self.model:
            return None
            
        try:
            ocr_prompt = """
            Please extract all visible text from this medical report image.
            Preserve the structure and formatting as much as possible.
            Include all patient information, test results, diagnoses, and recommendations.
            """
            
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_bytes
            }
            
            response = self.model.generate_content([ocr_prompt, image_part])
            
            if response and response.text:
                return response.text
            else:
                return None
                
        except Exception as e:
            st.error(f"Error extracting text from report: {e}")
            return None
    
    def identify_critical_findings(self, medical_data: Dict) -> Dict:
        """
        Identify critical or urgent findings from medical data
        
        Args:
            medical_data: Parsed medical report data
            
        Returns:
            Dictionary with critical findings analysis
        """
        try:
            critical_keywords = [
                "urgent", "emergency", "critical", "severe", "acute",
                "immediate", "hospitalization", "surgery", "tumor",
                "cancer", "malignant", "high risk", "abnormal"
            ]
            
            critical_findings = {
                "has_critical": False,
                "critical_items": [],
                "urgency_level": "low",
                "recommendations": []
            }
            
            # Check all fields for critical keywords
            text_to_check = f"{medical_data.get('diagnosis', '')} {medical_data.get('symptoms', '')} {medical_data.get('test_results', '')} {medical_data.get('recommendations', '')}"
            text_lower = text_to_check.lower()
            
            for keyword in critical_keywords:
                if keyword in text_lower:
                    critical_findings["has_critical"] = True
                    critical_findings["critical_items"].append(keyword)
            
            # Determine urgency level
            if any(word in text_lower for word in ["urgent", "emergency", "critical", "immediate"]):
                critical_findings["urgency_level"] = "high"
            elif any(word in text_lower for word in ["severe", "acute", "abnormal"]):
                critical_findings["urgency_level"] = "medium"
            
            # Add recommendations based on findings
            if critical_findings["has_critical"]:
                critical_findings["recommendations"].append("Consult with healthcare provider immediately")
                if critical_findings["urgency_level"] == "high":
                    critical_findings["recommendations"].append("Seek emergency medical attention")
            
            return critical_findings
            
        except Exception as e:
            st.error(f"Error identifying critical findings: {e}")
            return {"has_critical": False, "critical_items": [], "urgency_level": "low", "recommendations": []}
    
    def get_summary(self, medical_data: Dict) -> str:
        """
        Generate a concise summary of the medical report
        
        Args:
            medical_data: Parsed medical report data
            
        Returns:
            Summary string
        """
        try:
            diagnosis = medical_data.get('diagnosis', 'Not specified')
            symptoms = medical_data.get('symptoms', 'Not specified')
            medications = medical_data.get('medications', 'Not specified')
            
            summary = f"Diagnosis: {diagnosis}\n"
            if symptoms != 'Not specified':
                summary += f"Symptoms: {symptoms}\n"
            if medications != 'Not specified':
                summary += f"Medications: {medications}"
            
            return summary.strip()
            
        except Exception:
            return "Unable to generate summary from medical report" 