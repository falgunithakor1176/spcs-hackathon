import math
import random
from datetime import datetime, timedelta

# Advanced Mock Data Engine v2.0 - Python Port
# Preserves the same logical rules, seasonal patterns, and deterministic generation

def get_rand():
    # Use python's built-in random, seeded for reproducibility
    return random.random()

# Initialize fixed seed
random.seed(42)

def random_in_range(min_val, max_val):
    return min_val + get_rand() * (max_val - min_val)

def random_item(arr):
    return arr[math.floor(get_rand() * len(arr))]

def jitter(val, spread=0.015):
    return val + (get_rand() - 0.5) * spread * 2

def weighted_pick(items, weights):
    total = sum(weights)
    r = get_rand() * total
    for i, item in enumerate(items):
        r -= weights[i]
        if r <= 0:
            return item
    return items[-1]

def days_in_month(year, month):
    if month == 12:
        return 31
    return (datetime(year, month + 1, 1) - timedelta(days=1)).day

def day_of_week(year, month, day):
    # JS: 0=Sun, 6=Sat. Python: weekday() 0=Mon, 6=Sun
    # To match JS: (python_weekday + 1) % 7
    return (datetime(year, month, day).weekday() + 1) % 7

AREAS = [
  { 'name': 'Naroda',         'lat': 23.0695, 'lng': 72.6415, 'weight': 9, 'zone': 'East'    },
  { 'name': 'Maninagar',      'lat': 22.9970, 'lng': 72.6043, 'weight': 8, 'zone': 'South'   },
  { 'name': 'Bapunagar',      'lat': 23.0530, 'lng': 72.6160, 'weight': 9, 'zone': 'East'    },
  { 'name': 'Asarwa',         'lat': 23.0590, 'lng': 72.6080, 'weight': 8, 'zone': 'East'    },
  { 'name': 'Dariapur',       'lat': 23.0310, 'lng': 72.5960, 'weight': 8, 'zone': 'Central' },
  { 'name': 'Gomtipur',       'lat': 23.0280, 'lng': 72.6300, 'weight': 7, 'zone': 'East'    },
  { 'name': 'Isanpur',        'lat': 22.9845, 'lng': 72.6117, 'weight': 7, 'zone': 'South'   },
  { 'name': 'Nikol',          'lat': 23.0502, 'lng': 72.6525, 'weight': 7, 'zone': 'East'    },
  { 'name': 'Vastral',        'lat': 23.0261, 'lng': 72.6573, 'weight': 6, 'zone': 'East'    },
  { 'name': 'Narol',          'lat': 22.9700, 'lng': 72.6200, 'weight': 5, 'zone': 'South'   },
  { 'name': 'Vatva',          'lat': 22.9600, 'lng': 72.6400, 'weight': 5, 'zone': 'South'   },
  { 'name': 'Ranip',          'lat': 23.0935, 'lng': 72.5617, 'weight': 6, 'zone': 'North'   },
  { 'name': 'Shahibaug',      'lat': 23.0651, 'lng': 72.5899, 'weight': 5, 'zone': 'North'   },
  { 'name': 'Chandkheda',     'lat': 23.1180, 'lng': 72.5908, 'weight': 5, 'zone': 'North'   },
  { 'name': 'Paldi',          'lat': 23.0103, 'lng': 72.5731, 'weight': 5, 'zone': 'South'   },
  { 'name': 'Ellis Bridge',   'lat': 23.0328, 'lng': 72.5716, 'weight': 4, 'zone': 'Central' },
  { 'name': 'Navrangpura',    'lat': 23.0395, 'lng': 72.5613, 'weight': 4, 'zone': 'Central' },
  { 'name': 'Ambavadi',       'lat': 23.0270, 'lng': 72.5519, 'weight': 3, 'zone': 'West'    },
  { 'name': 'Vastrapur',      'lat': 23.0421, 'lng': 72.5301, 'weight': 3, 'zone': 'West'    },
  { 'name': 'Satellite',      'lat': 23.0226, 'lng': 72.5137, 'weight': 3, 'zone': 'West'    },
  { 'name': 'Gota',           'lat': 23.1018, 'lng': 72.5539, 'weight': 3, 'zone': 'North'   },
  { 'name': 'Thaltej',        'lat': 23.0566, 'lng': 72.5058, 'weight': 2, 'zone': 'West'    },
  { 'name': 'Prahlad Nagar',  'lat': 23.0157, 'lng': 72.5106, 'weight': 2, 'zone': 'West'    },
  { 'name': 'Bodakdev',       'lat': 23.0453, 'lng': 72.5164, 'weight': 2, 'zone': 'West'    },
  { 'name': 'Bopal',          'lat': 23.0297, 'lng': 72.4673, 'weight': 2, 'zone': 'West'    },
  { 'name': 'Vejalpur',       'lat': 23.0003, 'lng': 72.5465, 'weight': 3, 'zone': 'South'   },
  { 'name': 'Sarkhej',        'lat': 22.9790, 'lng': 72.4980, 'weight': 3, 'zone': 'South'   },
]

CRIME_TYPES = [
  'Theft', 'Chain Snatching', 'Mobile Theft', 'Vehicle Theft',
  'Robbery', 'Burglary', 'Assault', 'Domestic Violence',
  'Drug Offense', 'Fraud', 'Kidnapping', 'Murder',
  'Eve Teasing', 'Property Dispute', 'Arms Act Violation',
]

