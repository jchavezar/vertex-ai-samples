"""One-time backfill script — download all historical Amex statements.

Run locally once:
    python backfill.py
"""

import asyncio
import json
import logging
import random
import re
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Page

from amex_job.credentials import get_amex_credentials, get_gmail_access_token
from amex_job.browser import LoginError, OTPError, _extract_otp_from_gmail
from amex_job.parser import parse_statement_csv
from amex_job.storage import write_statement, statement_exists

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","name":"%(name)s","level":"%(levelname)s","message":%(message)s}',
)
logger = logging.getLogger("amex-job.backfill")


async def _login(page: Page, username: str, password: str, gmail_access_token: str) -> None:
    """Perform the Amex login flow with Gmail API OTP extraction."""
    await page.goto("https://www.americanexpress.com", wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(2000)

    login_btn = page.get_by_role("link", name=re.compile(r"log\s*in", re.IGNORECASE)).or_(
        page.get_by_role("button", name=re.compile(r"log\s*in", re.IGNORECASE))
    )
    await login_btn.first.click(timeout=10000)
    await page.wait_for_load_state("domcontentloaded")
    await page.wait_for_timeout(2000)

    user_field = page.get_by_label(re.compile(r"user\s*id|user\s*name|email", re.IGNORECASE))
    await user_field.first.fill(username)

    pass_field = page.get_by_label(re.compile(r"password", re.IGNORECASE))
    await pass_field.first.fill(password)

    submit_btn = page.get_by_role("button", name=re.compile(r"log\s*in|sign\s*in|submit", re.IGNORECASE))
    await submit_btn.first.click(timeout=10000)
    await page.wait_for_timeout(5000)

    # Handle two-step verification — Amex defaults to push notification
    verify_heading = page.get_by_role("heading", name=re.compile(r"verify your identity", re.IGNORECASE))
    try:
        await verify_heading.wait_for(state="visible", timeout=15000)
        logger.info(json.dumps({"event": "two_step_verification_detected"}))

        # Record epoch BEFORE triggering OTP email
        otp_trigger_epoch = int(time.time())

        # Switch from push notification to email OTP
        change_method_btn = page.get_by_role("button", name=re.compile(r"change.*verification.*method", re.IGNORECASE))
        await change_method_btn.click(timeout=10000)
        await page.wait_for_timeout(3000)

        email_otp_btn = page.get_by_role("button", name=re.compile(r"one.time.*password.*email", re.IGNORECASE))
        await email_otp_btn.click(timeout=10000)
        await page.wait_for_timeout(3000)

        # Fill OTP from Gmail
        otp_field = page.get_by_role("textbox", name=re.compile(r"one.time.*password", re.IGNORECASE))
        await otp_field.wait_for(state="visible", timeout=15000)
        await page.wait_for_timeout(15000)

        otp_code = None
        for attempt in range(3):
            try:
                otp_code = _extract_otp_from_gmail(gmail_access_token, after_epoch=otp_trigger_epoch)
                break
            except OTPError:
                if attempt < 2:
                    wait_secs = 15 * (attempt + 1)
                    logger.warning(json.dumps({"event": "otp_retry", "attempt": attempt + 1, "wait_secs": wait_secs}))
                    await page.wait_for_timeout(wait_secs * 1000)
                else:
                    raise

        await otp_field.fill(otp_code)
        verify_btn = page.get_by_role("button", name=re.compile(r"^verify$", re.IGNORECASE))
        await verify_btn.click(timeout=10000)
        await page.wait_for_timeout(5000)
        logger.info(json.dumps({"event": "otp_submitted"}))
    except Exception:
        pass  # No OTP challenge

    # Skip "Add This Device" prompt if it appears
    not_now_btn = page.get_by_role("button", name=re.compile(r"not now", re.IGNORECASE))
    try:
        await not_now_btn.wait_for(state="visible", timeout=10000)
        await not_now_btn.click(timeout=5000)
        await page.wait_for_timeout(5000)
    except Exception:
        pass

    # Verify login — check we reached the dashboard
    current_url = page.url
    if "/dashboard" in current_url or "/activity" in current_url or "/myca" in current_url:
        logger.info(json.dumps({"event": "login_successful"}))
    elif "/login" not in current_url and "/two-step" not in current_url:
        logger.info(json.dumps({"event": "login_successful", "url": current_url}))
    else:
        raise LoginError(f"Login verification failed — still on: {current_url}")


async def _discover_periods(page: Page) -> list[str]:
    """Discover available statement periods from the Amex statements page."""
    await page.goto(
        "https://global.americanexpress.com/activity/search",
        wait_until="domcontentloaded",
        timeout=30000,
    )
    await page.wait_for_timeout(3000)

    date_picker = page.get_by_role("combobox", name=re.compile(r"period|date|statement", re.IGNORECASE))
    try:
        await date_picker.click(timeout=10000)
        await page.wait_for_timeout(1000)
    except Exception:
        logger.warning(json.dumps({"event": "period_selector_not_found"}))
        return []

    options = page.get_by_role("option")
    count = await options.count()

    periods = []
    for i in range(count):
        text = await options.nth(i).inner_text()
        match = re.search(r'(\d{4})-(\d{2})', text)
        if match:
            periods.append(f"{match.group(1)}-{match.group(2)}")
            continue
        match = re.search(r'(\w+)\s+(\d{4})', text)
        if match:
            from datetime import datetime as dt
            try:
                d = dt.strptime(f"{match.group(1)} {match.group(2)}", "%B %Y")
                periods.append(d.strftime("%Y-%m"))
            except ValueError:
                pass

    await page.keyboard.press("Escape")
    periods.sort()
    logger.info(json.dumps({"event": "periods_discovered", "count": len(periods)}))
    return periods


async def _download_period_csv(page: Page, period: str) -> Optional[str]:
    """Download CSV for a specific period. Returns CSV content or None on failure."""
    try:
        await page.goto(
            "https://global.americanexpress.com/activity/search",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        await page.wait_for_timeout(2000)

        date_picker = page.get_by_role("combobox", name=re.compile(r"period|date|statement", re.IGNORECASE))
        await date_picker.click(timeout=5000)
        await page.wait_for_timeout(1000)

        option = page.get_by_role("option", name=re.compile(period, re.IGNORECASE))
        await option.click(timeout=5000)
        await page.wait_for_timeout(2000)

        download_btn = page.get_by_role("button", name=re.compile(r"download|export", re.IGNORECASE))
        await download_btn.first.click(timeout=10000)
        await page.wait_for_timeout(1000)

        csv_option = page.get_by_role("menuitem", name=re.compile(r"csv", re.IGNORECASE)).or_(
            page.get_by_role("option", name=re.compile(r"csv", re.IGNORECASE))
        ).or_(
            page.get_by_text(re.compile(r"\.csv|comma", re.IGNORECASE))
        )

        async with page.expect_download(timeout=30000) as download_info:
            await csv_option.first.click(timeout=5000)

        download = await download_info.value
        dest = Path(tempfile.mkdtemp()) / download.suggested_filename
        await download.save_as(dest)
        csv_content = dest.read_text()
        dest.unlink(missing_ok=True)
        return csv_content

    except Exception as e:
        logger.error(json.dumps({"event": "period_download_failed", "period": period, "error": str(e)}))
        return None


async def run_backfill() -> None:
    logger.info(json.dumps({"event": "backfill_started"}))

    creds = get_amex_credentials()
    gmail_token = get_gmail_access_token()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await _login(page, creds["username"], creds["code"], gmail_token)

            periods = await _discover_periods(page)
            if not periods:
                logger.warning(json.dumps({"event": "no_periods_found"}))
                return

            for i, period in enumerate(periods):
                if statement_exists(period):
                    logger.info(json.dumps({"event": "period_skipped", "period": period, "reason": "exists"}))
                    continue

                logger.info(json.dumps({"event": "downloading_period", "period": period, "index": i + 1, "total": len(periods)}))

                csv_content = await _download_period_csv(page, period)
                if csv_content:
                    statement = parse_statement_csv(csv_content, period)
                    write_statement(statement)
                    logger.info(json.dumps({
                        "event": "period_stored",
                        "period": period,
                        "transactions": statement["total_transactions"],
                    }))

                delay = random.uniform(10, 30)
                logger.info(json.dumps({"event": "delay", "seconds": round(delay, 1)}))
                await page.wait_for_timeout(int(delay * 1000))

        finally:
            await browser.close()

    logger.info(json.dumps({"event": "backfill_completed"}))


if __name__ == "__main__":
    asyncio.run(run_backfill())
