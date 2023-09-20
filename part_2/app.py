import streamlit as st
import pandas as pd
from ydata_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report
# from pydantic import BaseSettings
# from pydantic_settings import BaseSettings
import great_expectations as gx
import re
import os
import time
import tempfile
import base64
from great_expectations.expectations.expectation import ExpectationConfiguration
from great_expectations.data_context import FileDataContext
from great_expectations.dataset import PandasDataset
import random

# Set the title and description of your app
# Set Streamlit app title
st.title('Pandas Profiling')

# Upload a file
uploaded_file = st.file_uploader("Upload a CSV or XLS file", type=["csv", "xls", "xlsx"])
 
if st.button("Generate Profiling Report"): 
        # Create an empty text element for progress updates
        progress_text = st.empty()

        if uploaded_file is not None:
            file_extension = uploaded_file.name.split(".")[-1].lower()

            if file_extension == "csv":
                df = pd.read_csv(uploaded_file)
            elif file_extension in ["xls", "xlsx"]:
                df = pd.read_excel(uploaded_file)
            else:
                st.error("Unsupported file format. Please upload a CSV or Excel file.")
                st.stop()

            # Perform Pandas Profiling for Origination Data
            profile = ProfileReport(df, title="Origination Data Profiling Report", explorative=True)

            # Simulate progress and update the progress text
            for percent_complete in range(101):
                progress_text.text(f"Pandas Profiling Report is {percent_complete}% complete.")
                if percent_complete == 100:
                    time.sleep(2)  # Wait for 2 seconds at 100% progress
                time.sleep(0.1)  # Simulate processing time

            # Display a loading message while generating the report
            progress_message = st.info("Generating the report. Please wait...")

            # Remove the "Pandas Profiling Report is 100% complete." message
            progress_text.empty()

            # Save the report as an HTML file
            newpath = "temp"
            if not os.path.exists(newpath):
                os.makedirs(newpath)
            # temp_dir = tempfile.mkdtemp()
            report_path = f"{newpath}/origination_data_profile_report.html"
            profile.to_file(report_path)

            # Remove the loading message and display the report
            progress_message.empty()
            st.write(f"### Pandas Profiling Report")
            st.markdown(f'<iframe src="data:text/html;base64,{base64.b64encode(open(report_path, "rb").read()).decode()}" height="1000" width="100%"></iframe>', unsafe_allow_html=True)
            st.write("Pandas Profiling is complete.")
            
            # Create an empty text element for progress updates
            progress_text = st.empty()        

        else:
            st.warning("Please upload a file to generate report")

# Add a footer
st.markdown("---")

st.title('Great Expectations')

# Create a radio button for data type selection
data_type = st.radio("Select the Dataset Type:", ("Origination Data", "Monthly Performance Data"))