CYBER_TYPES = [
  'UPI Fraud', 'Phishing', 'OTP Scam', 'Social Media Fraud',
  'Identity Theft', 'Online Banking Fraud', 'Investment Scam',
  'Job Fraud', 'Lottery Scam', 'Cyberstalking',
]

MONTHLY_MULTIPLIERS = [1.15, 0.88, 1.12, 1.05, 1.00, 0.82, 0.78, 0.83, 0.92, 1.35, 1.25, 1.15]

FESTIVALS = [
  { 'name': 'Uttarayan', 'events': [{'year': 2023, 'month': 1, 'dayStart': 13, 'dayEnd': 15}, {'year': 2024, 'month': 1, 'dayStart': 13, 'dayEnd': 15}, {'year': 2025, 'month': 1, 'dayStart': 13, 'dayEnd': 15}], 'overallMultiplier': 1.9, 'crimeBoosts': { 'Eve Teasing': 4.0, 'Chain Snatching': 3.0, 'Theft': 2.5, 'Mobile Theft': 2.0, 'Assault': 1.5 } },
  { 'name': 'Holi', 'events': [{'year': 2023, 'month': 3, 'dayStart': 7, 'dayEnd': 8}, {'year': 2024, 'month': 3, 'dayStart': 24, 'dayEnd': 25}, {'year': 2025, 'month': 3, 'dayStart': 13, 'dayEnd': 14}], 'overallMultiplier': 1.7, 'crimeBoosts': { 'Assault': 3.0, 'Eve Teasing': 3.5, 'Drug Offense': 2.5, 'Robbery': 1.5 } },
  { 'name': 'Navratri', 'events': [{'year': 2023, 'month': 10, 'dayStart': 15, 'dayEnd': 24}, {'year': 2024, 'month': 10, 'dayStart': 3, 'dayEnd': 12}, {'year': 2025, 'month': 9, 'dayStart': 22, 'dayEnd': 30}], 'overallMultiplier': 2.1, 'crimeBoosts': { 'Eve Teasing': 4.5, 'Chain Snatching': 3.5, 'Theft': 2.5, 'Mobile Theft': 2.5, 'Robbery': 2.0 } },
  { 'name': 'Diwali', 'events': [{'year': 2023, 'month': 11, 'dayStart': 10, 'dayEnd': 14}, {'year': 2024, 'month': 11, 'dayStart': 1, 'dayEnd': 4}, {'year': 2025, 'month': 10, 'dayStart': 20, 'dayEnd': 23}], 'overallMultiplier': 2.0, 'crimeBoosts': { 'Burglary': 4.5, 'Theft': 2.5, 'Robbery': 2.0, 'Vehicle Theft': 2.0, 'Chain Snatching': 2.0 } },
  { 'name': 'New Year', 'events': [{'year': 2023, 'month': 12, 'dayStart': 31, 'dayEnd': 31}, {'year': 2024, 'month': 12, 'dayStart': 31, 'dayEnd': 31}], 'overallMultiplier': 1.8, 'crimeBoosts': { 'Assault': 3.0, 'Eve Teasing': 3.5, 'Drug Offense': 3.0, 'Robbery': 1.8 } },
  { 'name': 'New Year Day', 'events': [{'year': 2024, 'month': 1, 'dayStart': 1, 'dayEnd': 1}, {'year': 2025, 'month': 1, 'dayStart': 1, 'dayEnd': 1}], 'overallMultiplier': 1.6, 'crimeBoosts': { 'Assault': 2.5, 'Eve Teasing': 2.5, 'Drug Offense': 2.5 } },
]

def get_festival_context(year, month, day):
    for fest in FESTIVALS:
        for ev in fest['events']:
            if ev['year'] == year and ev['month'] == month and ev['dayStart'] <= day <= ev['dayEnd']:
                return { 'isFestival': True, 'name': fest['name'], 'multiplier': fest['overallMultiplier'], 'boosts': fest['crimeBoosts'] }
    return { 'isFestival': False, 'name': None, 'multiplier': 1.0, 'boosts': {} }

HOUR_WEIGHTS = {
  'Theft':            [3,3,3,2,1,1,1,2,3,3,3,3,3,2,2,3,3,4,4,4,4,4,4,4],
  'Chain Snatching':  [1,0,0,0,0,0,1,2,5,5,4,3,3,3,3,3,3,5,5,5,4,3,2,1],
  'Mobile Theft':     [1,0,0,0,0,0,1,2,4,5,5,5,5,4,4,4,4,5,5,4,3,2,2,1],
  'Vehicle Theft':    [4,4,5,5,4,3,2,1,1,1,1,1,1,1,2,2,2,2,3,3,4,4,4,4],
  'Robbery':          [2,2,2,2,1,1,1,1,2,2,2,2,2,2,2,2,2,3,4,5,5,5,4,3],
  'Burglary':         [3,4,5,5,4,3,1,1,0,0,0,0,1,3,4,3,2,2,2,2,2,3,3,3],
  'Assault':          [1,1,1,1,0,0,0,1,2,2,2,2,2,2,2,2,2,2,3,4,5,5,5,4],
  'Domestic Violence':[1,1,1,0,0,0,0,1,3,4,3,2,2,2,2,2,2,3,5,5,5,4,3,2],
  'Drug Offense':     [2,3,4,4,3,1,0,0,0,0,0,0,1,1,1,1,1,2,3,4,5,5,5,4],
  'Fraud':            [0,0,0,0,0,0,0,0,2,4,5,5,5,4,4,5,5,5,4,2,1,0,0,0],
  'Kidnapping':       [1,1,0,0,0,0,1,3,4,3,2,2,2,3,4,3,2,2,3,4,3,2,1,1],
  'Murder':           [2,3,3,2,1,0,0,0,0,0,0,0,0,0,1,1,1,1,2,3,4,5,5,4],
  'Eve Teasing':      [0,0,0,0,0,0,0,1,2,2,2,2,2,2,2,2,2,3,5,5,5,5,4,2],
  'Property Dispute': [0,0,0,0,0,0,0,1,3,4,4,4,4,4,4,4,4,4,3,2,1,0,0,0],
  'Arms Act Violation':[1,2,3,3,2,1,0,0,0,0,0,0,0,0,0,0,0,1,2,3,4,4,4,3],
}

