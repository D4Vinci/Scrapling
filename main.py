import uvicorn
import argparse

def start_server(host="0.0.0.0", port=8000):
    """
    Entry point to launch the Scrapling Stealth API.
    """
    print("="*50)
    print("🚀 SCALING STEALTH API: LOADING")
    print("="*50)
    print(f"Server is starting on http://{host}:{port}")
    print("Use /docs for the API Documentation.")
    
    # Run the FastAPI app defined in api.py
    uvicorn.run("api:app", host=host, port=port, reload=False) # Reload=False because of the Windows event loop logic

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the Scrapling API Server.")
    parser.add_argument("--host", default="0.0.0.0", help="Address to listen on (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    
    args = parser.parse_args()
    start_server(host=args.host, port=args.port)
