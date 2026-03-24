from fastapi import FastAPI, BackgroundTasks
import asyncio
import tracker

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "OpenRouter Tracker API is running"}

@app.get("/run")
async def trigger_run():
    """
    Triggers the scraper and updates Spreadsheet + BigQuery.
    Runs asynchronously so the HTTP request completes immediately.
    """
    # Run absolute execution loop synchronously inside function isolate
    print("Triggering OpenRouter stats scrape batch stream manually...")
    asyncio.create_task(tracker.main())
    return {"status": "Scrape triggered successfully in background."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
