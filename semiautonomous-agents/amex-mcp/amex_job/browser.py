"""Playwright browser automation for Amex login and CSV statement download.

OTP extraction uses the Gmail API (via existing gworkspace OAuth tokens).
Includes stealth patches to bypass bot detection on financial sites.
"""

import asyncio
import base64
import json
import logging
import re
import tempfile
import time
from pathlib import Path
from typing import Optional

import requests
from playwright.async_api import async_playwright, Page, BrowserContext

logger = logging.getLogger("amex-job.browser")

# Stealth JS injected before every page load to mask automation signals
STEALTH_JS = """
// Remove webdriver flag
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

// Override plugins to look like a real browser
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5],
});

// Override languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en'],
});

// Override platform
Object.defineProperty(navigator, 'platform', {
    get: () => 'Win32',
});

// Chrome runtime stub
window.chrome = { runtime: {} };

// Override permissions query
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) =>
    parameters.name === 'notifications'
        ? Promise.resolve({ state: Notification.permission })
        : originalQuery(parameters);
"""


class LoginError(Exception):
    pass


class OTPError(Exception):
    pass


class DownloadError(Exception):
    pass


async def _create_stealth_context(playwright) -> tuple:
    """Create a browser + context with stealth settings to bypass bot detection."""
    browser = await playwright.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-infobars",
            "--window-size=1920,1080",
            "--start-maximized",
        ],
    )
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        screen={"width": 1920, "height": 1080},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        locale="en-US",
        timezone_id="America/New_York",
        java_script_enabled=True,
        has_touch=False,
        is_mobile=False,
        color_scheme="light",
    )
    # Inject stealth script before every page load
    await context.add_init_script(STEALTH_JS)
    return browser, context


def _extract_otp_from_gmail(gmail_access_token: str, after_epoch: int = 0) -> str:
    """Extract OTP code from Gmail using the Gmail API.

    Args:
        gmail_access_token: OAuth access token for Gmail API.
        after_epoch: Unix epoch seconds — only consider emails received after
            this timestamp.  Prevents reusing stale OTP codes from earlier
            verification attempts.  When 0, falls back to ``newer_than:5m``.
    """
    logger.info(json.dumps({"event": "otp_extraction_started", "after_epoch": after_epoch}))

    headers = {"Authorization": f"Bearer {gmail_access_token}"}

    query = "from:americanexpress subject:(verification OR code OR security)"
    if after_epoch:
        # Gmail search `after:` accepts epoch seconds and matches on internalDate.
        # Subtract 10s to cover clock skew between Amex mail server and Gmail.
        query += f" after:{after_epoch - 10}"
    else:
        query += " newer_than:5m"

    search_resp = requests.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages",
        headers=headers,
        params={
            "q": query,
            "maxResults": 3,
        },
    )
    search_resp.raise_for_status()
    messages = search_resp.json().get("messages", [])

    if not messages:
        raise OTPError("No Amex verification email found in the last hour")

    msg_id = messages[0]["id"]
    msg_resp = requests.get(
        f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}",
        headers=headers,
        params={"format": "full"},
    )
    msg_resp.raise_for_status()
    msg_data = msg_resp.json()

    payload = msg_data.get("payload", {})

    def _extract_body(part: dict) -> str:
        mime = part.get("mimeType", "")
        if mime in ("text/plain", "text/html") and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
        for sub in part.get("parts", []):
            result = _extract_body(sub)
            if result:
                return result
        return ""

    body_text = _extract_body(payload) or msg_data.get("snippet", "")

    otp_match = re.search(r'\b(\d{6})\b', body_text)
    if not otp_match:
        raise OTPError("Could not find 6-digit OTP in Amex email body")

    logger.info(json.dumps({"event": "otp_extracted"}))
    return otp_match.group(1)


async def _log_page_state(page: Page, step: str) -> None:
    """Log current page URL and title for debugging."""
    try:
        url = page.url
        title = await page.title()
        logger.info(json.dumps({"event": "page_state", "step": step, "url": url, "title": title}))
    except Exception:
        pass


async def _download_csv(page: Page, period: Optional[str] = None) -> str:
    """Download the CSV statement for the given period (or latest)."""
    logger.info(json.dumps({"event": "csv_download_started", "period": period or "latest"}))

    await page.goto(
        "https://global.americanexpress.com/activity/search",
        wait_until="domcontentloaded",
        timeout=30000,
    )
    await page.wait_for_timeout(2000)

    if period:
        try:
            date_picker = page.get_by_role("combobox", name=re.compile(r"period|date|statement", re.IGNORECASE))
            await date_picker.click(timeout=5000)
            await page.wait_for_timeout(1000)
            option = page.get_by_role("option", name=re.compile(period, re.IGNORECASE))
            await option.click(timeout=5000)
            await page.wait_for_timeout(2000)
        except Exception:
            logger.warning(json.dumps({"event": "period_selection_fallback", "period": period}))

    try:
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

    except Exception as e:
        raise DownloadError(f"CSV download failed: {e}")

    if not csv_content.strip():
        raise DownloadError("Downloaded CSV is empty")

    logger.info(json.dumps({
        "event": "csv_downloaded",
        "period": period or "latest",
        "size_bytes": len(csv_content),
    }))
    return csv_content


