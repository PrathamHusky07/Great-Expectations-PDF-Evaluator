import streamlit as st
from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.onprem.client import User
import os
from diagrams.programming.language import Python

temp_dir = "temp_diagram"
os.makedirs(temp_dir, exist_ok=True)
# Create the diagram
with Diagram("Workflow Diagram", show=False) as diag:
    user = User("user")
    cs = Custom("Streamlit","part_1/images/streamlit.png")
    
    with Cluster("Libraries"):
        pypdf = Custom("PyPDF","part_1/images/streamlit.png")
        nougat = Custom("Nougat","part_1/images/streamlit.png")

    with Cluster("Codebase"):
        python_code = Python("Python")
        colab = Custom("Colab","part_1/images/streamlit.png")
    
    cs1 = Custom("Streamlit","/part_1/images/streamlit.png")

    user >> Edge(label="User interacts with Streamlit") >> cs
    cs >> Edge(label="If PyPDF is Selected") >> pypdf
    cs >> Edge(label="If Nougat is Selected") >> nougat
    pypdf >> Edge(label="Calling the function in Python") >> python_code
    python_code >> Edge(label="View Parsed PDF") >> cs1 
    nougat >> Edge(label="Calling the function in Python") >> colab
    colab >> Edge(label="View Parsed PDF") >> cs1 

output_image_path = os.path.join(temp_dir, "workflow_diagram.png")


# Create a Streamlit page to display the diagram
st.title("Workflow Diagram")
st.image("/home/sarvesh/streamli_part1/workflow_diagram.png")