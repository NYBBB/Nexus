import json
import urllib.request
import re
import sys
import os
from datetime import datetime, timedelta, timezone, date

# Add Config Utils
try:
    from config_utils import load_config
except ImportError:
    import config_utils
    load_config = config_utils.load_config

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Get local timezone (best effort)
try:
    LOCAL_TZ = datetime.now().astimezone().tzinfo
except:
    # Fallback to UTC if something is very wrong
    LOCAL_TZ = timezone.utc

def get_config_calendars():
    cfg = load_config()
    cals = cfg.get("calendar_urls", [])
    if isinstance(cals, str):
        cals = [c.strip() for c in cals.split(',') if c.strip()]
    normalized = []
    for item in cals:
        if isinstance(item, str):
            normalized.append({"url": item})
        elif isinstance(item, dict) and 'url' in item:
            normalized.append(item)
    return normalized

def get_ics_content(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def parse_dt(dt_str):
    """Parse ICS datetime string to aware datetime object."""
    # Formats: YYYYMMDDThhmmssZ (UTC), YYYYMMDDThhmmss (Local/Floating), YYYYMMDD (Date)
    if not dt_str: return None
    
    # Handle Date only (All day)
    if len(dt_str) == 8 and 'T' not in dt_str:
        try:
            d = datetime.strptime(dt_str, "%Y%m%d").date()
            # Convert to midnight local time for comparison
            return datetime.combine(d, datetime.min.time()).replace(tzinfo=LOCAL_TZ)
        except: return None

    try:
        if 'Z' in dt_str:
            dt_utc = datetime.strptime(dt_str.replace('Z', ''), "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
            return dt_utc.astimezone(LOCAL_TZ)
        else:
            # Floating time: Assume it's in the local timezone (or event's TZID which we largely ignore for simplicity)
            dt = datetime.strptime(dt_str, "%Y%m%dT%H%M%S")
            return dt.replace(tzinfo=LOCAL_TZ)
    except ValueError:
        return None

def parse_rrule(rrule_str):
    params = {}
    for part in rrule_str.split(';'):
        if '=' in part:
            k, v = part.split('=', 1)
            params[k] = v
    return params

def expand_recurring(event, start_range, end_range):
    """Expand RRULE for DAILY and WEEKLY."""
    instances = []
    rrule = event.get('RRULE')
    dtstart = event.get('DTSTART')
    exdates = event.get('EXDATE', []) # List of datetime objects
    
    if not rrule or not dtstart:
        return instances
        
    params = parse_rrule(rrule)
    freq = params.get('FREQ')
    until_str = params.get('UNTIL')
    until_dt = parse_dt(until_str) if until_str else None
    
    # Simple Logic: Iterate day by day from start_range to end_range
    # Check if day matches RRULE rules
    
    # Optimization: Start checking from whichever is later: event start or query start
    current = max(dtstart, start_range).replace(hour=dtstart.hour, minute=dtstart.minute, second=dtstart.second)
    # Backtrack 1 day to be safe with timezones
    current -= timedelta(days=1)
    
    while current <= end_range:
        if current >= start_range:
            # Check UNTIL
            if until_dt and current > until_dt:
                break
            
            # Check EXDATE (Simple date match)
            is_excluded = False
            for ex in exdates:
                if ex.date() == current.date():
                    is_excluded = True
                    break
            if is_excluded:
                current += timedelta(days=1)
                continue

            match = False
            if freq == 'DAILY':
                match = True
            elif freq == 'WEEKLY':
                byday = params.get('BYDAY', '').split(',')
                # Convert MO,TU to 0,1
                day_map = {'MO': 0, 'TU': 1, 'WE': 2, 'TH': 3, 'FR': 4, 'SA': 5, 'SU': 6}
                target_days = [day_map[d] for d in byday if d in day_map]
                
                # If no BYDAY, implies same day of week as start
                if not target_days:
                    target_days = [dtstart.weekday()]
                    
                if current.weekday() in target_days:
                    match = True
            
            # TODO: Add MONTHLY if needed, but usually rare for class schedules
            
            if match:
                instances.append({
                    'summary': event.get('SUMMARY', 'Busy'),
                    'start': current,
                    'is_recurring': True
                })
                
        current += timedelta(days=1)
        
    return instances

def main():
    cals = get_config_calendars()
    if not cals:
        print("No calendars configured. Use nexus_config to add calendar_urls.")
        return
    
    now = datetime.now(LOCAL_TZ)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_end = today_start + timedelta(days=2) - timedelta(seconds=1)
    
    all_events = []

    print(f"Current Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}\n")

    for cal in cals:
        raw = get_ics_content(cal['url'])
        if not raw:
            continue
            
        chunks = raw.split('BEGIN:VEVENT')
        for chunk in chunks[1:]:
            lines = chunk.splitlines()
            event = {'EXDATE': []}
            for line in lines:
                if line.startswith('SUMMARY:'):
                    event['SUMMARY'] = line[8:]
                elif line.startswith('DTSTART'):
                    val = line.split(':', 1)[1]
                    event['DTSTART'] = parse_dt(val)
                elif line.startswith('RRULE:'):
                    event['RRULE'] = line[6:]
                elif line.startswith('EXDATE'):
                    # EXDATE;TZID=...:20231010T000000
                    try:
                        val = line.split(':', 1)[1]
                        ex_dt = parse_dt(val)
                        if ex_dt: event['EXDATE'].append(ex_dt)
                    except: pass
            
            if 'DTSTART' not in event or not event['DTSTART']:
                continue
                
            # 1. Single Event
            if 'RRULE' not in event:
                start = event['DTSTART']
                if today_start <= start <= tomorrow_end:
                    all_events.append({
                        'summary': event.get('SUMMARY', 'Busy'),
                        'start': start,
                        'is_recurring': False
                    })
            # 2. Recurring
            else:
                instances = expand_recurring(event, today_start, tomorrow_end)
                all_events.extend(instances)

    all_events.sort(key=lambda x: x['start'])

    current_day = None
    for evt in all_events:
        day_str = evt['start'].strftime('%Y-%m-%d (%A)')
        if day_str != current_day:
            print(f"\n📅 {day_str}")
            current_day = day_str
            
        time_str = evt['start'].strftime('%H:%M')
        status = ""
        if evt['start'].date() == now.date():
            if evt['start'] < now:
                status = "[STARTED/DONE]"
            else:
                status = "[UPCOMING]"
        
        print(f"  {time_str} - {evt['summary']} {status}")

if __name__ == "__main__":
    main()
