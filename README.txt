SchoolBot Project Structure

- scripts/build_faiss_index.py: Converts .txt files into searchable chunks and builds FAISS index.
- scripts/chatbot.py: Loads model, chunks, metadata, and handles semantic search.
- scripts/intent_handler.py: Contains intent detection logic and predefined responses.
- scripts/main.py: Command-line interface for users to chat with SchoolBot.
- school_data/: Place all .txt files from PDF regulations here.
- faiss_index.index / faiss_metadata.json: Auto-generated when you run build_faiss_index.py

Usage:
1. Activate your virtual environment: 
   llama-env\Scripts\activate

2. Build or update your FAISS index:
   python scripts/build_faiss_index.py

3. Run the chatbot:
   python main.py

4. To reload the backend/ Frontend
   npm run start-all

5. To export_unknown_queries.py
   python export_unknown_queries.py