async def download_statement(
    username: str,
    password: str,
    gmail_access_token: str,
    period: Optional[str] = None,
) -> str:
    """Full automated flow: login to Amex, handle OTP, download CSV."""
    logger.info(json.dumps({"event": "login_started"}))

    async with async_playwright() as p:
        browser, context = await _create_stealth_context(p)
        page = await context.new_page()

        try:
            # Step 1: Navigate directly to login page (skip homepage redirect)
            await page.goto(
                "https://www.americanexpress.com/en-us/account/login",
                wait_until="domcontentloaded",
                timeout=30000,
            )
            await page.wait_for_timeout(3000)
            await _log_page_state(page, "login_page_loaded")

            # Step 2: Fill username — try multiple locator strategies
            user_field = (
                page.get_by_label(re.compile(r"user\s*id|user\s*name|email", re.IGNORECASE))
                .or_(page.locator("#eliloUserID"))
                .or_(page.locator("input[name='UserID']"))
            )
            await user_field.first.wait_for(state="visible", timeout=15000)
            await user_field.first.click()
            await page.wait_for_timeout(500)
            await user_field.first.fill(username)
            logger.info(json.dumps({"event": "username_filled"}))

            # Step 3: Fill password
            pass_field = (
                page.get_by_label(re.compile(r"password", re.IGNORECASE))
                .or_(page.locator("#eliloPassword"))
                .or_(page.locator("input[name='Password']"))
            )
            await pass_field.first.click()
            await page.wait_for_timeout(500)
            await pass_field.first.fill(password)
            logger.info(json.dumps({"event": "password_filled"}))

            # Step 4: Submit login
            submit_btn = page.get_by_role("button", name=re.compile(r"log\s*in|sign\s*in|submit", re.IGNORECASE))
            await submit_btn.first.click(timeout=10000)
            logger.info(json.dumps({"event": "login_submitted"}))
            await page.wait_for_timeout(5000)
            await _log_page_state(page, "after_login_submit")

            # Step 5: Handle two-step verification
            # Amex defaults to push notification, we need to switch to email OTP
            verify_heading = page.get_by_role("heading", name=re.compile(r"verify your identity", re.IGNORECASE))
            try:
                await verify_heading.wait_for(state="visible", timeout=15000)
                otp_detected = True
                logger.info(json.dumps({"event": "two_step_verification_detected"}))
            except Exception:
                otp_detected = False

            if otp_detected:
                # Record epoch BEFORE triggering OTP email so we can filter out stale codes
                otp_trigger_epoch = int(time.time())

                # Step 5a: Click "Change verification method" to see all options
                change_method_btn = page.get_by_role("button", name=re.compile(r"change.*verification.*method", re.IGNORECASE))
                try:
                    await change_method_btn.click(timeout=10000)
                    await page.wait_for_timeout(3000)
                    logger.info(json.dumps({"event": "change_verification_method_clicked"}))
                except Exception:
                    logger.warning(json.dumps({"event": "change_method_button_not_found"}))

                # Step 5b: Select "One-time password (email)" option — triggers Amex to send email
                email_otp_btn = page.get_by_role("button", name=re.compile(r"one.time.*password.*email", re.IGNORECASE))
                try:
                    await email_otp_btn.click(timeout=10000)
                    await page.wait_for_timeout(3000)
                    logger.info(json.dumps({"event": "email_otp_selected"}))
                except Exception:
                    raise OTPError("Could not select email OTP verification method")

                # Step 5c: Wait for OTP input field and extract code from Gmail
                otp_field = page.get_by_role("textbox", name=re.compile(r"one.time.*password", re.IGNORECASE))
                await otp_field.wait_for(state="visible", timeout=15000)

                # Wait 15s for the OTP email to arrive in Gmail
                await page.wait_for_timeout(15000)

                # Extract OTP — only look for emails arriving AFTER we triggered the OTP
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
                await _log_page_state(page, "after_otp_submit")

            # Step 6: Handle "Add This Device" prompt — skip it
            not_now_btn = page.get_by_role("button", name=re.compile(r"not now", re.IGNORECASE))
            try:
                await not_now_btn.wait_for(state="visible", timeout=10000)
                await not_now_btn.click(timeout=5000)
                await page.wait_for_timeout(5000)
                logger.info(json.dumps({"event": "add_device_skipped"}))
            except Exception:
                pass  # Device prompt may not appear

            # Step 7: Verify login — check URL pattern
            await page.wait_for_timeout(3000)
            await _log_page_state(page, "login_verification")

            current_url = page.url
            login_success = any(pattern in current_url for pattern in [
                "/dashboard",
                "/activity",
                "/summary",
                "/account/home",
                "/myca",
            ])

            if not login_success:
                login_success = "/login" not in current_url and "/two-step" not in current_url and "americanexpress.com" in current_url

            if not login_success:
                await _log_page_state(page, "login_failed")
                raise LoginError(f"Login verification failed — still on: {current_url}")

            logger.info(json.dumps({"event": "login_successful"}))

            # Step 8: Download CSV
            csv_content = await _download_csv(page, period)
            return csv_content

        finally:
            await browser.close()
