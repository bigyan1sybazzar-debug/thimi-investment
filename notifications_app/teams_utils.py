import json
import datetime
import urllib.request
import urllib.parse
import urllib.error
from django.conf import settings


def create_microsoft_teams_meeting(subject="Thimi Investment Group General Meeting", start_datetime_str=None, duration_minutes=60):
    """
    Creates an online meeting via Microsoft Graph API and returns the joinWebUrl.
    Uses pure standard library (urllib) - zero external dependencies.

    Required settings / env vars:
      TEAMS_TENANT_ID
      TEAMS_CLIENT_ID
      TEAMS_CLIENT_SECRET
      TEAMS_ORGANIZER_ID (User ID or UserPrincipalName, e.g. admin@yourdomain.com)
    """
    tenant_id = getattr(settings, 'TEAMS_TENANT_ID', '')
    client_id = getattr(settings, 'TEAMS_CLIENT_ID', '')
    client_secret = getattr(settings, 'TEAMS_CLIENT_SECRET', '')
    organizer_id = getattr(settings, 'TEAMS_ORGANIZER_ID', '')

    if not (tenant_id and client_id and client_secret and organizer_id):
        missing = []
        if not tenant_id: missing.append("TEAMS_TENANT_ID")
        if not client_id: missing.append("TEAMS_CLIENT_ID")
        if not client_secret: missing.append("TEAMS_CLIENT_SECRET")
        if not organizer_id: missing.append("TEAMS_ORGANIZER_ID")
        return {
            "success": False,
            "error": "Missing Microsoft Teams credentials in settings/.env: " + ", ".join(missing),
            "help": "Please configure your Azure AD App (TEAMS_TENANT_ID, TEAMS_CLIENT_ID, TEAMS_CLIENT_SECRET, TEAMS_ORGANIZER_ID) in your .env or cPanel environment."
        }

    # 1. Obtain OAuth2 token from Microsoft Entra ID (Azure AD)
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = urllib.parse.urlencode({
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'scope': 'https://graph.microsoft.com/.default'
    }).encode('utf-8')

    try:
        req = urllib.request.Request(token_url, data=token_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        with urllib.request.urlopen(req, timeout=12) as response:
            token_json = json.loads(response.read().decode('utf-8'))
            access_token = token_json.get('access_token')
            if not access_token:
                return {
                    "success": False,
                    "error": "Failed to get access token from Microsoft login."
                }
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        try:
            err_json = json.loads(err_body)
            err_desc = err_json.get('error_description') or err_json.get('error') or err_body
        except Exception:
            err_desc = err_body
        return {
            "success": False,
            "error": f"Microsoft Authentication Failed ({e.code}): {err_desc}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Connection error reaching Microsoft login: {str(e)}"
        }

    # 2. Prepare meeting time
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    if start_datetime_str:
        try:
            clean_str = start_datetime_str.replace(" ", "T")
            if len(clean_str) == 10:  # "YYYY-MM-DD"
                clean_str += "T10:00:00"
            elif len(clean_str) == 16: # "YYYY-MM-DDTHH:MM"
                clean_str += ":00"
            start_dt = datetime.datetime.fromisoformat(clean_str)
            if start_dt.tzinfo is None:
                start_dt = start_dt.replace(tzinfo=datetime.timezone.utc)
        except Exception:
            start_dt = now_utc + datetime.timedelta(hours=1)
    else:
        start_dt = now_utc + datetime.timedelta(hours=1)

    end_dt = start_dt + datetime.timedelta(minutes=duration_minutes)

    meeting_payload = {
        "startDateTime": start_dt.isoformat(),
        "endDateTime": end_dt.isoformat(),
        "subject": subject or "Thimi Investment Group General Meeting",
        "lobbyBypassSettings": {
            "scope": "everyone"
        },
        "allowedPresenters": "everyone"
    }

    # 3. Create online meeting via Microsoft Graph API
    graph_url = f"https://graph.microsoft.com/v1.0/users/{urllib.parse.quote(organizer_id)}/onlineMeetings"
    req_body = json.dumps(meeting_payload).encode('utf-8')
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(graph_url, data=req_body, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=15) as response:
            meeting_json = json.loads(response.read().decode('utf-8'))
            join_url = meeting_json.get('joinWebUrl')

            if join_url:
                return {
                    "success": True,
                    "join_url": join_url,
                    "meeting_id": meeting_json.get('id', ''),
                    "subject": meeting_json.get('subject', subject),
                    "conference_id": meeting_json.get('videoTeleconferenceId', '')
                }
            else:
                return {
                    "success": False,
                    "error": "Microsoft Graph response did not contain a joinWebUrl."
                }
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        try:
            err_json = json.loads(err_body)
            err_msg = err_json.get('error', {}).get('message') or err_body
        except Exception:
            err_msg = err_body
        return {
            "success": False,
            "error": f"Microsoft Graph API Error ({e.code}): {err_msg}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error calling Microsoft Graph API: {str(e)}"
        }
