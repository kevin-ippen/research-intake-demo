import io
import streamlit as st
from databricks.sdk import WorkspaceClient

# Initialize Databricks client
w = WorkspaceClient()

# Create the UI components
st.title("File Upload to UC Volume")

uploaded_file = st.file_uploader(label="Select file")

upload_volume_path = st.text_input(
    label="Specify a three-level Unity Catalog volume name (catalog.schema.volume_name)",
    placeholder="users.kevin_ippen.research_files",
)

if st.button("Save changes"):
    if uploaded_file is not None and upload_volume_path:
        try:
            # Read the uploaded file
            file_bytes = uploaded_file.read()
            binary_data = io.BytesIO(file_bytes)
            file_name = uploaded_file.name
            
            # Parse the volume path
            parts = upload_volume_path.strip().split(".")
            catalog = parts[0]
            schema = parts[1]
            volume_name = parts[2]
            
            # Construct the full volume path
            volume_file_path = f"/Volumes/{catalog}/{schema}/{volume_name}/{file_name}"
            
            # Upload the file
            w.files.upload(volume_file_path, binary_data, overwrite=True)
            
            st.success(f"File uploaded successfully to {volume_file_path}")
            
        except Exception as e:
            st.error(f"Upload failed: {str(e)}")
    else:
        st.warning("Please select a file and specify a volume path")