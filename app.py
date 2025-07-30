import io
import streamlit as st
from databricks.sdk import WorkspaceClient
from databricks.sql import connect
import datetime
import uuid
import hashlib

# Initialize Databricks client
w = WorkspaceClient()

# Domino's Brand Configuration
DOMINOS_RED = "#E31837"
DOMINOS_BLUE = "#006491" 
DOMINOS_WHITE = "#FFFFFF"
DOMINOS_LIGHT_GRAY = "#F5F5F5"

# Custom CSS for Domino's branding
st.markdown(f"""
<style>
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1000px;
    }}
    
    .stApp {{
        background-color: {DOMINOS_WHITE};
    }}
    
    /* Header styling */
    .dominos-header {{
        background: linear-gradient(135deg, {DOMINOS_RED} 0%, {DOMINOS_BLUE} 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    
    .dominos-header h1 {{
        color: {DOMINOS_WHITE};
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        margin: 0;
        font-size: 2.2rem;
    }}
    
    .dominos-header p {{
        color: {DOMINOS_WHITE};
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }}
    
    /* Form styling */
    .stSelectbox label, .stTextInput label, .stTextArea label, .stMultiSelect label {{
        color: {DOMINOS_BLUE} !important;
        font-weight: bold !important;
        font-size: 1rem !important;
    }}
    
    /* Button styling */
    .stButton > button {{
        background: linear-gradient(135deg, {DOMINOS_RED} 0%, {DOMINOS_BLUE} 100%);
        color: {DOMINOS_WHITE};
        border: none;
        border-radius: 8px;
        font-weight: bold;
        font-size: 1.1rem;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(227, 24, 55, 0.3);
    }}
    
    /* Upload area styling */
    .stFileUploader {{
        border: 2px dashed {DOMINOS_BLUE};
        border-radius: 10px;
        padding: 1rem;
        background-color: {DOMINOS_LIGHT_GRAY};
    }}
    
    /* Success/error message styling */
    .stSuccess {{
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
    }}
    
    .stError {{
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
    }}
    
    /* Info boxes */
    .info-box {{
        background-color: {DOMINOS_LIGHT_GRAY};
        border-left: 4px solid {DOMINOS_BLUE};
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }}
    
    .metadata-section {{
        background-color: {DOMINOS_WHITE};
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="dominos-header">
    <h1>🍕 Domino's Research Intake Portal</h1>
    <p>Upload and organize research documents for AI-powered insights</p>
</div>
""", unsafe_allow_html=True)

# File upload section
st.markdown("### 📁 Document Upload")
uploaded_file = st.file_uploader(
    label="Select your research document",
    type=['pdf', 'ppt', 'pptx', 'doc', 'docx', 'xlsx', 'csv', 'txt'],
    help="Supported formats: PDF, PowerPoint, Word, Excel, CSV, Text files"
)

upload_volume_path = st.text_input(
    label="Unity Catalog Volume Path",
    placeholder="research_library.intake.documents",
    help="Format: catalog.schema.volume_name"
)

# Metadata capture section
st.markdown("### 📋 Document Metadata")
st.markdown('<div class="metadata-section">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    doc_type = st.selectbox(
        "Document Type *",
        ["PDF Report", "Presentation", "Survey Data", "Focus Group", 
         "Analytics Report", "Consumer Insights", "Market Research", 
         "Competitive Analysis", "Other"],
        help="What type of document are you uploading?"
    )
    
    business_area = st.selectbox(
        "Business Area *",
        ["Marketing", "Product Development", "Operations", "Consumer Research", 
         "Competitive Intelligence", "Strategy", "Finance", "Other"],
        help="Which business area does this research support?"
    )
    
    geographic_scope = st.selectbox(
        "Geographic Scope *",
        ["Global", "North America", "US Only", "Regional", "Local Market", 
         "International", "Other"],
        help="What geographic area does this research cover?"
    )
    
    data_source = st.selectbox(
        "Data Source *",
        ["Internal Research", "External Agency", "Public Data", 
         "Customer Feedback", "Partner Data", "Academic Study", "Other"],
        help="Where did this research data come from?"
    )

with col2:
    time_period = st.text_input(
        "Time Period Covered",
        placeholder="Q4 2024, Jan-Mar 2024, 2024, etc.",
        help="When was this data collected or what period does it analyze?"
    )
    
    confidentiality = st.selectbox(
        "Confidentiality Level *",
        ["Internal", "Confidential", "Restricted", "Public"],
        index=0,
        help="What's the sensitivity level of this document?"
    )
    
    content_categories = st.multiselect(
        "Content Categories",
        ["Customer Satisfaction", "Brand Perception", "Product Performance", 
         "Market Trends", "Competitive Analysis", "Consumer Behavior", 
         "Sales Performance", "Digital/Social Media", "Pricing Strategy",
         "Store Operations", "Supply Chain", "Innovation"],
        help="Select all categories that apply to this document"
    )

# Full-width fields
description = st.text_area(
    "Brief Description *",
    placeholder="Provide a 1-2 sentence summary of what this document contains and its key findings...",
    height=80,
    help="This will help others find and understand your research"
)

tags = st.text_input(
    "Key Topics/Tags",
    placeholder="pizza preferences, delivery satisfaction, mobile app, competitor pricing, etc.",
    help="Enter comma-separated tags for better searchability"
)

st.markdown('</div>', unsafe_allow_html=True)

