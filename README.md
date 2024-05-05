**Project Overview:**

The project focuses on developing a system to calculate and store pipeline efficiency metrics for Agile Release Trains (ARTs). It utilizes a serverless architecture on AWS for scalability and cost-effectiveness.

**Key Components:**

* **Database (MySQL):** Stores information about ARTs, configurations, and pipeline efficiency data. Database credentials are securely managed with AWS Secrets Manager.
* **AWS Services:**
    * **API Gateway:** Provides endpoints for interacting with the program functions.
    * **Lambda Functions (Python):** Implement functionalities like retrieving ART information, configurations, and saving pipeline efficiency data.
    * **Secrets Manager (Optional):** Securely stores database credentials (used in version 1 of the serverless template).
    * **Step Functions (Optional - version 1):** Orchestrates the workflow of calculating and saving pipeline efficiency data.

**Code Analysis:**

* **SQL Scripts:** Create and manage database tables for storing ART details, configurations, and pipeline efficiency data.
* **AWS Serverless Templates (sam-program-template.yaml):** Define the infrastructure for deployment on AWS. Two versions exist, with version 1 using Step Functions for workflow orchestration and version 2 simplifying the structure.
* **Python Lambda Functions:**
    * `get-all-arts.py`: Retrieves information about all ARTs.
    * `get-art-configuration.py`: Retrieves configuration details for a specific ART.
    * `get-art-pipeline-efficiency.py`: Retrieves pipeline efficiency data for a specific ART.
    * `save-art-pipeline-efficiency.py`: Saves calculated pipeline efficiency data.
    * `calculate-pipeline-efficiency.py`: Calculates pipeline efficiency metrics based on configurations and Jira issue data.

**Functionality Breakdown:**

1. **Retrieving ART Information:**
    * `get-all-arts.py` retrieves details about all ARTs from the database.
    * `get-art-configuration.py` retrieves configuration details for a specific ART.
2. **Calculating Pipeline Efficiency:**
    * `calculate-pipeline-efficiency.py` calculates pipeline efficiency metrics (minimum, maximum, average lead time) based on configurations and Jira issue data.
3. **Saving Pipeline Efficiency Data:**
    * `save-art-pipeline-efficiency.py` iterates through a list of ART pipeline efficiency objects and saves them to the database.

**Deployment and Getting Started:**

* Refer to separate documentation for detailed instructions.
* Involves packaging the code and configuration files for deployment using AWS Serverless Application Model (SAM).
* Setting up environment variables or Secrets Manager for database credentials is required.

**Overall, this project demonstrates the use of AWS serverless technologies to build a system for managing ART pipeline efficiency calculations.**




### Install Packages for Layers

```
pip3 install -r requirements.txt -t ./layers/python/
```

```
python3 -m pip install -r requirements.txt -t ./layers/python/
```

### Package & Deploy Program Stack

```
sam package --template-file ./stacks/sam-program-template.yaml --s3-bucket st-lambda-artifacts --output-template-file ./stacks/sam-program-output-template.yaml

sam deploy --template-file ./stacks/sam-program-output-template.yaml --stack-name safe-program-metrics --capabilities CAPABILITY_IAM
```

### Delete a Stack

```
aws cloudformation delete-stack --stack-name [stack-name]

aws cloudformation delete-stack --stack-name safe-program-metrics
```
