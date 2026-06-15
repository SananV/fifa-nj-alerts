import json, urllib.request, urllib.error, os, sys
from datetime import datetime, timezone, timedelta

api_key = os.environ.get('ANTHROPIC_API_KEY', '').strip()
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY secret is not set.")
    sys.exit(1)

print(f"API key found, last 4: ...{api_key[-4:]}")

prompt = (
    "You are a sports data assistant. Generate the complete FIFA World Cup 2026 schedule as a JSON array.\n\n"
    "Include ALL matches: all group stage games, round of 32, round of 16, quarter-finals, semi-finals, third place, and the final.\n\n"
    "All times must be in Eastern Time (EDT = UTC-4). Use offset -04:00 in ISO datetime strings.\n\n"
    "MetLife Stadium in East Rutherford, NJ is the New York/New Jersey venue. Label it as: MetLife Stadium, East Rutherford, NJ\n\n"
    "Other venues include: ATT Stadium (Arlington TX), SoFi Stadium (Inglewood CA), "
    "Levis Stadium (Santa Clara CA), Rose Bowl (Pasadena CA), Arrowhead Stadium (Kansas City MO), "
    "Gillette Stadium (Foxborough MA), Lincoln Financial Field (Philadelphia PA), "
    "Hard Rock Stadium (Miami FL), Mercedes-Benz Stadium (Atlanta GA), NRG Stadium (Houston TX), "
    "Estadio Azteca (Mexico City), Estadio BBVA (Monterrey), Estadio Akron (Guadalajara), "
    "BC Place (Vancouver), BMO Field (Toronto).\n\n"
    "Return ONLY a valid JSON array. Start with [ and end with ]. No markdown, no backticks, no extra text.\n\n"
    "Each object must have exactly these fields:\n"
    '{"scheduled":"2026-06-11T12:00:00-04:00","home_team":{"name":"Mexico"},"away_team":{"name":"TBD"},'
    '"venue":{"name":"ATT Stadium, Arlington, TX"},"tournament_round":{"name":"Group Stage - Group A"},'
    '"phase":"group","status":"scheduled"}\n\n'
    "Return the full JSON array now."
)

payload = json.dumps({
    "model": "claude-sonnet-4-6",
    "max_tokens": 8000,
    "messages": [{"role": "user", "content": prompt}]
}).encode()

req = urllib.request.Request(
    "https://api.anthropic.com/v1/messages",
    data=payload,
    headers={
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"HTTP {e.code} from Anthropic API: {body}")
    sys.exit(1)
except Exception as e:
    print(f"Request failed: {e}")
    sys.exit(1)

print(f"API call succeeded. Stop reason: {data.get('stop_reason')}")

full_text = ''.join(
    block.get('text', '') for block in data.get('content', [])
    if block.get('type') == 'text'
)

print(f"Response length: {len(full_text)} chars")

clean = full_text.replace('```json', '').replace('```', '').strip()
start = clean.find('[')
end = clean.rfind(']')

if start == -1 or end == -1:
    print("ERROR: No JSON array found.")
    print("First 500 chars:", full_text[:500])
    sys.exit(1)

try:
    matches = json.loads(clean[start:end+1])
except json.JSONDecodeError as e:
    print(f"JSON parse error: {e}")
    print("JSON attempt (first 500):", clean[start:start+500])
    sys.exit(1)

print(f"Parsed {len(matches)} matches successfully.")

est = timezone(timedelta(hours=-4))
output = {
    "generated_at": datetime.now(est).isoformat(),
    "match_count": len(matches),
    "matches": matches
}

with open("schedule.json", "w") as f:
    json.dump(output, f, indent=2)

print("schedule.json written successfully.")
