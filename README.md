# BoxGPT

BoxGPT is a FastAPI-backed AI chat workspace with conversation history, Gemini model selection, document uploads, web search, memory, and calculator tools.

## Run locally

1. Create and activate a Python 3.11 environment, then install the backend requirements:

   ```powershell
   uv venv --python 3.11
   .\.venv\Scripts\Activate.ps1
   uv pip install -r requirements.txt
   ```

2. Copy `.env-sample` to `.env` and add the API keys used by the backend.

3. Start the FastAPI server from the `BoxGPT` directory:

   ```powershell
   python app.py
   ```

   The API runs at `http://localhost:8080`.

4. In a second terminal, start the React frontend from the sibling `frontend` directory:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

   Open the Vite URL printed in the terminal. Its `/chat`, `/conversations`, `/history`, and `/upload` requests are proxied to FastAPI. Frontend requests are centralized in `frontend/src/apiEndpoint.js`.

   For a frontend hosted on a different origin, set `VITE_API_BASE_URL` to the FastAPI base URL before building.

## Serve the built frontend through FastAPI

From the sibling `frontend` directory, build the React app with `npm run build`. Then start FastAPI from the `BoxGPT` directory; the app serves `../frontend/dist` at `/` and its assets from `/assets`.
