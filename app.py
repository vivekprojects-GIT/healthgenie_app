"""
HealthGenie App - AI-Powered Healthcare Assistant
Main Streamlit application for medical analysis and recommendations
"""
import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import config
from agents.controller import HealthcareController
from utils.image_helpers import display_image_preview, get_image_info

# Page configuration
st.set_page_config(
    page_title="HealthGenie - AI Healthcare Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_app():
    """Initialize the application and session state"""
    try:
        # Instantiating config will raise if required keys are missing
        _ = config  # This will trigger validation
        
        # Initialize controller in session state
        if 'controller' not in st.session_state:
            st.session_state.controller = HealthcareController()
            
        # Initialize analysis results in session state
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
            
        return True
        
    except Exception as e:
        st.error(f"Configuration Error: {e}")
        st.error("Please ensure you have set up your API keys in the .env file:")
        st.code("""
        GEMINI_API_KEY=your_gemini_api_key
        SERP_API_KEY=your_serp_api_key
        """)
        return False

def display_combined_analysis(xray_results, report_results):
    """Display combined analysis from X-ray and medical report"""
    st.header("🔄 Combined Medical Analysis")
    
    # Compare and combine findings
    combined_findings = []
    confidence_scores = []
    
    if xray_results:
        combined_findings.extend(xray_results['clinical_impression']['primary_findings'])
        if xray_results['clinical_impression']['confidence']:
            # Handle both int and str confidence values
            try:
                confidence_val = xray_results['clinical_impression']['confidence']
                if isinstance(confidence_val, str):
                    # Extract numeric value from string
                    confidence_val = float(''.join(filter(lambda x: x.isdigit() or x == '.', confidence_val)))
                confidence_scores.append(float(confidence_val))
            except (ValueError, TypeError):
                # Skip invalid confidence values
                pass
    
    if report_results:
        combined_findings.extend(report_results.get('findings', []))
        if report_results.get('confidence'):
            # Handle both int and str confidence values
            try:
                confidence_val = report_results.get('confidence')
                if isinstance(confidence_val, str):
                    # Extract numeric value from string
                    confidence_val = float(''.join(filter(lambda x: x.isdigit() or x == '.', confidence_val)))
                confidence_scores.append(float(confidence_val))
            except (ValueError, TypeError):
                # Skip invalid confidence values
                pass
    
    # Display combined findings
    st.subheader("🔍 Combined Medical Findings")
    for finding in set(combined_findings):  # Remove duplicates
        st.write(f"• {finding}")
    
    # Display average confidence if available
    if confidence_scores:
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        st.metric("Overall Confidence Score", f"{avg_confidence:.1f}/10")
    else:
        st.info("Confidence scores not available")

def display_xray_analysis(analysis_results):
    """Display X-ray analysis results"""
    st.header("📋 X-ray Analysis Results")
    
    # Anatomical region info
    st.subheader("🔍 Anatomical Region Details")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Region Information:**")
        st.info(f"Region: {analysis_results['anatomical_region']['region']}")
        st.info(f"Technical Quality: {analysis_results['anatomical_region']['technical_quality']}")
    
    with col2:
        st.write("**Positioning & Variants:**")
        st.info(f"Positioning: {analysis_results['anatomical_region']['positioning']}")
        if analysis_results['anatomical_region']['variants']:
            st.info("Anatomical Variants:")
            for variant in analysis_results['anatomical_region']['variants']:
                st.write(f"• {variant}")

    # Visual findings
    st.subheader("🔬 Visual Findings")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Bone Structure:**")
        for finding in analysis_results['visual_findings']['bone_structure']:
            st.write(f"• {finding}")
            
        st.write("**Soft Tissue:**")
        for finding in analysis_results['visual_findings']['soft_tissue']:
            st.write(f"• {finding}")
    
    with col2:
        st.write("**Alignment:**")
        st.write(analysis_results['visual_findings']['alignment'])
        
        st.write("**Pathological Signs:**")
        for sign in analysis_results['visual_findings']['pathological_signs']:
            st.write(f"• {sign}")

    # Clinical impression
    st.subheader("🏥 Clinical Impression")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Primary Findings:**")
        for finding in analysis_results['clinical_impression']['primary_findings']:
            st.write(f"• {finding}")
    
    with col2:
        st.write("**Differential Diagnoses:**")
        for diagnosis in analysis_results['clinical_impression']['differential_diagnoses']:
            st.write(f"• {diagnosis}")
    
    with col3:
        st.metric("Confidence Level", f"{analysis_results['clinical_impression']['confidence']}/10")
        st.metric("Severity", analysis_results['clinical_impression']['severity'])

def display_report_analysis(report_results):
    """Display medical report analysis results"""
    st.header("📄 Medical Report Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Key Findings")
        for finding in report_results.get('findings', []):
            st.write(f"• {finding}")
            
        st.subheader("Current Medications")
        for med in report_results.get('medications', []):
            st.write(f"• {med}")
    
    with col2:
        st.subheader("Diagnoses")
        for diagnosis in report_results.get('diagnoses', []):
            st.write(f"• {diagnosis}")
            
        st.subheader("Test Results")
        for test in report_results.get('test_results', []):
            st.write(f"• {test}")

def display_meal_plan(meal_plan):
    """Display meal plan recommendations"""
    st.header("🍽️ Personalized 3-Day Meal Plan")
    
    # Nutritional requirements
    st.subheader("📊 Nutritional Requirements")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Calories:**")
        st.info(meal_plan['nutritional_requirements']['calories'])
    
    with col2:
        st.write("**Macronutrients:**")
        for macro in meal_plan['nutritional_requirements']['macros']:
            st.write(f"• {macro}")
    
    with col3:
        st.write("**Micronutrients:**")
        for micro in meal_plan['nutritional_requirements']['micros']:
            st.write(f"• {micro}")

    # Daily meal plans
    st.subheader("📅 Daily Meal Plans")
    tab1, tab2, tab3 = st.tabs(["Day 1", "Day 2", "Day 3"])
    
    for i, tab in enumerate([tab1, tab2, tab3], 1):
        with tab:
            day_key = f'day{i}'
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🌅 Breakfast:**")
                for item in meal_plan['daily_plans'][day_key]['breakfast']:
                    st.write(f"• {item}")
                    
                st.write("**🥗 Lunch:**")
                for item in meal_plan['daily_plans'][day_key]['lunch']:
                    st.write(f"• {item}")
            
            with col2:
                st.write("**🍽️ Dinner:**")
                for item in meal_plan['daily_plans'][day_key]['dinner']:
                    st.write(f"• {item}")
                    
                st.write("**🥪 Snacks:**")
                for item in meal_plan['daily_plans'][day_key]['snacks']:
                    st.write(f"• {item}")

    # Dietary guidelines
    st.subheader("🎯 Dietary Guidelines")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Recommended Foods:**")
        for food in meal_plan['guidelines']['recommended_foods']:
            st.write(f"• {food}")
    
    with col2:
        st.write("**Foods to Avoid:**")
        for food in meal_plan['guidelines']['foods_to_avoid']:
            st.write(f"• {food}")
    
    st.write("**💧 Hydration Guidelines:**")
    st.info(meal_plan['guidelines']['hydration'])
    
    if meal_plan['guidelines']['supplements']:
        st.write("**💊 Supplement Recommendations:**")
        for supplement in meal_plan['guidelines']['supplements']:
            st.write(f"• {supplement}")

def display_hospital_recommendations(recommendations):
    """Display enhanced hospital recommendations with medical context"""
    st.header("🏥 Intelligent Hospital Recommendations")
    
    # Display search context
    if 'search_context' in recommendations:
        context = recommendations['search_context']
        
        with st.expander("📋 Recommendation Context", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**🏥 Search Location:**")
                st.info(f"📍 {context['search_location']}")
                
                st.write("**⚡ Severity Level:**")
                severity_color = {
                    'mild': '🟢',
                    'moderate': '🟡', 
                    'severe': '🔴',
                    'critical': '🚨'
                }
                severity_icon = severity_color.get(context.get('severity', 'moderate'), '🟡')
                st.write(f"{severity_icon} {context.get('severity', 'Moderate').title()}")
                
            with col2:
                st.write("**🩺 Medical Conditions:**")
                conditions = context.get('conditions', [])
                if conditions:
                    for condition in conditions[:3]:  # Show top 3
                        st.write(f"• {condition}")
                else:
                    st.write("• General medical care")
                
            with col3:
                st.write("**👨‍⚕️ Required Specialties:**")
                specialties = context.get('specialties', [])
                if specialties and 'general' not in specialties:
                    for specialty in specialties:
                        st.write(f"• {specialty.title()}")
                else:
                    st.write("• General Medicine")
                
                st.write("**🚨 Urgency Level:**")
                urgency_icon = "🚨" if context.get('urgency') == 'urgent' else "📅"
                st.write(f"{urgency_icon} {context.get('urgency', 'Routine').title()}")
        
        # Display recommendation basis
        if 'recommendation_basis' in recommendations:
            st.info(f"**📊 Recommendation Basis:** {recommendations['recommendation_basis']}")
    
    st.write(f"**🔍 Total Hospitals Found:** {recommendations.get('total_found', 0)}")
    st.divider()
    
    # Display top hospitals with enhanced information
    for hospital in recommendations.get('top_hospitals', []):
        # Hospital header with rank and score
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"#{hospital.get('rank', 1)} {hospital['name']}")
        with col2:
            score = hospital.get('relevance_score', 0)
            if score > 50:
                st.success(f"🎯 Match: {score}")
            elif score > 30:
                st.info(f"🎯 Match: {score}")
            else:
                st.warning(f"🎯 Match: {score}")
        
        # Main hospital information
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write("**📄 Hospital Description:**")
            st.write(hospital['description'])
            
            if hospital.get('website'):
                st.markdown(f"**🌐 [Visit Hospital Website]({hospital['website']})**")
        
        with col2:
            # Emergency services
            if hospital.get('emergency_services', False):
                st.success("🚑 Emergency Services")
            else:
                st.info("🏥 Regular Services")
            
            # Search context
            st.write("**🔍 Found via:**")
            search_context = hospital.get('search_context', 'General search')
            st.caption(search_context)
        
        with col3:
            # Quality indicators
            quality_indicators = hospital.get('quality_indicators', [])
            if quality_indicators:
                st.write("**⭐ Quality Indicators:**")
                for indicator in quality_indicators[:3]:  # Show top 3
                    st.write(f"✓ {indicator}")
        
        # Why recommended
        if hospital.get('why_recommended'):
            st.success(f"**💡 Why Recommended:** {hospital['why_recommended']}")
        
        # Medical specialties
        specialties = hospital.get('specialties', [])
        if specialties:
            st.write("**👨‍⚕️ Medical Specialties:**")
            specialty_cols = st.columns(min(3, len(specialties)))
            for idx, specialty in enumerate(specialties[:6]):  # Show up to 6 specialties
                with specialty_cols[idx % 3]:
                    st.write(f"• {specialty}")
        
        st.divider()
    
    # Additional information
    if not recommendations.get('top_hospitals'):
        st.warning("No hospital recommendations available. Please try again or consult your healthcare provider.")
    else:
        st.info("💡 **Note:** These recommendations are based on your medical analysis. Please consult with your healthcare provider before making any medical decisions.")

def main():
    """Main application function"""
    st.set_page_config(
        page_title="HealthGenie - AI Healthcare Assistant",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🏥 HealthGenie - AI Healthcare Assistant")
    st.markdown("### Autonomous medical analysis using Gemini AI and SERP API")
    
    # Status indicators
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔬 X-ray Analysis", "Ready", delta="Gemini 2.5 Flash")
    with col2:
        st.metric("📄 Report Analysis", "Ready", delta="Gemini 2.5 Flash")
    with col3:
        st.metric("🍽️ Meal Planning", "Ready", delta="Gemini AI")
    with col4:
        st.metric("🏥 Hospital Search", "Ready", delta="SERP API")

    if not initialize_app():
        return
    
    st.divider()
    
    # File upload section
    st.subheader("📁 Upload Medical Files")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📸 X-ray Image**")
        xray_file = st.file_uploader(
            "Upload X-ray Image", 
            type=config.SUPPORTED_IMAGE_FORMATS,
            help="Upload a clear X-ray image for analysis"
        )
        if xray_file:
            st.image(xray_file, caption="Uploaded X-ray Image", use_container_width=True)
            st.success("✅ X-ray uploaded successfully")
    
    with col2:
        st.write("**📄 Medical Report**")
        report_file = st.file_uploader(
            "Upload Medical Report", 
            type=config.SUPPORTED_DOCUMENT_FORMATS,
            help="Upload medical report as image or PDF"
        )
        if report_file:
            st.success("✅ Medical report uploaded successfully")
            with st.expander("📋 File Info"):
                info = get_image_info(report_file)
                st.json(info)
    
    # Analysis button
    st.divider()
    
    # Handle analysis from sidebar
    if getattr(st.session_state, 'analysis_started', False):
        if xray_file or report_file:
            # Create progress container
            progress_container = st.container()
            
            with progress_container:
                st.header("🤖 AI Analysis in Progress")
                
                # Process files using healthcare controller
                controller = HealthcareController()
                results = controller.process_files(xray_file, report_file, progress_container)
                
                # Store results in session state
                st.session_state.analysis_results = results
                st.session_state.analysis_started = False
                
                if not results.get('errors'):
                    st.balloons()
        else:
            st.error("No files found for analysis. Please upload files and try again.")
    
    # Legacy analysis button (kept for backward compatibility)
    if not getattr(st.session_state, 'analysis_started', False):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Autonomous Analysis", type="primary", use_container_width=True):
                if not (xray_file or report_file):
                    st.error("❌ Please upload at least one file to begin analysis.")
                    return
                
                # Set analysis started flag
                st.session_state.analysis_started = True
                st.rerun()
    
    # Display results if available
    if st.session_state.analysis_results:
        st.divider()
        results = st.session_state.analysis_results
        
        # Results summary
        st.subheader("📊 Analysis Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            has_xray = bool(results.get('xray_analysis'))
            st.metric("X-ray Analysis", "✅ Complete" if has_xray else "❌ Not provided")
        
        with col2:
            has_report = bool(results.get('report_analysis'))
            st.metric("Report Analysis", "✅ Complete" if has_report else "❌ Not provided")
        
        with col3:
            has_meal = bool(results.get('meal_plan'))
            st.metric("Meal Plan", "✅ Generated" if has_meal else "❌ Failed")
        
        with col4:
            has_hospitals = bool(results.get('hospital_recommendations'))
            st.metric("Hospitals Found", "✅ Available" if has_hospitals else "❌ Not found")
        
        st.divider()
        
        # Create tabs for results
        tabs = st.tabs([
            "🔄 Combined Analysis",
            "📋 X-ray Results", 
            "📄 Report Results",
            "🍽️ Meal Plan",
            "🏥 Hospitals"
        ])
        
        with tabs[0]:
            if results.get('xray_analysis') or results.get('report_analysis'):
                display_combined_analysis(
                    results.get('xray_analysis'),
                    results.get('report_analysis')
                )
            else:
                st.info("No analysis data available for combination")
        
        with tabs[1]:
            if results.get('xray_analysis'):
                display_xray_analysis(results['xray_analysis'])
            else:
                st.info("No X-ray analysis available")
        
        with tabs[2]:
            if results.get('report_analysis'):
                display_report_analysis(results['report_analysis'])
            else:
                st.info("No report analysis available")
        
        with tabs[3]:
            if results.get('meal_plan'):
                display_meal_plan(results['meal_plan'])
            else:
                st.info("No meal plan available")
        
        with tabs[4]:
            if results.get('hospital_recommendations'):
                display_hospital_recommendations(results['hospital_recommendations'])
            else:
                st.info("No hospital recommendations available")

if __name__ == "__main__":
    main() 