# Info section
st.markdown("""
<div class="info-box">
    <strong>🤖 AI-Ready Research Library</strong><br>
    Your uploaded documents will be processed by our autoloader system to extract text content, 
    making them searchable and ready for AI-powered insights and analysis.
</div>
""", unsafe_allow_html=True)

# Upload button and processing
if st.button("🚀 Upload & Process Document", type="primary"):
    # Validation
    missing_fields = []
    if not uploaded_file:
        missing_fields.append("Document file")
    if not upload_volume_path:
        missing_fields.append("Volume path")
    if not doc_type:
        missing_fields.append("Document type")
    if not business_area:
        missing_fields.append("Business area")
    if not geographic_scope:
        missing_fields.append("Geographic scope")
    if not data_source:
        missing_fields.append("Data source")
    if not confidentiality:
        missing_fields.append("Confidentiality level")
    if not description.strip():
        missing_fields.append("Brief description")
    
    if missing_fields:
        st.error(f"Please fill in the following required fields: {', '.join(missing_fields)}")
    else:
        try:
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            
            # Read the uploaded file
            file_bytes = uploaded_file.read()
            binary_data = io.BytesIO(file_bytes)
            file_name = uploaded_file.name
            
            # Parse the volume path
            parts = upload_volume_path.strip().split(".")
            if len(parts) != 3:
                st.error("Volume path must be in format: catalog.schema.volume_name")
                st.stop()
            catalog = parts[0]
            schema = parts[1]
            volume_name = parts[2]
            
            # Create timestamped filename to avoid conflicts
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{file_id[:8]}_{file_name}"
            
            # Construct the full volume path
            volume_file_path = f"/Volumes/{catalog}/{schema}/{volume_name}/{safe_filename}"
            
            # Upload the file to UC Volume
            w.files.upload(volume_file_path, binary_data, overwrite=True)
            
            # Calculate file hash for deduplication
            file_hash = hashlib.md5(file_bytes).hexdigest()
            
            # Prepare metadata for Delta table
            file_metadata = {
                'file_id': file_id,
                'original_filename': file_name,
                'stored_filename': safe_filename,
                'volume_path': volume_file_path,
                'file_size_bytes': len(file_bytes),
                'file_hash': file_hash,
                'upload_timestamp': datetime.datetime.now().isoformat(),
                'doc_type': doc_type,
                'business_area': business_area,
                'geographic_scope': geographic_scope,
                'time_period_covered': time_period if time_period else None,
                'data_source': data_source,
                'confidentiality_level': confidentiality,
                'content_categories': ','.join(content_categories) if content_categories else None,
                'description': description,
                'tags': tags if tags else None,
                'uploaded_by': 'system_user',  # You can get this from Databricks context
                'processing_status': 'pending'
            }
            
            st.success(f"✅ File uploaded successfully!")
            st.info(f"📍 **File location:** `{volume_file_path}`")
            st.info(f"🆔 **File ID:** `{file_id}`")
            
            # Display metadata summary
            st.markdown("### 📊 Metadata Summary")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **Document Details:**
                - Type: {doc_type}
                - Business Area: {business_area}
                - Geographic Scope: {geographic_scope}
                - Data Source: {data_source}
                """)
            
            with col2:
                st.markdown(f"""
                **Classification:**
                - Confidentiality: {confidentiality}
                - Time Period: {time_period or 'Not specified'}
                - Categories: {', '.join(content_categories) if content_categories else 'None'}
                """)
            
            if tags:
                st.markdown(f"**Tags:** {tags}")
            
            st.markdown(f"**Description:** {description}")
            
            # Show next steps
            st.markdown("""
            ### ⚡ Next Steps
            - **Autoloader Processing**: Your file will be automatically processed to extract text content
            - **AI Indexing**: Content will be indexed for AI-powered search and analysis  
            - **Delta Tables**: Metadata saved to `research_library.intake.file_metadata`
            - **Content Extraction**: Text content will be stored in `research_library.processing.file_content`
            """)
            
            # Note about the SQL commands needed to create tables
            with st.expander("🔧 SQL Setup Commands (for admins)"):
                st.code(f"""
-- Create metadata table
CREATE TABLE IF NOT EXISTS {catalog}.{schema}.file_metadata (
    file_id STRING,
    original_filename STRING,
    stored_filename STRING,
    volume_path STRING,
    file_size_bytes BIGINT,
    file_hash STRING,
    upload_timestamp TIMESTAMP,
    doc_type STRING,
    business_area STRING,
    geographic_scope STRING,
    time_period_covered STRING,
    data_source STRING,
    confidentiality_level STRING,
    content_categories STRING,
    description STRING,
    tags STRING,
    uploaded_by STRING,
    processing_status STRING
) USING DELTA;

-- Create autoloader job for file processing
CREATE OR REFRESH STREAMING LIVE TABLE file_content
AS SELECT 
    _metadata.file_path,
    _metadata.file_name,
    _metadata.file_modification_time,
    *
FROM cloud_files('/Volumes/{catalog}/{schema}/{volume_name}/', 'binaryFile')
                """, language="sql")
            
        except Exception as e:
            st.error(f"❌ Upload failed: {str(e)}")
            st.error("Please check your permissions and volume path configuration.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <strong>Domino's Research Intelligence Platform</strong><br>
    Powered by Databricks Unity Catalog & AI
</div>
""", unsafe_allow_html=True)