def pick_hour(crime_type):
    weights = HOUR_WEIGHTS.get(crime_type)
    if not weights:
        return math.floor(get_rand() * 24)
    return weighted_pick(list(range(24)), weights)

AREA_CRIME_TENDENCIES = {
  'Naroda':        { 'Drug Offense': 3.0, 'Robbery': 2.5, 'Assault': 2.5, 'Arms Act Violation': 3.0, 'Murder': 2.5 },
  'Maninagar':     { 'Chain Snatching': 2.5, 'Vehicle Theft': 2.0, 'Theft': 1.8, 'Robbery': 1.5 },
  'Bapunagar':     { 'Robbery': 2.2, 'Chain Snatching': 2.0, 'Assault': 1.8, 'Drug Offense': 1.5 },
  'Asarwa':        { 'Drug Offense': 2.5, 'Assault': 2.2, 'Robbery': 1.8, 'Arms Act Violation': 1.5 },
  'Dariapur':      { 'Theft': 2.5, 'Property Dispute': 3.0, 'Drug Offense': 2.0, 'Chain Snatching': 1.8 },
  'Gomtipur':      { 'Vehicle Theft': 2.5, 'Burglary': 2.0, 'Robbery': 1.8 },
  'Isanpur':       { 'Assault': 2.0, 'Domestic Violence': 2.2, 'Robbery': 1.5 },
  'Nikol':         { 'Robbery': 2.5, 'Assault': 2.0, 'Chain Snatching': 1.8 },
  'Vastral':       { 'Chain Snatching': 2.2, 'Robbery': 2.0, 'Vehicle Theft': 1.8 },
  'Narol':         { 'Vehicle Theft': 2.5, 'Robbery': 2.0, 'Burglary': 1.8 },
  'Vatva':         { 'Burglary': 2.5, 'Arms Act Violation': 2.0, 'Vehicle Theft': 2.0 },
  'Ranip':         { 'Drug Offense': 1.8, 'Theft': 1.5, 'Chain Snatching': 1.5 },
  'Shahibaug':     { 'Theft': 1.5, 'Mobile Theft': 1.5, 'Chain Snatching': 1.5 },
  'Chandkheda':    { 'Fraud': 2.0, 'Mobile Theft': 1.8, 'Theft': 1.5 },
  'Paldi':         { 'Theft': 1.5, 'Mobile Theft': 1.5, 'Eve Teasing': 1.5 },
  'Satellite':     { 'Burglary': 2.5, 'Vehicle Theft': 2.5, 'Fraud': 2.0, 'Mobile Theft': 1.5 },
  'Bodakdev':      { 'Vehicle Theft': 3.0, 'Burglary': 2.5, 'Fraud': 2.5, 'Mobile Theft': 1.5 },
  'Prahlad Nagar': { 'Burglary': 2.5, 'Vehicle Theft': 2.5, 'Fraud': 2.2 },
  'Bopal':         { 'Burglary': 2.0, 'Vehicle Theft': 2.0, 'Theft': 1.3 },
  'Navrangpura':   { 'Fraud': 2.5, 'Mobile Theft': 2.0, 'Eve Teasing': 1.5 },
  'Vastrapur':     { 'Vehicle Theft': 2.0, 'Fraud': 2.0, 'Burglary': 1.8 },
  'Thaltej':       { 'Vehicle Theft': 2.0, 'Burglary': 1.8, 'Fraud': 1.8 },
}

BASE_SEVERITY_PROBS = {
  'Murder':           [0.95, 0.05, 0.00, 0.00],
  'Kidnapping':       [0.60, 0.35, 0.05, 0.00],
  'Arms Act Violation':[0.30, 0.50, 0.18, 0.02],
  'Robbery':          [0.20, 0.55, 0.20, 0.05],
  'Assault':          [0.10, 0.40, 0.35, 0.15],
  'Burglary':         [0.10, 0.35, 0.40, 0.15],
  'Drug Offense':     [0.06, 0.30, 0.44, 0.20],
  'Fraud':            [0.05, 0.25, 0.45, 0.25],
  'Vehicle Theft':    [0.03, 0.20, 0.50, 0.27],
  'Chain Snatching':  [0.06, 0.30, 0.44, 0.20],
  'Domestic Violence':[0.08, 0.35, 0.40, 0.17],
  'Theft':            [0.01, 0.10, 0.35, 0.54],
  'Mobile Theft':     [0.01, 0.08, 0.30, 0.61],
  'Eve Teasing':      [0.02, 0.15, 0.45, 0.38],
  'Property Dispute': [0.02, 0.10, 0.35, 0.53],
}

