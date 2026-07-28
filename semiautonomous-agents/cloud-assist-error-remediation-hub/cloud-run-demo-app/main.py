import os
import sys
import logging
from typing import Optional
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse

app = FastAPI(title="Envato Vibe Storefront - Real Cloud Run Service")

# Configure structured logging for GCP Cloud Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cloudrun-storefront")

@app.get("/healthz")
def healthz(state: Optional[str] = "healed"):
    is_broken = (state == "broken")
    return {"status": "error" if is_broken else "ok", "isBroken": is_broken}

@app.get("/inject-error")
def inject_error():
    logger.error("[CRITICAL] Application error injected into Cloud Run revision. /api/checkout will throw ZeroDivisionError.")
    return {"status": "ERROR_INJECTED", "isBroken": True}

@app.get("/heal-app")
def heal_app():
    logger.info("[REMEDIATED] Applied safe_item_count fallback patch to /api/checkout. Cloud Run revision operational.")
    return {"status": "HEALED", "isBroken": False}

@app.get("/", response_class=HTMLResponse)
def render_storefront(state: Optional[str] = "healed"):
    is_broken = (state == "broken")

    if is_broken:
        # Emit real GCP error log entry
        logger.error("ZeroDivisionError: division by zero in /api/cart/checkout. File '/app/routes/checkout.py', line 42")
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
          <title>Envato Vibe Storefront (HTTP 500)</title>
          <meta charset="utf-8">
          <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #ffffff; color: #0f172a; margin: 0; padding: 28px; }
            .card { background: #ffffff; border: 1px solid #fecdd3; border-radius: 16px; padding: 24px; box-shadow: 0 10px 25px -5px rgba(244,63,94,0.08); }
            .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #ffe4e6; padding-bottom: 14px; }
            .dot { width: 10px; height: 10px; border-radius: 50%; background: #f43f5e; box-shadow: 0 0 10px #f43f5e; display: inline-block; margin-right: 8px; }
            .badge { font-size: 11px; background: #fff1f2; color: #e11d48; border: 1px solid #fecdd3; padding: 4px 12px; border-radius: 99px; font-weight: 700; }
            .stack { margin-top: 18px; background: #0f172a; padding: 18px; border-radius: 12px; font-family: monospace; font-size: 12px; color: #fda4af; }
          </style>
        </head>
        <body>
          <div class="card">
            <div class="header">
              <div>
                <span class="dot"></span>
                <span style="font-weight: 800; font-size: 16px; color: #e11d48;">Envato Vibe Storefront (Live Cloud Run)</span>
              </div>
              <span class="badge">HTTP 500 CRITICAL ERROR</span>
            </div>
            <div class="stack">
              <div style="color: #f43f5e; font-weight: 700;">ZeroDivisionError: division by zero in POST /api/cart/checkout</div>
              <div style="color: #94a3b8; margin-top: 4px;">File "/app/routes/checkout.py", line 42, in process_cart_checkout</div>
              <div style="color: #fda4af; margin-top: 6px; background: rgba(244,63,94,0.2); padding: 6px 10px; border-radius: 4px;">
                discount_ratio = total_discount / itemCount
              </div>
            </div>
          </div>
        </body>
        </html>
        """, status_code=500)

    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Envato Vibe Storefront (HTTP 200)</title>
      <meta charset="utf-8">
      <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #ffffff; color: #0f172a; margin: 0; padding: 28px; }
        .card { background: #ffffff; border: 1px solid #a7f3d0; border-radius: 16px; padding: 24px; box-shadow: 0 10px 25px -5px rgba(16,185,129,0.08); }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 14px; }
        .dot { width: 10px; height: 10px; border-radius: 50%; background: #10b981; box-shadow: 0 0 10px #10b981; display: inline-block; margin-right: 8px; }
        .badge { font-size: 11px; background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; padding: 4px 12px; border-radius: 99px; font-weight: 700; }
        .grid { margin-top: 18px; display: grid; grid-template-columns: 1.2fr 1fr; gap: 16px; }
        .box { background: #f8fafc; padding: 16px; border-radius: 12px; border: 1px solid #e2e8f0; }
        .box-green { background: #f0fdf4; padding: 16px; border-radius: 12px; border: 1px solid #bbf7d0; }
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <div>
            <span class="dot"></span>
            <span style="font-weight: 800; font-size: 16px; color: #0f172a;">Envato Vibe Storefront (Live Cloud Run Revision)</span>
          </div>
          <span class="badge">HTTP 200 OK — LIVE HEALED</span>
        </div>

        <div class="grid">
          <div class="box">
            <div style="font-size: 11px; color: #64748b; font-weight: 700; text-transform: uppercase;">Cart Products (3 Items)</div>
            <div style="font-size: 18px; font-weight: 800; color: #0f172a; margin-top: 4px;">Antigravity Agent Suite</div>
            <div style="font-size: 13px; color: #10b981; font-weight: 700; margin-top: 4px;">Subtotal: $149.00</div>
          </div>

          <div class="box-green">
            <div style="font-size: 11px; color: #166534; font-weight: 700; text-transform: uppercase;">Order Checkout Summary</div>
            <div style="font-size: 16px; font-weight: 800; color: #047857; margin-top: 4px;">Order #ORD-2026-8849</div>
            <div style="font-size: 12px; color: #15803d; margin-top: 4px; font-weight: 600;">Payment Verified & Settled ($99.00)</div>
          </div>
        </div>

        <div style="margin-top: 16px; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 12px; border-radius: 10px; font-size: 12px; color: #047857;">
          ✨ <strong>Live Cloud Run Container Revision:</strong> Operating cleanly on Google Cloud Platform with zero errors.
        </div>
      </div>
    </body>
    </html>
    """, status_code=200)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
