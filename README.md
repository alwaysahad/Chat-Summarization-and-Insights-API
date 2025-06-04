# Chat Summarization and Insights API

A FastAPI-based REST API for processing chat data, storing conversations in MongoDB, and generating summaries using Google's Generative AI (Gemini Pro).

## Features

- Real-time chat message ingestion and storage
- Efficient conversation retrieval with filtering capabilities
- AI-powered chat summarization using Google's Generative AI
- Paginated user chat history
- Optimized CRUD operations with MongoDB
- Async database operations for better performance
- Comprehensive error handling
- Docker support for easy deployment
- Interactive Streamlit UI for chat interaction

## Prerequisites

- Python 3.8+
- MongoDB
- Google Cloud API key for Generative AI
- Docker (optional)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=chat_db
GOOGLE_API_KEY=your_google_api_key
```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd chat-summarization-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Local Development

1. Start MongoDB:
   ```bash
   mongod --dbpath /path/to/data/directory
   ```

2. Run the FastAPI application:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Run the Streamlit UI (in a separate terminal):
   ```bash
   streamlit run app/streamlit_app.py
   ```

The API will be available at `http://localhost:8000`
The Streamlit UI will be available at `http://localhost:8501`

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t chat-summarization-api .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env chat-summarization-api
   ```

3. Run the Streamlit UI (in a separate terminal):
   ```bash
   streamlit run app/streamlit_app.py
   ```

## API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Available Endpoints

#### Chat Operations

1. **Store Chat Messages**
   ```http
   POST /chats
   Content-Type: application/json

   {
     "conversation_id": "string",
     "user_id": "string",
     "message": "string",
     "timestamp": "2024-03-20T10:00:00Z"
   }
   ```

2. **Retrieve Chat Messages**
   ```http
   GET /chats/{conversation_id}
   ```

3. **Summarize Chat**
   ```http
   POST /chats/summarize
   Content-Type: application/json

   {
     "conversation_id": "string"
   }
   ```

4. **Delete Chat**
   ```http
   DELETE /chats/{conversation_id}
   ```

#### User Operations

1. **Get User's Chat History**
   ```http
   GET /users/{user_id}/chats?page=1&limit=10
   ```

## Database Schema

### Chat Message
```json
{
  "conversation_id": "string",
  "user_id": "string",
  "message": "string",
  "timestamp": "datetime",
  "metadata": {
    "platform": "string",
    "message_type": "string"
  }
}
```

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Streamlit UI Features

The Streamlit interface provides an easy-to-use chat interface with the following features:

- User authentication via User ID
- Real-time chat message sending and receiving
- Conversation history display
- Conversation summarization on demand
- New conversation creation
- Sidebar for user settings and controls

To use the Streamlit UI:

1. Start the FastAPI backend server
2. Run the Streamlit application
3. Enter your User ID in the sidebar
4. Start chatting and generating summaries

## Docker Compose Quick Start

1. Copy `.env.example` to `.env` and fill in your secrets:
   ```bash
   cp .env.example .env
   # Edit .env to add your real API keys and secrets
   ```
2. Build and run all services:
   ```bash
   docker compose up --build
   ```
3. Access the API at [http://localhost:8000](http://localhost:8000)
4. Access the UI at [http://localhost:8501](http://localhost:8501)

- The API will connect to MongoDB at `mongo:27017` (inside Docker).
- Data is persisted in a Docker volume (`mongo_data`).

## Project Handoff Checklist

Send the following files to your client:
- `Dockerfile`
- `docker-compose.yml`
- `.env.example` (never send your real secrets)
- All source code (`app/` and project files)
- `requirements.txt`
- `README.md`

**Production Notes:**
- For production, use strong secrets and secure your `.env` file.
- Consider using HTTPS and a managed MongoDB service for reliability and security.
- This setup can be deployed on any cloud VM or Docker host. 