# Student Assessment Feedback System (Prototype for Brockport ACM Project)
<img width="1392" alt="Screenshot 2024-10-22 at 3 17 35 PM" src="https://github.com/user-attachments/assets/b9afa54f-78e0-4028-abb0-915074da6568">

## Description
This project is a Student Assessment Feedback System that uses AI to provide personalized feedback on student answers. It leverages OpenAI's GPT model and ChromaDB for efficient content storage and retrieval.

## Features
- Embeds and stores module content using ChromaDB
- Loads questions and answers from a JSON file
- Collects student answers through a Streamlit interface
- Generates AI-powered feedback based on student responses and relevant content

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/student-assessment-feedback-system.git
   cd student-assessment-feedback-system
   ```
2. Set up your environment variables:
   Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   AWS_USERNAME=your_db_username
   AWS_PASSWORD=your_db_password
   DATABASE_HOST_AWS=aws_host_url
   DB_PORT=5432  # Default PostgreSQL port
   DB_NAME=your_db_name
   ```

3. Set up Docker:
    
   Build the Docker image: In the project directory, build the Docker image using the    provided Dockerfile:
   ```
     docker build -t student-assessment-feedback-system .

   ```
4. Run the Docker container:
   Once the image is built, you can run the container. Make sure to pass the 
   environment variables using the .env file. This file should contain your 
   PostgreSQL connection settings and the OpenAI API key.
   ```
     docker run --env-file .env -p 8501:8501 student-assessment-feedback-system

   ```
   This will run the application in a containerized environment on port 8501. You can 
   access the Streamlit interface at http://localhost:8501.

## Usage

1. Prepare your module content:
   Place your PDF file in the appropriate directory and update the `module_content_fp` variable in the script.

2. Prepare your questions and answers:
   Create a JSON file with questions and answers, and update the `questions_fp` variable in the script.

3. Set up PostgreSQL:
   Ensure that your PostgreSQL instance is running and accessible. You can either use    a local PostgreSQL server or a managed service like AWS RDS or Heroku Postgres. If    running locally, use Docker to set up a PostgreSQL container if needed.

4. Open the provided URL in your web browser to access the Student Assessment Feedback System.

