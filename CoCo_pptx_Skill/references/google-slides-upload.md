---
name: pptx-google-slides-upload
description: Upload & convert a .pptx deck to Google Slides via the Google Drive API. Covers auth setup, upload helper, and post-upload verification.
---

# Google Slides Upload — PPTX → Google Drive → Google Slides

> **This file is a reference companion to SKILL.md.**
> Load this reference ONLY when the user requests Google Slides output.
> The deck is ALWAYS built as .pptx first using the standard skill workflow,
> then uploaded and converted via the Google Drive API.

---

## Overview

Google Drive's API natively converts uploaded .pptx files to Google Slides
format with high fidelity (95%+ formatting preserved). This is far simpler
and more reliable than building slides via the Google Slides REST API.

**Flow**: Build .pptx → Upload to Google Drive with `mimeType` conversion → Return Google Slides URL

---

## Prerequisites

### 1. Install Dependencies

```bash
uv pip install python-pptx google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 2. Google Cloud Project Setup (One-Time)

The user needs a Google Cloud project with the Drive API enabled and OAuth 2.0 credentials.
If the user hasn't set this up, guide them through:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select existing)
3. Enable the **Google Drive API** (`APIs & Services → Library → Google Drive API`)
4. Create **OAuth 2.0 Client ID** credentials (`APIs & Services → Credentials → Create Credentials → OAuth client ID`)
   - Application type: **Desktop app**
   - Download the `credentials.json` file
5. Place `credentials.json` in the working directory (or specify the path)

**IMPORTANT**: Never commit `credentials.json` or `token.json` to version control.

### 3. Authentication Flow

On first run, a browser window opens for the user to authorize access.
A `token.json` file is saved for subsequent runs (auto-refreshes).

---

## Helper Functions — Copy Into Script

### Authentication Helper

```python
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service(credentials_path='credentials.json', token_path='token.json'):
    """Authenticate and return a Google Drive API service object.
    
    First run opens a browser for OAuth consent. Subsequent runs use cached token.
    """
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)
```

### Upload & Convert Helper

```python
def upload_pptx_to_google_slides(pptx_path, title=None, folder_id=None,
                                  credentials_path='credentials.json',
                                  token_path='token.json'):
    """Upload a .pptx file to Google Drive and convert it to Google Slides.
    
    Args:
        pptx_path: Path to the local .pptx file
        title: Presentation title in Google Drive (defaults to filename without extension)
        folder_id: Optional Google Drive folder ID to upload into
        credentials_path: Path to OAuth credentials JSON
        token_path: Path to cached auth token
    
    Returns:
        dict with 'id' (presentation ID), 'url' (Google Slides URL), 'title'
    """
    service = get_drive_service(credentials_path, token_path)
    
    if title is None:
        title = os.path.splitext(os.path.basename(pptx_path))[0]
    
    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.presentation',
    }
    if folder_id:
        file_metadata['parents'] = [folder_id]
    
    media = MediaFileUpload(
        pptx_path,
        mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation',
        resumable=True
    )
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, webViewLink'
    ).execute()
    
    result = {
        'id': file.get('id'),
        'url': file.get('webViewLink'),
        'title': file.get('name'),
    }
    
    print(f"Uploaded to Google Slides: {result['title']}")
    print(f"URL: {result['url']}")
    
    return result
```

---

## Integration Into Build Script

Add the upload step AFTER `prs.save()` and `verify_deck()`:

```python
prs.save(output_path)
print(f"Saved: {output_path}")

result = upload_pptx_to_google_slides(
    output_path,
    title="My Presentation Title",
    folder_id=None,  # or a specific Drive folder ID
)
print(f"\nGoogle Slides URL: {result['url']}")
```

---

## Handling Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `credentials.json` not found | OAuth credentials not downloaded | Guide user through Google Cloud Console setup (see Prerequisites) |
| Browser doesn't open for auth | Running in headless environment | Use `flow.run_console()` instead of `flow.run_local_server()` |
| `token.json` expired / invalid | Refresh token revoked or expired | Delete `token.json` and re-authenticate |
| Formatting differences after conversion | Google Slides doesn't support all PPTX features | Minor differences expected — theme colours, custom shapes, and text layout are preserved. Wave graphics / embedded images convert well. |
| Upload fails with 403 | Drive API not enabled or insufficient scope | Verify Drive API is enabled in Google Cloud Console; check SCOPES includes `drive.file` |
| Want to upload to specific folder | Need folder ID | Get folder ID from the Google Drive URL: `drive.google.com/drive/folders/{FOLDER_ID}` |

### Formatting Conversion Notes

Google Drive's PPTX→Slides converter handles:
- **Well**: Shapes, text boxes, tables, colours, fonts (Arial), images, slide layouts
- **Mostly**: Custom shape fills, line styles, text alignment, bullet hierarchy
- **Limitations**: Some advanced animations, SmartArt, embedded OLE objects, custom fonts not in Google Fonts

The Snowflake template converts well because it uses standard shapes, Arial font, and solid colour fills — all of which Google Slides supports natively.

---

## User Interaction — Asking for Credentials

When the user requests Google Slides output, check for credentials:

```
I'll build the deck as a .pptx first, then upload it to Google Slides.

To upload, I need Google Drive API access. Do you have:
1. A `credentials.json` file from Google Cloud Console? → Tell me the path
2. Not set up yet? → I'll walk you through the 5-minute setup

(If you'd prefer, I can just save the .pptx and you can upload it manually
to Google Drive — it auto-converts to Slides format.)
```

---

## Manual Alternative (No API Setup)

If the user doesn't want to set up the Google API:

1. Save the .pptx as normal
2. Open [Google Drive](https://drive.google.com)
3. Click **New → File upload** → select the .pptx
4. Once uploaded, double-click → it opens as Google Slides
5. Optionally: **File → Save as Google Slides** to convert permanently

This is a perfectly valid workflow and doesn't require any API credentials.

---