def determine_severity(crime_type, hour, day_of_week, is_festival):
    probs = BASE_SEVERITY_PROBS.get(crime_type, [0.05, 0.20, 0.45, 0.30])
    c, h, m, l = probs

    is_night = hour >= 22 or hour <= 4
    if is_night:
        c = min(1, c * 1.6)
        h = min(1, h * 1.3)
        t = c + h + m + l
        c, h, m, l = c/t, h/t, m/t, l/t

    if is_festival:
        c = min(1, c * 1.35)
        h = min(1, h * 1.25)
        t = c + h + m + l
        c, h, m, l = c/t, h/t, m/t, l/t

    is_weekend = day_of_week == 0 or day_of_week == 6
    if is_weekend and crime_type in ['Assault', 'Eve Teasing', 'Drug Offense']:
        h = min(1, h * 1.4)
        t = c + h + m + l
        c, h, m, l = c/t, h/t, m/t, l/t

    return weighted_pick(['Critical', 'High', 'Medium', 'Low'], [c, h, m, l])

def get_area_temporal_weight(area_name, year, month):
    area_dict = next((a for a in AREAS if a['name'] == area_name), None)
    base = area_dict['weight'] if area_dict else 5
    multiplier = 1.0

    if area_name in ['Narol', 'Vatva'] and ((year == 2024 and month >= 6) or year == 2025):
        multiplier *= 1.6
    if area_name == 'Chandkheda' and ((year == 2024 and month >= 8) or year == 2025):
        multiplier *= 0.55
    if area_name == 'Dariapur' and year == 2025:
        multiplier *= 0.72
    if area_name == 'Naroda' and year >= 2024:
        multiplier *= 1.2
    if area_name == 'Maninagar' and year == 2025:
        multiplier *= 0.80
    if area_name == 'Bapunagar' and year == 2025:
        multiplier *= 1.25
    if area_name in ['Satellite', 'Bodakdev'] and year >= 2024:
        multiplier *= 1.35

    return base * multiplier

def pick_crime_type(area_name, hour, dow, festival_boosts):
    is_weekend = dow == 0 or dow == 6
    is_night = hour >= 21 or hour <= 5
    is_morning = 7 <= hour <= 10
    is_evening = 17 <= hour <= 21
    area_tend = AREA_CRIME_TENDENCIES.get(area_name, {})

    weights = []
    for type_ in CRIME_TYPES:
        w = 1.0
        w *= area_tend.get(type_, 1.0)
        w *= festival_boosts.get(type_, 1.0)
        
        hw = HOUR_WEIGHTS.get(type_)
        if hw:
            w *= (hw[hour] + 0.5) / 3.5

        if is_weekend:
            if type_ in ['Assault','Drug Offense','Eve Teasing','Robbery']: w *= 1.6
            if type_ in ['Fraud','Property Dispute']: w *= 0.6
        else:
            if type_ in ['Fraud','Chain Snatching','Mobile Theft']: w *= 1.4
            if type_ in ['Assault','Eve Teasing']: w *= 0.75

        if is_night:
            if type_ in ['Burglary','Robbery','Murder','Drug Offense','Vehicle Theft','Arms Act Violation']: w *= 2.0
            if type_ in ['Fraud','Property Dispute','Mobile Theft']: w *= 0.2

        if is_morning and type_ in ['Chain Snatching','Mobile Theft']: w *= 1.7
        if is_evening and type_ in ['Eve Teasing','Chain Snatching','Theft']: w *= 1.5

        weights.append(max(0.01, w))

    return weighted_pick(CRIME_TYPES, weights)

def generate_realistic_date():
    year = weighted_pick([2023, 2024, 2025], [0.30, 0.38, 0.32])
    month_weights = [w if not (year == 2025 and i >= 6) else 0.01 for i, w in enumerate(MONTHLY_MULTIPLIERS)]
    month = weighted_pick(list(range(1, 13)), month_weights)
    max_day = days_in_month(year, month)
    day = math.floor(get_rand() * max_day) + 1
    dow = day_of_week(year, month, day)
    return {'year': year, 'month': month, 'day': day, 'dow': dow}

def generate_description(type_, area):
    descriptions = {
        'Murder': [f'Homicide case registered in {area}', f'Suspicious death under investigation in {area}'],
        'Kidnapping': [f'Kidnapping/abduction case registered from {area}', f'Missing person report filed from {area}'],
        'Arms Act Violation': [f'Illegal arms recovered in {area}', f'Arms act violation registered in {area}'],
        'Robbery': [f'Armed robbery reported in {area}', f'Cash robbery near {area} ATM/shop'],
        'Burglary': [f'House break-in reported in {area} residential area', f'Commercial establishment burgled in {area}'],
        'Assault': [f'Physical assault case in {area}', f'Victim assaulted near {area} by unidentified persons'],
        'Drug Offense': [f'Drug peddling activity detected in {area}', f'Narcotics seized from suspects in {area}'],
        'Fraud': [f'Financial fraud case filed from {area}', f'Cheating case involving cash registered in {area}'],
        'Vehicle Theft': [f'Two-wheeler stolen from {area} parking area', f'Car/bike theft reported in {area}'],
        'Chain Snatching': [f'Gold chain snatching near {area} market', f'Victim\'s jewellery snatched in {area}'],
        'Domestic Violence': [f'Domestic violence complaint from {area}', f'Family dispute escalated in {area}'],
        'Theft': [f'Property theft reported near {area} market', f'Items stolen from {area} residence'],
        'Mobile Theft': [f'Smartphone snatched/stolen in {area}', f'Mobile phone theft reported from {area}'],
        'Eve Teasing': [f'Eve teasing / harassment complaint near {area}', f'Verbal/physical harassment reported in {area}'],
        'Property Dispute': [f'Property encroachment complaint from {area}', f'Land dispute case filed in {area}'],
    }
    opts = descriptions.get(type_, [f'Incident reported in {area}'])
    return opts[math.floor(get_rand() * len(opts))]

