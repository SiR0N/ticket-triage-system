# Ticket Triage System

The Ticket Triage System is a web application designed to categorize and triage incidents reported by users. It uses Large Language Models (LLMs) to determine the category, urgency, department, and summary of each incident.

## Features

- **Incident Categorization**: Automatically categorize incidents into predefined categories.
- **Urgency Assessment**: Determine the urgency level of each incident.
- **Department Assignment**: Assign incidents to the appropriate department.
- **Summary Generation**: Generate a concise summary of the incident.
- **Reasoning Explanation**: Provide reasoning for the categorization and assignment decisions.

---

## Deployment Options

You can run this application either using **Docker** (recommended) or **Locally** using a Python virtual environment.

### Option A: Running with Docker (Recommended)

1. **Clone the Repository**
   ```bash
   git clone https://github.com/SiR0N/ticket-triage-system.git
   cd ticket-triage-system
   ```

2. **Configure Environment Variables**
   Make sure you have your `.env` file properly set up at the root of the project with your configurations and model selections.

3. **Download Required Models**
   Run the environment setup script to automatically download the models specified in your `.env`:
   ```bash
   python scripts/setup_environment.py
   ```

4. **Build and Run with Docker Compose**
   ```bash
   docker compose up --build
   ```

   Once running, you can access:
   - **Frontend UI (Reflex)**: `http://localhost:8002`
   - **Backend API Docs (FastAPI)**: `http://localhost:8000/docs`

---

### Option B: Running Locally (Without Docker)

1. **Clone the Repository**
   ```bash
   git clone https://github.com/SiR0N/ticket-triage-system.git
   cd ticket-triage-system
   ```

2. **Set Up a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt

   ```
4. **Download Required Models**
   Run the setup script to pull the necessary models based on your `.env`:
   ```bash
   python scripts/setup_environment.py
   ```
5. **Execute the Script**
   The `run_app_local` script is provided to run the application locally without using Docker.
   ```bash
   ./run_app_local.sh
   ```
   The application will be available at `http://127.0.0.1:8000`.

---
### API Endpoints

- **POST /triage**
  - **Description**: Submit an incident for triage.
  - **Request Body:**
    ```json
    {
      "provider": "local",  // or "externo"
      "description": "Description of the incident"
    }
    ```
  - **Response:**
    ```json
    {
      "category": "string",
      "urgency": "string",
      "summary": "string",
      "department": "string",
      "reasoning": "string"
    }
    ```

### Example Usage
To triage an incident via curl:
```bash
curl -X POST "http://127.0.0.1:8000/triage" -H "Content-Type: application/json" -d '{"provider": "local", "description": "Network connectivity issue in the office."}'
```

---

## Contributing

Contributions are welcome! Please follow these steps to contribute to the project:

1. **Fork the Repository**
2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make Your Changes**
4. **Commit Your Changes**
   ```bash
   git commit -m "Add your feature description"
   ```
5. **Push to Your Branch**
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
