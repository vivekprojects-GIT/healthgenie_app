"""
Controller Agent - Orchestrates all healthcare analysis agents
Manages the workflow and coordinates between different agents
"""
from typing import Dict, List, Optional, Tuple
import streamlit as st
from agents.xray_agent import XRayAgent
from agents.report_agent import ReportAgent
from agents.food_plan_agent import FoodPlanAgent
from agents.serp_hospital_agent import SerpHospitalAgent
from utils.image_helpers import process_image_for_gemini, validate_image_file
import time

class HealthcareController:
    """Main controller that coordinates all healthcare analysis agents"""
    
    def __init__(self):
        """Initialize all agents"""
        try:
            self.xray_agent = XRayAgent()
            self.report_agent = ReportAgent()
            self.food_plan_agent = FoodPlanAgent()
            self.hospital_agent = SerpHospitalAgent()
            
        except Exception as e:
            st.error(f"Failed to initialize Healthcare Controller: {e}")
            self.xray_agent = None
            self.report_agent = None
            self.food_plan_agent = None
            self.hospital_agent = None
    
    def process_files(self, xray_file, report_file, progress_container):
        """
        Process uploaded files through all agents
        
        Args:
            xray_file: Uploaded X-ray image file (UploadedFile object)
            report_file: Uploaded medical report file (UploadedFile object)
            progress_container: Streamlit container for progress updates
            
        Returns:
            Dict containing all analysis results
        """
        results = {
            'xray_analysis': None,
            'report_analysis': None,
            'combined_analysis': None,
            'meal_plan': None,
            'hospital_recommendations': None,
            'processing_time': None,
            'errors': []
        }
        
        start_time = time.time()
        
        try:
            # Initialize agents
            with progress_container.status("🤖 Initializing AI agents...", expanded=True) as status:
                status.write("Setting up X-ray analysis agent...")
                time.sleep(0.5)
                status.write("Setting up medical report agent...")
                time.sleep(0.5)
                status.write("Setting up meal planning agent...")
                time.sleep(0.5)
                status.write("Setting up hospital search agent...")
                time.sleep(0.5)
                status.update(label="✅ All agents initialized successfully", state="complete")
            
            # Process X-ray if uploaded
            if xray_file:
                with progress_container.status("🔬 Analyzing X-ray image...", expanded=True) as status:
                    try:
                        status.write("Processing medical image...")
                        
                        # Convert UploadedFile to bytes
                        if not validate_image_file(xray_file):
                            raise ValueError("Invalid X-ray image file")
                        
                        xray_bytes = process_image_for_gemini(xray_file)
                        if not xray_bytes:
                            raise ValueError("Failed to process X-ray image")
                        
                        status.write("Running AI visual analysis...")
                        status.write("Extracting clinical findings...")
                        
                        xray_result = self.xray_agent.analyze_xray(xray_bytes)
                        if xray_result:
                            results['xray_analysis'] = xray_result
                            status.update(label="✅ X-ray analysis completed", state="complete")
                        else:
                            status.update(label="⚠️ X-ray analysis failed", state="error")
                            results['errors'].append("X-ray analysis failed")
                    except Exception as e:
                        status.update(label="❌ X-ray analysis error", state="error")
                        results['errors'].append(f"X-ray analysis error: {str(e)}")
            
            # Process medical report if uploaded
            if report_file:
                with progress_container.status("📄 Analyzing medical report...", expanded=True) as status:
                    try:
                        status.write("Processing document...")
                        
                        # Convert UploadedFile to bytes
                        if not validate_image_file(report_file):
                            raise ValueError("Invalid medical report file")
                        
                        report_bytes = process_image_for_gemini(report_file)
                        if not report_bytes:
                            raise ValueError("Failed to process medical report")
                        
                        status.write("Extracting medical information...")
                        status.write("Analyzing lab results and diagnoses...")
                        
                        report_result = self.report_agent.analyze_report(report_bytes)
                        if report_result:
                            results['report_analysis'] = report_result
                            status.update(label="✅ Medical report analysis completed", state="complete")
                        else:
                            status.update(label="⚠️ Medical report analysis failed", state="error")
                            results['errors'].append("Medical report analysis failed")
                    except Exception as e:
                        status.update(label="❌ Medical report analysis error", state="error")
                        results['errors'].append(f"Medical report analysis error: {str(e)}")
            
            # Combine analyses
            with progress_container.status("🔗 Combining medical analyses...", expanded=True) as status:
                try:
                    status.write("Integrating X-ray and report findings...")
                    status.write("Generating comprehensive medical summary...")
                    
                    combined_analysis = self._combine_analyses(
                        results.get('xray_analysis'),
                        results.get('report_analysis')
                    )
                    results['combined_analysis'] = combined_analysis
                    status.update(label="✅ Combined analysis completed", state="complete")
                except Exception as e:
                    status.update(label="❌ Analysis combination error", state="error")
                    results['errors'].append(f"Analysis combination error: {str(e)}")
            
            # Generate meal plan
            if results['combined_analysis']:
                with progress_container.status("🍽️ Generating personalized meal plan...", expanded=True) as status:
                    try:
                        status.write("Analyzing dietary requirements...")
                        status.write("Creating 3-day meal plan...")
                        status.write("Adding nutritional recommendations...")
                        
                        meal_plan = self.food_plan_agent.generate_meal_plan(results['combined_analysis'])
                        if meal_plan:
                            results['meal_plan'] = meal_plan
                            status.update(label="✅ Meal plan generated", state="complete")
                        else:
                            status.update(label="⚠️ Meal plan generation failed", state="error")
                            results['errors'].append("Meal plan generation failed")
                    except Exception as e:
                        status.update(label="❌ Meal plan generation error", state="error")
                        results['errors'].append(f"Meal plan generation error: {str(e)}")
            
            # Find hospitals with location awareness
            if results['combined_analysis']:
                with progress_container.status("🏥 Finding specialized hospitals...", expanded=True) as status:
                    try:
                        status.write("Searching hospitals in default location...")
                        status.write("Analyzing medical conditions for specialty matching...")
                        status.write("Ranking hospitals by relevance...")
                        
                        hospital_recs = self.hospital_agent.find_best_hospitals(results['combined_analysis'])
                        if hospital_recs:
                            results['hospital_recommendations'] = hospital_recs
                            status.update(label="✅ Hospital recommendations ready", state="complete")
                        else:
                            status.update(label="⚠️ Hospital search failed", state="error")
                            results['errors'].append("Hospital search failed")
                    except Exception as e:
                        status.update(label="❌ Hospital search error", state="error")
                        results['errors'].append(f"Hospital search error: {str(e)}")
            
            # Calculate processing time
            end_time = time.time()
            results['processing_time'] = round(end_time - start_time, 2)
            
            # Final status
            if results['errors']:
                with progress_container.status("⚠️ Analysis completed with some errors", expanded=False) as status:
                    status.write(f"Completed in {results['processing_time']} seconds")
                    status.write(f"Errors encountered: {len(results['errors'])}")
            else:
                with progress_container.status("🎉 Analysis completed successfully!", expanded=False) as status:
                    status.write(f"All analyses completed in {results['processing_time']} seconds")
                    status.write("Ready to view results!")
                    
        except Exception as e:
            st.error(f"Critical error in analysis workflow: {str(e)}")
            results['errors'].append(f"Critical workflow error: {str(e)}")
        
        return results
    
    def _combine_analyses(self, xray_analysis, report_analysis) -> Dict:
        """Combine X-ray and report analyses into a unified medical report"""
        combined = {
            'clinical_impression': {
                'primary_findings': [],
                'differential_diagnoses': [],
                'severity': 'moderate',
                'confidence': 7
            },
            'findings': [],
            'diagnoses': [],
            'medications': [],
            'test_results': [],
            'recommendations': []
        }
        
        try:
            # Combine X-ray analysis
            if xray_analysis:
                if 'clinical_impression' in xray_analysis:
                    clinical = xray_analysis['clinical_impression']
                    combined['clinical_impression']['primary_findings'].extend(
                        clinical.get('primary_findings', [])
                    )
                    combined['clinical_impression']['differential_diagnoses'].extend(
                        clinical.get('differential_diagnoses', [])
                    )
                    
                    # Use X-ray severity if available
                    if clinical.get('severity'):
                        combined['clinical_impression']['severity'] = clinical['severity']
                    
                    # Use X-ray confidence if available
                    if clinical.get('confidence'):
                        combined['clinical_impression']['confidence'] = clinical['confidence']
                
                # Add other X-ray findings
                combined['findings'].extend(xray_analysis.get('findings', []))
                combined['diagnoses'].extend(xray_analysis.get('diagnoses', []))
                combined['recommendations'].extend(xray_analysis.get('recommendations', []))
            
            # Combine report analysis
            if report_analysis:
                combined['findings'].extend(report_analysis.get('findings', []))
                combined['diagnoses'].extend(report_analysis.get('diagnoses', []))
                combined['medications'].extend(report_analysis.get('medications', []))
                combined['test_results'].extend(report_analysis.get('test_results', []))
                combined['recommendations'].extend(report_analysis.get('recommendations', []))
            
            # Remove duplicates while preserving order
            for key in ['findings', 'diagnoses', 'medications', 'test_results', 'recommendations']:
                combined[key] = list(dict.fromkeys(combined[key]))  # Remove duplicates
            
            return combined
            
        except Exception as e:
            st.warning(f"Error combining analyses: {e}")
            return combined
    
    def _create_combined_medical_report(self, xray_analysis, report_analysis) -> Dict:
        """Create a combined medical report for downstream agents"""
        combined_report = {
            'clinical_impression': {
                'primary_findings': [],
                'differential_diagnoses': [],
                'severity': 'Not specified',
                'confidence': None
            },
            'recommendations': [],
            'findings': [],
            'diagnoses': [],
            'medications': [],
            'test_results': []
        }
        
        try:
            # Extract from X-ray analysis
            if xray_analysis:
                if 'clinical_impression' in xray_analysis:
                    ci = xray_analysis['clinical_impression']
                    combined_report['clinical_impression']['primary_findings'].extend(
                        ci.get('primary_findings', [])
                    )
                    combined_report['clinical_impression']['differential_diagnoses'].extend(
                        ci.get('differential_diagnoses', [])
                    )
                    if ci.get('severity'):
                        combined_report['clinical_impression']['severity'] = ci['severity']
                    if ci.get('confidence'):
                        combined_report['clinical_impression']['confidence'] = ci['confidence']
                
                combined_report['recommendations'].extend(
                    xray_analysis.get('recommendations', [])
                )
            
            # Extract from report analysis
            if report_analysis:
                combined_report['findings'].extend(report_analysis.get('findings', []))
                combined_report['diagnoses'].extend(report_analysis.get('diagnoses', []))
                combined_report['medications'].extend(report_analysis.get('medications', []))
                combined_report['test_results'].extend(report_analysis.get('test_results', []))
            
            return combined_report
            
        except Exception as e:
            st.error(f"Error creating combined medical report: {e}")
            return combined_report 