# CACHE MEMORY
_mock_crimes = []
_mock_cybercrime = []
_mock_patrol_units = []
_mock_hotspots = []
_mock_alerts = []
_mock_patrol_routes = []

def generate_crimes(count=10000):
    if _mock_crimes:
        return _mock_crimes
    crimes = []
    for i in range(count):
        date_info = generate_realistic_date()
        year, month, day, dow = date_info['year'], date_info['month'], date_info['day'], date_info['dow']
        fest = get_festival_context(year, month, day)

        area_weights = [get_area_temporal_weight(a['name'], year, month) for a in AREAS]
        if fest['isFestival']:
            for idx, a in enumerate(AREAS):
                if a['name'] in ['Navrangpura', 'Vastrapur', 'Paldi', 'Ellis Bridge']:
                    area_weights[idx] *= 1.8
        
        area = weighted_pick(AREAS, area_weights)
        hour = math.floor(get_rand() * 24)
        crime_type = pick_crime_type(area['name'], hour, dow, fest['boosts'])
        refined_hour = pick_hour(crime_type) if get_rand() < 0.65 else hour
        severity = determine_severity(crime_type, refined_hour, dow, fest['isFestival'])

        timestamp = f"{year}-{month:02d}-{day:02d} {refined_hour:02d}:{math.floor(get_rand()*60):02d}:{math.floor(get_rand()*60):02d}"

        crimes.append({
            'crime_id': f"CRM-{str(i + 1).zfill(6)}",
            'crime_type': crime_type,
            'latitude': round(jitter(area['lat'], 0.018), 6),
            'longitude': round(jitter(area['lng'], 0.018), 6),
            'area': area['name'],
            'zone': area['zone'],
            'timestamp': timestamp,
            'severity': severity,
            'status': weighted_pick(['Reported', 'Under Investigation', 'Chargesheeted', 'Closed'], [0.35, 0.30, 0.15, 0.20]),
            'fir_number': f"AHD/{year}/{str(math.floor(get_rand() * 99999)).zfill(5)}",
            'description': generate_description(crime_type, area['name']),
            'hour': refined_hour,
            'day_of_week': dow,
            'month': month,
            'year': year,
            'day': day,
            'is_weekend': dow == 0 or dow == 6,
            'is_festival': fest['isFestival'],
            'festival_name': fest['name']
        })
    _mock_crimes.extend(crimes)
    return crimes

CYBER_GROWTH_BY_YEAR = { 2023: 1.0, 2024: 1.55, 2025: 2.30 }
CYBER_TYPE_GROWTH = {
  'UPI Fraud':           { 2023: 1.0, 2024: 1.8, 2025: 3.0 },
  'Online Banking Fraud':{ 2023: 1.0, 2024: 1.4, 2025: 1.9 },
  'Investment Scam':     { 2023: 1.0, 2024: 1.6, 2025: 2.5 },
  'Job Fraud':           { 2023: 1.0, 2024: 1.5, 2025: 2.2 },
  'OTP Scam':            { 2023: 1.0, 2024: 1.7, 2025: 2.8 },
  'Phishing':            { 2023: 1.0, 2024: 1.3, 2025: 1.7 },
  'Social Media Fraud':  { 2023: 1.0, 2024: 1.6, 2025: 2.4 },
  'Identity Theft':      { 2023: 1.0, 2024: 1.2, 2025: 1.5 },
  'Lottery Scam':        { 2023: 1.0, 2024: 1.1, 2025: 1.2 },
  'Cyberstalking':       { 2023: 1.0, 2024: 1.4, 2025: 1.8 },
}
CYBER_AMOUNT_RANGES = {
  'UPI Fraud':            [500,   80000],
  'Online Banking Fraud': [5000,  600000],
  'Investment Scam':      [10000, 3000000],
  'Job Fraud':            [2000,  150000],
  'Lottery Scam':         [1000,  50000],
  'Phishing':             [1000,  100000],
  'OTP Scam':             [500,   120000],
  'Social Media Fraud':   [500,   30000],
  'Identity Theft':       [0,     15000],
  'Cyberstalking':        [0,     0],
}

