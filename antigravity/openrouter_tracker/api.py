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
    Triggers the scraper and updates BigQuery synchronously.
    Keeps HTTP connection open to guarantee Cloud Run preserves CPU execution until complete.
    """
    print("Triggering OpenRouter stats scrape batch stream synchronous...")
    await tracker.main()
    return {"status": "Scrape completed successfully and saved to BigQuery."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
