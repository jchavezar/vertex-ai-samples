"""Cloud Run Job entry point — fetch current Amex statement and store in Firestore."""

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone

from credentials import get_amex_credentials, get_gmail_access_token
from browser import download_statement, LoginError, OTPError, DownloadError
from parser import parse_statement_csv
from storage import write_statement

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","name":"%(name)s","level":"%(levelname)s","message":%(message)s}',
)
logger = logging.getLogger("amex-job.main")


async def run() -> None:
    now = datetime.now(timezone.utc)
    period = now.strftime("%Y-%m")

    logger.info(json.dumps({"event": "job_started", "period": period}))

    # 1. Fetch credentials + Gmail token (reuses gworkspace OAuth)
    creds = get_amex_credentials()
    gmail_token = get_gmail_access_token()

    # 2. Login and download CSV
    csv_content = await download_statement(
        username=creds["username"],
        password=creds["code"],
        gmail_access_token=gmail_token,
        period=None,  # latest/current
    )

    # 3. Parse CSV
    statement = parse_statement_csv(csv_content, period)

    # 4. Write to Firestore
    write_statement(statement)

    logger.info(json.dumps({
        "event": "job_completed",
        "period": period,
        "transactions": statement["total_transactions"],
    }))


def main() -> None:
    try:
        asyncio.run(run())
    except (LoginError, OTPError, DownloadError) as e:
        logger.error(json.dumps({"event": "job_failed", "error": str(e)}))
        sys.exit(1)
    except Exception as e:
        logger.error(json.dumps({"event": "job_failed", "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