# Create a button to trigger data summary
if st.button("Generate Validation Report"):

    # Check if a file has been uploaded
    if uploaded_file is not None:

        # Read and display the uploaded file
        if data_type == "Origination Data":

            # Process Origination Data here
            try:

                columns = [
                    "CREDIT SCORE",
                    "FIRST PAYMENT DATE",
                    "FIRST TIME HOMEBUYER FLAG",
                    "MATURITY DATE",
                    "METROPOLITAN STATISTICAL AREA (MSA) OR METROPOLITAN DIVISION",
                    "MORTGAGE INSURANCE PERCENTAGE (MI %)",
                    "NUMBER OF UNITS",
                    "OCCUPANCY STATUS",
                    "ORIGINAL COMBINED LOAN-TO-VALUE (CLTV)",
                    "ORIGINAL DEBT-TO-INCOME (DTI) RATIO",
                    "ORIGINAL UPB",
                    "ORIGINAL LOAN-TO-VALUE (LTV)",
                    "ORIGINAL INTEREST RATE",
                    "CHANNEL",
                    "PREPAYMENT PENALTY MORTGAGE (PPM) FLAG",
                    "AMORTIZATION TYPE (FORMERLY PRODUCT TYPE)",
                    "PROPERTY STATE",
                    "PROPERTY TYPE",
                    "POSTAL CODE",
                    "LOAN SEQUENCE NUMBER",
                    "LOAN PURPOSE",
                    "ORIGINAL LOAN TERM",
                    "NUMBER OF BORROWERS",
                    "SELLER NAME",
                    "SERVICER NAME",
                    "SUPER CONFORMING FLAG",
                    "PRE-HARP LOAN SEQUENCE NUMBER",
                    "PROGRAM INDICATOR",
                    "HARP INDICATOR",
                    "PROPERTY VALUATION METHOD",
                    "INTEREST ONLY (I/O) INDICATOR",
                    "MORTGAGE INSURANCE CANCELLATION INDICATOR"
                ]

                df = pd.read_csv(uploaded_file, header=None, names=columns)

                #variables
                path_to_repo_dir="part_2"
                path_to_data_dir=f"gx/data"
                
                if not os.path.exists(path_to_data_dir):
                    os.mkdir(path_to_data_dir)
                else:
                    # List all files in the directory
                    files = os.listdir(path_to_data_dir)

                    # Iterate through the files and remove CSV files
                    for file in files:
                        if file.endswith("Origination.csv"):
                            file_path = os.path.join(path_to_data_dir, file)
                            os.remove(file_path)

                expectation_suite_name="Origination_Data_File_Suite"

                #Store the data in CSV format in the 'data' folder
                df.to_csv(f"{path_to_data_dir}/Origination.csv", index=False)

                #Initialize the GX Dir
                context = FileDataContext.create(project_root_dir=path_to_repo_dir)

                # Give your Datasource a name
                num = random.randint(1,5000)
                datasource_name = f"Local_FileSystem_Source{num}"
                datasource = context.sources.add_pandas_filesystem(name=datasource_name, base_directory=path_to_data_dir)

                # Give your first Asset a name
                asset_name = "Origination_Data"
                asset = datasource.add_csv_asset(name=asset_name)

                # Build batch request
                batch_request = asset.build_batch_request()

                data_asset = context.get_datasource(datasource_name).get_asset(asset_name)
                batch_request=data_asset.build_batch_request()

                context.list_expectation_suite_names()
                context.add_or_update_expectation_suite(expectation_suite_name)
                validator = context.get_validator(batch_request=batch_request, expectation_suite_name=expectation_suite_name)
                
                for column in columns:
                    validator.expect_column_values_to_not_be_null(column=column)

                # Validation for "CREDIT SCORE"
                # credit_score_expectation_config = {
                #     "type": "expect_column_values_to_be_of_type",
                #     "kwargs": {
                #         "column": "CREDIT SCORE",
                #         "type_": "int",
                #     },
                # }

                # Schema Validation
                validator.expect_column_values_to_match_regex(column="CREDIT SCORE", regex=r'^\\d{4}$')
                validator.expect_column_values_to_match_regex(column="FIRST PAYMENT DATE", regex=r'^\d{6}$')
                validator.expect_column_values_to_match_regex(column="FIRST TIME HOMEBUYER FLAG", regex=r'^[A-Za-z]$')
                validator.expect_column_values_to_match_regex(column="MATURITY DATE", regex=r'^\\d{6}$')
                validator.expect_column_values_to_match_regex(column="METROPOLITAN STATISTICAL AREA (MSA) OR METROPOLITAN DIVISION", regex=r'^\\d{5}$')
                validator.expect_column_values_to_match_regex(column="MORTGAGE INSURANCE PERCENTAGE (MI %)", regex=r'^\\d{3}$')
                validator.expect_column_values_to_match_regex(column="NUMBER OF UNITS", regex=r'^\\d{2}$')
                validator.expect_column_values_to_match_regex(column="OCCUPANCY STATUS", regex=r'^[A-Za-z]$')
                validator.expect_column_values_to_match_regex(column="ORIGINAL COMBINED LOAN-TO-VALUE (CLTV)", regex=r'^\\d{3}$')
                validator.expect_column_values_to_match_regex(column="ORIGINAL DEBT-TO-INCOME (DTI) RATIO", regex=r'^\\d{3}$')
                validator.expect_column_values_to_match_regex(column="ORIGINAL UPB", regex=r'^\\d{12}$')
                validator.expect_column_values_to_match_regex(column="ORIGINAL LOAN-TO-VALUE (LTV)", regex=r'^\\d{3}$')
                validator.expect_column_values_to_match_regex(column="ORIGINAL INTEREST RATE", regex=r'^\d{6}\.\d{3}$')						
                validator.expect_column_values_to_match_regex(column="CHANNEL", regex=r'^[A-Za-z]$')
                validator.expect_column_values_to_match_regex(column="PREPAYMENT PENALTY MORTGAGE (PPM) FLAG", regex=r'^[A-Za-z]$')
                validator.expect_column_values_to_match_regex(column="AMORTIZATION TYPE (FORMERLY PRODUCT TYPE)", regex=r'^[A-Za-z]{5}$')
                validator.expect_column_values_to_match_regex(column="PROPERTY STATE", regex=r'^[A-Za-z]{2}$')
                validator.expect_column_values_to_match_regex(column="PROPERTY TYPE", regex=r'^[A-Za-z]{2}$')
                validator.expect_column_values_to_match_regex(column="POSTAL CODE", regex=r'^\\d{5}$')
                validator.expect_column_values_to_match_regex(column="LOAN SEQUENCE NUMBER", regex=r'^[A-Za-z]{1}[A-Za-z]{3}\\d{7}$')
                validator.expect_column_values_to_match_regex(column="LOAN PURPOSE", regex=r'^[A-Za-z]$')
                validator.expect_column_values_to_match_regex(column="ORIGINAL LOAN TERM", regex=r'^\\d{3}$')
                validator.expect_column_values_to_match_regex(column="NUMBER OF BORROWERS", regex=r'^\\d{2}$')
                validator.expect_column_values_to_match_regex(column="SELLER NAME", regex=r'^[A-Za-z0-9]{1,60}$')
                validator.expect_column_values_to_match_regex(column="SERVICER NAME", regex=r'^[A-Za-z0-9]{1,60}$')
                validator.expect_column_values_to_match_regex(column="SUPER CONFORMING FLAG", regex=r'^[A-Za-z]$')
                validator.expect_column_values_to_match_regex(column="PRE-HARP LOAN SEQUENCE NUMBER", regex=r'^[A-Za-z]{1}[A-Za-z]{3}\\d{7}$')
                validator.expect_column_values_to_match_regex(column="PROGRAM INDICATOR", regex=r'^[A-Za-z0-9]{1}$')
                validator.expect_column_values_to_match_regex(column="HARP INDICATOR", regex=r'^[A-Za-z]{1}$')
                validator.expect_column_values_to_match_regex(column="PROPERTY VALUATION METHOD", regex=r'^\\d{1}$')
                validator.expect_column_values_to_match_regex(column="INTEREST ONLY (I/O) INDICATOR", regex=r'^[A-Za-z]{1}$')
                validator.expect_column_values_to_match_regex(column="MORTGAGE INSURANCE CANCELLATION INDICATOR", regex=r'^[A-Za-z]{1}$')

                validator.save_expectation_suite()

                checkpoint = context.add_or_update_checkpoint(
                    name="my_quickstart_checkpoint",
                    validator=validator,
                )

                checkpoint_result = checkpoint.run(run_name="Manual run for Origination Data")
                context.view_validation_result(checkpoint_result)
                context.build_data_docs()

            except Exception as e:
                st.error(f"An error occurred: {e}")

        elif data_type == "Monthly Performance Data":

            # Process Monthly Performance Data here
            try:

                columns = [

                    "Loan Sequence Number",
                    "Monthly Reporting Period",
                    "Current Actual UPB",
                    "Current Loan Delinquency Status",
                    "Loan Age",
                    "Remaining Months to Legal Maturity",
                    "Defect Settlement Date",
                    "Modification Flag",
                    "Zero Balance Code",
                    "Zero Balance Effective Date",
                    "Current Interest Rate",
                    "Current Deferred UPB",
                    "Due Date of Last Paid Installment (DDLPI)",
                    "MI Recoveries",
                    "Net Sales Proceeds",
                    "Non MI Recoveries",
                    "Expenses",
                    "Legal Costs",
                    "Maintenance and Preservation Cost",
                    "Taxes and Insurance",
                    "Miscellaneous Expenses",
                    "Actual Loss Calculation",
                    "Modification Cost",
                    "Step Modification Flag",
                    "Deferred Payment Plan",
                    "Estimated Loan-to-Value (ELTV)",
                    "Zero Balance Removal UPB",
                    "Delinquent Accrued Interest",
                    "Delinquency Due to Disaster",
                    "Borrower Assistance Status Code",
                    "Current Month Modification Cost",
                    "Interest Bearing UPB"
                ]

                df = pd.read_csv(uploaded_file, header=None, names=columns)

                #variables
                path_to_repo_dir="part_2"
                path_to_data_dir=f"{path_to_repo_dir}/gx/data"
                
                if not os.path.exists(path_to_data_dir):
                    os.mkdir(path_to_data_dir)
                else:
                    # List all files in the directory
                    files = os.listdir(path_to_data_dir)

                    # Iterate through the files and remove CSV files
                    for file in files:
                        if file.endswith("Monthly.csv"):
                            file_path = os.path.join(path_to_data_dir, file)
                            os.remove(file_path)

                expectation_suite_name="Monthly_Data_File_Suite"

                df.to_csv(f"{path_to_data_dir}/Monthly.csv", index=False)

                context = FileDataContext.create(project_root_dir=path_to_repo_dir)

                # Give your Datasource a name
                num = random.randint(1,5000)
                datasource_name = f"Local_FileSystem_Source{num}"
                datasource = context.sources.add_pandas_filesystem(name=datasource_name, base_directory=path_to_data_dir)

                # Give your first Asset a name
                asset_name = "Monthly_Data"
                asset = datasource.add_csv_asset(name=asset_name)

                # Build batch request
                batch_request = asset.build_batch_request()

                data_asset = context.get_datasource(datasource_name).get_asset(asset_name)
                batch_request=data_asset.build_batch_request()

                context.list_expectation_suite_names()
                context.add_or_update_expectation_suite(expectation_suite_name)
                validator = context.get_validator(batch_request=batch_request, expectation_suite_name=expectation_suite_name)

                for column in columns:
                    validator.expect_column_values_to_not_be_null(column=column)

                # Schema Validation
                validator.expect_column_values_to_match_regex(column="Loan Sequence Number", regex=r'^[A-Z]{1}\d{6}[A-Z0-9]{6}$')
                validator.expect_column_values_to_match_regex(column="Monthly Reporting Period", regex=r'^\d{6}$')
                validator.expect_column_values_to_match_regex(column="Current Actual UPB", regex=r'^\d{1,10}(\.\d{1,2})?$')
                validator.expect_column_values_to_match_regex(column="Current Loan Delinquency Status", regex=r'^[A-Za-z0-9]{3}$')
                validator.expect_column_values_to_match_regex(column="Loan Age", regex=r'^\d{1,3}$')
                validator.expect_column_values_to_match_regex(column="Remaining Months to Legal Maturity", regex=r'^\d{1,3}$')
                validator.expect_column_values_to_match_regex(column="Defect Settlement Date", regex=r'^\d{6}$')
                validator.expect_column_values_to_match_regex(column="Modification Flag", regex=r'^[A-Za-z]{1}$')
                validator.expect_column_values_to_match_regex(column="Zero Balance Code", regex=r'^\d{2}$')
                validator.expect_column_values_to_match_regex(column="Zero Balance Effective Date", regex=r'^\d{6}$')
                validator.expect_column_values_to_match_regex(column="Current Interest Rate", regex=r'^\d{1,5}(\.\d{1,3})?$')
                validator.expect_column_values_to_match_regex(column="Current Deferred UPB", regex=r'^\d{1,10}(\.\d{1,2})?$')
                validator.expect_column_values_to_match_regex(column="Due Date of Last Paid Installment (DDLPI)", regex=r'^\d{6}$')
                validator.expect_column_values_to_match_regex(column="MI Recoveries", regex=r'^\d{1,10}(\.\d{1,2})?$')
                validator.expect_column_values_to_match_regex(column="Net Sales Proceeds", regex=r'^[A-Za-z0-9]{1,14}$')
                validator.expect_column_values_to_match_regex(column="Non MI Recoveries", regex=r'^\d{1,10}(\.\d{1,2})?$')
                validator.expect_column_values_to_match_regex(column="Expenses", regex=r'^\d{1,10}(\.\d{1,2})?$')
                validator.expect_column_values_to_match_regex(column="Legal Costs", regex=r'^\d{1,10}(\.\d{1,2})?$')
                validator.expect_column_values_to_match_regex(column="Maintenance and Preservation Costs", regex=r'^\d{1,10}(\.\d{1,2})?$')
                validator.expect_column_values_to_match_regex(column="Taxes and Insurance", regex=r'^\d{1,10}(\.\d{1,2})?$')
                validator.expect_column_values_to_match_regex(column="Miscellaneous Expenses", regex=r'^\d{1,10}(\.\d{1,2})?$')
                validator.expect_column_values_to_match_regex(column="Actual Loss Calculation", regex=r'^\d{1,10}(\.\d{1,2})?$')
                validator.expect_column_values_to_match_regex(column="Modification Cost", regex=r'^\d{1,10}(\.\d{1,2})?$')
                validator.expect_column_values_to_match_regex(column="Step Modification Flag", regex=r'^[A-Za-z]{1}$')
                validator.expect_column_values_to_match_regex(column="Deferred Payment Plan", regex=r'^[A-Za-z]{1}$')
                validator.expect_column_values_to_match_regex(column="Estimated Loan-to-Value (ELTV)", regex=r'^\d{1,4}(\.\d{1,2})?$')
                validator.expect_column_values_to_match_regex(column="Zero Balance Removal UPB", regex=r'^\d{1,10}(\.\d{1,2})?$')
                validator.expect_column_values_to_match_regex(column="Delinquent Accrued Interest", regex=r'^\d{1,10}(\.\d{1,2})?$')
                validator.expect_column_values_to_match_regex(column="Delinquency Due to Disaster", regex=r'^[A-Za-z]{1}$')
                validator.expect_column_values_to_match_regex(column="Borrower Assistance Status Code", regex=r'^[A-Za-z]{1}$')
                validator.expect_column_values_to_match_regex(column="Current Month Modification Cost", regex=r'^\d{1,10}(\.\d{1,2})?$')
                validator.expect_column_values_to_match_regex(column="Interest Bearing UPB", regex=r'^\d{1,10}(\.\d{1,2})?$')

                validator.save_expectation_suite()

                checkpoint = context.add_or_update_checkpoint(
                    name="my_quickstart_checkpoint_v2",
                    validator=validator,
                )

                checkpoint_result = checkpoint.run(run_name="Manual Run for Monthly Data")

                context.view_validation_result(checkpoint_result)

                context.build_data_docs()

            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error(f"Selected Data Type does not match the uploaded file type).")

    else:
        st.warning("Please upload a file")

# Add a footer
st.markdown("---")
st.write("Created by Huskies 🐾")