def generate_cybercrime(count=1200):
    if _mock_cybercrime:
        return _mock_cybercrime
    reports = []
    for i in range(count):
        d = generate_realistic_date()
        year_w = weighted_pick([2023, 2024, 2025], [0.22, 0.35, 0.43])
        type_weights = [CYBER_TYPE_GROWTH.get(t, {}).get(year_w, CYBER_GROWTH_BY_YEAR.get(year_w, 1.0)) for t in CYBER_TYPES]
        fraud_type = weighted_pick(CYBER_TYPES, type_weights)
        area = weighted_pick(AREAS, [a['weight'] for a in AREAS])
        min_amt, max_amt = CYBER_AMOUNT_RANGES.get(fraud_type, [500, 50000])
        amt_growth = 1.6 if year_w == 2025 else 1.25 if year_w == 2024 else 1.0
        amount = round((min_amt + get_rand() * (max_amt - min_amt)) * amt_growth)

        hh = math.floor(get_rand() * 24)
        timestamp = f"{year_w}-{d['month']:02d}-{d['day']:02d} {hh:02d}:{math.floor(get_rand()*60):02d}:00"

        reports.append({
            'report_id': f"CYB-{str(i + 1).zfill(5)}",
            'fraud_type': fraud_type,
            'latitude': round(jitter(area['lat'], 0.022), 6),
            'longitude': round(jitter(area['lng'], 0.022), 6),
            'area': area['name'],
            'zone': area['zone'],
            'amount_lost': amount,
            'timestamp': timestamp,
            'status': weighted_pick(['Reported','Under Investigation','Chargesheeted','Closed'], [0.35,0.30,0.15,0.20]),
            'platform': weighted_pick(['WhatsApp','Telegram','Phone Call','Email','Website','Instagram','OLX','Unknown'], [3,2,4,2,2,2,1,1]),
            'victim_age_group': weighted_pick(['18-25','26-35','36-45','46-60','60+'], [2,3,3,2,1]),
            'hour': hh,
            'month': d['month'],
            'year': year_w,
            'day_of_week': d['dow'],
            'is_weekend': d['dow'] == 0 or d['dow'] == 6
        })
    _mock_cybercrime.extend(reports)
    return reports

def generate_hotspots():
    if _mock_hotspots:
        return _mock_hotspots
    hotspots = [
        {'id':'HS-001', 'name':'Naroda Industrial Corridor', 'lat':23.0720, 'lng':72.6430, 'radius':850, 'risk':'Critical', 'score':94, 'crimes':487, 'primary_type':'Robbery',         'trend':'+12%', 'emerged':'Jan 2023', 'zone':'East'},
        {'id':'HS-002', 'name':'Maninagar Junction Area',    'lat':22.9960, 'lng':72.6055, 'radius':750, 'risk':'Critical', 'score':91, 'crimes':421, 'primary_type':'Chain Snatching', 'trend':'+8%',  'emerged':'Jan 2023', 'zone':'South'},
        {'id':'HS-003', 'name':'Bapunagar Market Cluster',   'lat':23.0540, 'lng':72.6175, 'radius':680, 'risk':'High',     'score':83, 'crimes':356, 'primary_type':'Assault',         'trend':'+6%',  'emerged':'Mar 2023', 'zone':'East'},
        {'id':'HS-004', 'name':'Dariapur Old City',           'lat':23.0315, 'lng':72.5970, 'radius':620, 'risk':'High',     'score':78, 'crimes':312, 'primary_type':'Drug Offense',    'trend':'+2%',  'emerged':'Jan 2023', 'zone':'Central'},
        {'id':'HS-005', 'name':'Asarwa Railway Corridor',     'lat':23.0600, 'lng':72.6095, 'radius':580, 'risk':'High',     'score':76, 'crimes':298, 'primary_type':'Theft',           'trend':'-3%',  'emerged':'Jan 2023', 'zone':'East'},
        {'id':'HS-006', 'name':'Gomtipur East Market',        'lat':23.0270, 'lng':72.6310, 'radius':520, 'risk':'High',     'score':72, 'crimes':267, 'primary_type':'Vehicle Theft',   'trend':'+5%',  'emerged':'May 2023', 'zone':'East'},
        {'id':'HS-007', 'name':'Narol Industrial Zone',       'lat':22.9700, 'lng':72.6200, 'radius':680, 'risk':'High',     'score':74, 'crimes':285, 'primary_type':'Vehicle Theft',   'trend':'+18%', 'emerged':'Jun 2024', 'zone':'South'},
        {'id':'HS-008', 'name':'Vatva GIDC Cluster',          'lat':22.9600, 'lng':72.6400, 'radius':640, 'risk':'High',     'score':70, 'crimes':265, 'primary_type':'Burglary',        'trend':'+14%', 'emerged':'Aug 2024', 'zone':'South'},
        {'id':'HS-009', 'name':'Isanpur Crossroads',          'lat':22.9850, 'lng':72.6130, 'radius':480, 'risk':'Medium',   'score':63, 'crimes':221, 'primary_type':'Assault',         'trend':'+1%',  'emerged':'Jan 2023', 'zone':'South'},
        {'id':'HS-010', 'name':'Nikol Highway Stretch',       'lat':23.0510, 'lng':72.6540, 'radius':460, 'risk':'Medium',   'score':58, 'crimes':198, 'primary_type':'Robbery',         'trend':'-4%',  'emerged':'Jan 2023', 'zone':'East'},
        {'id':'HS-011', 'name':'Vastral Bridge Vicinity',     'lat':23.0265, 'lng':72.6590, 'radius':430, 'risk':'Medium',   'score':54, 'crimes':176, 'primary_type':'Chain Snatching', 'trend':'+3%',  'emerged':'Apr 2023', 'zone':'East'},
        {'id':'HS-012', 'name':'Ranip Junction',              'lat':23.0940, 'lng':72.5625, 'radius':410, 'risk':'Medium',   'score':49, 'crimes':154, 'primary_type':'Drug Offense',    'trend':'+8%',  'emerged':'Jul 2023', 'zone':'North'},
        {'id':'HS-013', 'name':'Chandkheda Market',           'lat':23.1190, 'lng':72.5920, 'radius':340, 'risk':'Low',      'score':29, 'crimes':87,  'primary_type':'Mobile Theft',    'trend':'-18%', 'emerged':'Jan 2023', 'zone':'North'},
        {'id':'HS-014', 'name':'Shahibaug Junction',          'lat':23.0660, 'lng':72.5910, 'radius':360, 'risk':'Low',      'score':34, 'crimes':112, 'primary_type':'Theft',           'trend':'-8%',  'emerged':'Jan 2023', 'zone':'North'},
        {'id':'HS-015', 'name':'Satellite-Bodakdev Corridor', 'lat':23.0340, 'lng':72.5150, 'radius':580, 'risk':'High',     'score':68, 'crimes':245, 'primary_type':'Vehicle Theft',   'trend':'+22%', 'emerged':'Jan 2025', 'zone':'West'}
    ]
    _mock_hotspots.extend(hotspots)
    return hotspots

