import tkinter as tk
from tkinter import messagebox, scrolledtext
import webbrowser
import requests
import os
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# --- LOAD ENVIRONMENT ---
load_dotenv(override=True)

# --- CONFIGURATION ---
CLIENT_ID = os.getenv("ATLASSIAN_CLIENT_ID")
CLIENT_SECRET = os.getenv("ATLASSIAN_CLIENT_SECRET")
REDIRECT_URI = os.getenv("ATLASSIAN_REDIRECT_URI")
TOKEN_URL = "https://auth.atlassian.com/oauth/token"

if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
    print("❌ Error: Missing configuration in .env file.")
    print("Please ensure ATLASSIAN_CLIENT_ID, ATLASSIAN_CLIENT_SECRET, and ATLASSIAN_REDIRECT_URI are set.")
    exit(1)

# CORRECT SCOPES (Spaces only, no commas)
SCOPES = "read:me read:jira-work read:jira-user write:jira-work manage:jira-project manage:jira-configuration offline_access"

# --- COLORS ---
BG_COLOR = "#ffffff"         # White background
TEXT_COLOR = "#172B4D"       # Dark Text
ACCENT_COLOR = "#0052CC"     # Blue
SUCCESS_COLOR = "#36B37E"    # Green

class OAuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Atlassian Token Generator")
        self.root.geometry("600x750")
        self.root.configure(bg=BG_COLOR)

        # --- STYLES ---
        # Labels: Dark text on white background
        label_style = {"bg": BG_COLOR, "fg": TEXT_COLOR, "font": ("Arial", 12)}
        header_style = {"bg": BG_COLOR, "fg": TEXT_COLOR, "font": ("Arial", 16, "bold")}

        # Buttons: Black text (so it shows on Mac native buttons) and highlight border matches bg
        btn_style = {
            "font": ("Arial", 12, "bold"),
            "fg": "black",
            "highlightbackground": BG_COLOR
        }

        # HEADER
        tk.Label(root, text="Step 1: Authorization", **header_style).pack(pady=(30, 10))

        # INSTRUCTIONS
        tk.Label(root, text="Click below to open your browser.\nLog in and accept permissions.", **label_style).pack()

        # BUTTON 1
        tk.Button(root, text="1. Open Browser & Authorize", command=self.open_browser,
                  bg=ACCENT_COLOR, **btn_style).pack(pady=15, ipadx=10, ipady=5)

        # STEP 2
        tk.Label(root, text="Step 2: Paste the Redirect URL", **header_style).pack(pady=(30, 5))
        tk.Label(root, text="(Copy the full URL from your browser address bar after login\neven if the page says 'Illegal base64' or 'Error')", **label_style).pack()

        # INPUT
        self.url_input = tk.Text(root, height=4, width=60, borderwidth=2, relief="groove",
                                 bg="white", fg="black", insertbackground="black")
        self.url_input.pack(pady=10, padx=20)

        # BUTTON 2
        tk.Button(root, text="2. Exchange for Token", command=self.get_token,
                  bg=SUCCESS_COLOR, **btn_style).pack(pady=15, ipadx=10, ipady=5)

        # OUTPUT
        tk.Label(root, text="Result (Access Token):", font=("Arial", 12, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)

        self.result_output = scrolledtext.ScrolledText(root, height=12, width=60, font=("Consolas", 11),
                                                       bg="#F4F5F7", fg="black", borderwidth=2, relief="sunken")
        self.result_output.pack(pady=10, padx=20)

    def open_browser(self):
        # NOTE: .replace commas isn't needed anymore since SCOPES is fixed above,
        # but kept .replace(' ', '%20') for URL encoding.
        auth_url = (
            f"https://auth.atlassian.com/authorize?"
            f"audience=api.atlassian.com&"
            f"client_id={CLIENT_ID}&"
            f"scope={SCOPES.replace(' ', '%20')}&"
            f"redirect_uri={REDIRECT_URI}&"
            f"state=token-gen-ui&"
            f"response_type=code&"
            f"prompt=consent"
        )
        print(f"Opening: {auth_url}")
        webbrowser.open(auth_url)

    def get_token(self):
        pasted_url = self.url_input.get("1.0", tk.END).strip()

        if not pasted_url:
            messagebox.showerror("Error", "Please paste the URL first!")
            return

        # Extract Code
        try:
            if "http" in pasted_url:
                parsed = urlparse(pasted_url)
                code = parse_qs(parsed.query).get('code')
                if not code:
                    messagebox.showerror("Error", "Could not find 'code=' in the URL.")
                    return
                auth_code = code[0]
            else:
                auth_code = pasted_url
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse URL: {e}")
            return

        # Exchange
        payload = {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": auth_code,
            "redirect_uri": REDIRECT_URI
        }

        try:
            response = requests.post(TOKEN_URL, json=payload)
            response.raise_for_status()
            data = response.json()

            token = data.get("access_token")

            self.result_output.delete("1.0", tk.END)
            self.result_output.insert(tk.END, token)

            # Select all text for easy copying
            self.result_output.tag_add("sel", "1.0", "end")
            self.result_output.focus_set()

        except requests.exceptions.HTTPError as e:
            self.result_output.delete("1.0", tk.END)
            self.result_output.insert(tk.END, f"Error: {e}\nResponse: {response.text}")
            messagebox.showerror("Failed", "Authorization failed. The code might be expired. Try Step 1 again.")

if __name__ == "__main__":
    root = tk.Tk()
    app = OAuthApp(root)
    root.mainloop()