OFFICER_NAMES = [
  'SI Rajan Patel','HC Amit Shah','ASI Meera Joshi','SI Suresh Kumar',
  'PSI Priya Desai','SI Vikram Singh','HC Rajesh Yadav','ASI Anjali Mehta',
  'SI Dinesh Chauhan','PSI Kavita Sharma','HC Mohan Trivedi','SI Ankit Patel',
  'ASI Sunita Rao','SI Manish Gupta','HC Dilip Solanki','PSI Rekha Nair',
  'SI Bharat Patel','HC Jignesh Modi','ASI Pooja Verma','SI Kiran Kumar',
  'PSI Sanjay Shah','HC Nita Pandya','SI Ashok Prajapati','PSI Leela Raj',
]

def generate_patrol_units(count=24):
    if _mock_patrol_units:
        return _mock_patrol_units
    statuses = ['On Patrol','On Patrol','On Patrol','Responding','At Station','Standby']
    vehicles = ['PCR Van','Motorcycle','SUV','Jeep']
    units = []
    for i in range(count):
        area = AREAS[i % len(AREAS)]
        units.append({
            'vehicle_id': f"AHD-PCR-{str(i + 1).zfill(3)}",
            'officer_id': f"OFF-{str(1000 + i).zfill(4)}",
            'officer_name': OFFICER_NAMES[i % len(OFFICER_NAMES)],
            'current_location': {'lat': round(jitter(area['lat'], 0.01), 6), 'lng': round(jitter(area['lng'], 0.01), 6)},
            'area': area['name'],
            'zone': area['zone'],
            'status': statuses[i % len(statuses)],
            'vehicle_type': vehicles[i % len(vehicles)],
            'shift_time': '06:00–14:00' if i%3==0 else '14:00–22:00' if i%3==1 else '22:00–06:00',
            'incidents_handled': math.floor(get_rand() * 8),
            'last_update': (datetime.utcnow() - timedelta(milliseconds=math.floor(get_rand()*3600000))).isoformat() + "Z"
        })
    _mock_patrol_units.extend(units)
    return units

def generate_patrol_routes():
    if _mock_patrol_routes:
        return _mock_patrol_routes
    routes = [
        {
          'id':'RT-001', 'vehicle_id':'AHD-PCR-001', 'name':'Naroda High-Risk Circuit', 'color':'#FF1744',
          'waypoints':[
            { 'lat':23.0695, 'lng':72.6415, 'name':'Naroda PS (Start)' },
            { 'lat':23.0720, 'lng':72.6450, 'name':'Industrial Zone Entry' },
            { 'lat':23.0680, 'lng':72.6490, 'name':'Naroda Patiya' },
            { 'lat':23.0650, 'lng':72.6430, 'name':'Market Cluster' },
            { 'lat':23.0695, 'lng':72.6415, 'name':'Naroda PS (End)' },
          ],
          'distance_km':8.4, 'coverage':'94%', 'eta_minutes':45,
        },
        {
          'id':'RT-002', 'vehicle_id':'AHD-PCR-005', 'name':'Maninagar-Isanpur Route', 'color':'#FF6D00',
          'waypoints':[
            { 'lat':22.9970, 'lng':72.6043, 'name':'Maninagar PS' },
            { 'lat':22.9920, 'lng':72.6100, 'name':'Station Road Jct.' },
            { 'lat':22.9860, 'lng':72.6130, 'name':'Isanpur Market' },
            { 'lat':22.9810, 'lng':72.6080, 'name':'Isanpur Crossing' },
            { 'lat':22.9970, 'lng':72.6043, 'name':'Maninagar PS' },
          ],
          'distance_km':6.2, 'coverage':'87%', 'eta_minutes':35,
        },
        {
          'id':'RT-003', 'vehicle_id':'AHD-PCR-010', 'name':'Central Ahmedabad Route', 'color':'#FFD600',
          'waypoints':[
            { 'lat':23.0310, 'lng':72.5960, 'name':'Dariapur PS' },
            { 'lat':23.0350, 'lng':72.5910, 'name':'Teen Darwaja' },
            { 'lat':23.0395, 'lng':72.5613, 'name':'Navrangpura' },
            { 'lat':23.0328, 'lng':72.5716, 'name':'Ellis Bridge' },
            { 'lat':23.0310, 'lng':72.5960, 'name':'Dariapur PS' },
          ],
          'distance_km':9.1, 'coverage':'78%', 'eta_minutes':52,
        },
    ]
    _mock_patrol_routes.extend(routes)
    return routes

def generate_alerts(count=50):
    if _mock_alerts:
        return _mock_alerts
    templates = [
        {'type':'Critical', 'title':'Crime Spike Detected',    'msg': lambda a: f"Robbery incidents up 40% in {a} in last 2 hours"},
        {'type':'Critical', 'title':'New Hotspot Emerged',     'msg': lambda a: f"New crime cluster detected near {a} — 8 incidents in 1 hour"},
        {'type':'Critical', 'title':'Armed Robbery Active',    'msg': lambda a: f"Armed robbery in progress reported near {a}"},
        {'type':'High',     'title':'Risk Threshold Breached', 'msg': lambda a: f"Risk score exceeded 85 in {a}"},
        {'type':'High',     'title':'Patrol Gap Identified',   'msg': lambda a: f"No patrol unit active in {a} for 45+ mins"},
        {'type':'High',     'title':'Cyber Fraud Cluster',     'msg': lambda a: f"UPI fraud cluster detected — 12 reports from {a} in 3 hours"},
        {'type':'High',     'title':'Drug Peddling Alert',     'msg': lambda a: f"Suspected drug peddling hub identified in {a}"},
        {'type':'Medium',   'title':'Chain Snatching Alert',   'msg': lambda a: f"3 chain snatching incidents near {a} in 30 mins"},
        {'type':'Medium',   'title':'Vehicle Theft Pattern',   'msg': lambda a: f"Multiple vehicle thefts near {a} parking zone"},
        {'type':'Medium',   'title':'Festival Crowd Alert',    'msg': lambda a: f"Large gathering near {a} — increased patrol advised"},
        {'type':'Low',      'title':'Patrol Route Update',     'msg': lambda a: f"AI-recommended patrol route updated for {a} sector"},
        {'type':'Low',      'title':'Shift Change Alert',      'msg': lambda a: f"Patrol handover scheduled for {a} sector in 15 min"},
    ]
    alerts = []
    now = datetime.utcnow()
    for i in range(count):
        tpl = templates[i % len(templates)]
        area = AREAS[math.floor(get_rand() * len(AREAS))]['name']
        mins_ago = math.floor(get_rand() * 480)
        alerts.append({
            'id': f"ALT-{str(i + 1).zfill(4)}",
            'type': tpl['type'],
            'title': tpl['title'],
            'message': tpl['msg'](area),
            'area': area,
            'timestamp': (now - timedelta(minutes=mins_ago)).isoformat() + "Z",
            'acknowledged': get_rand() > 0.65,
            'assigned_to': random_item(OFFICER_NAMES) if get_rand() > 0.5 else None
        })
    alerts.sort(key=lambda x: x['timestamp'], reverse=True)
    _mock_alerts.extend(alerts)
    return alerts

def get_predictions():
    return [
        {'area':'Naroda',          'risk_level':'Critical', 'score':94, 'predicted_crimes':48, 'top_crime':'Robbery',         'confidence':91, 'deployment':'4 units + 1 PCR van', 'lat':23.0695, 'lng':72.6415},
        {'area':'Maninagar',       'risk_level':'Critical', 'score':89, 'predicted_crimes':42, 'top_crime':'Chain Snatching', 'confidence':88, 'deployment':'3 units + special team', 'lat':22.9970, 'lng':72.6043},
        {'area':'Bapunagar',       'risk_level':'High',     'score':81, 'predicted_crimes':34, 'top_crime':'Assault',         'confidence':84, 'deployment':'3 units recommended', 'lat':23.0530, 'lng':72.6160},
        {'area':'Narol',           'risk_level':'High',     'score':74, 'predicted_crimes':28, 'top_crime':'Vehicle Theft',   'confidence':80, 'deployment':'2 units + CCTV check', 'lat':22.9700, 'lng':72.6200},
        {'area':'Dariapur',        'risk_level':'High',     'score':72, 'predicted_crimes':26, 'top_crime':'Drug Offense',    'confidence':78, 'deployment':'2 units recommended', 'lat':23.0310, 'lng':72.5960},
        {'area':'Satellite',       'risk_level':'Medium',   'score':68, 'predicted_crimes':22, 'top_crime':'Vehicle Theft',   'confidence':74, 'deployment':'2 units — night shift', 'lat':23.0226, 'lng':72.5137},
        {'area':'Chandkheda',      'risk_level':'Low',      'score':29, 'predicted_crimes':7,  'top_crime':'Mobile Theft',    'confidence':68, 'deployment':'Standard patrol',       'lat':23.1180, 'lng':72.5908},
    ]

# Pre-generate or trigger on load
# generate_crimes(10000)
# generate_cybercrime(1200)
# generate_patrol_units(24)
# generate_hotspots()
# generate_alerts(50)
# generate_patrol_routes()
