import os
import re

src_dir = r"C:\Users\FBT\.gemini\antigravity\scratch\crime-hotspot-platform\src"

files_to_update = [
    r"components\charts\BottomPanel.jsx",
    r"components\map\CommandMap.jsx",
    r"components\panels\LeftPanel.jsx",
    r"components\panels\RightPanel.jsx",
    r"pages\Alerts.jsx",
    r"pages\CrimeAnalytics.jsx",
    r"pages\CyberCrime.jsx",
    r"pages\PatrolRouting.jsx"
]

for rel_path in files_to_update:
    filepath = os.path.join(src_dir, rel_path)
    if not os.path.exists(filepath):
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Determine relative path to context
    depth = rel_path.count(os.sep)
    ctx_path = '../' * depth + 'context/DataContext'
    utils_path = '../' * depth + 'data/analyticsUtils'

    # Remove mockData imports
    content = re.sub(r"import\s+\{[^}]*\}\s+from\s+['\"]\.\./[^'\"]*mockData['\"];\n?", "", content)
    content = re.sub(r"import\s+\{[^}]*\}\s+from\s+['\"]\.\./\.\./data/mockData['\"];\n?", "", content)

    # Insert new imports
    new_imports = f"import {{ useData }} from '{ctx_path}';\nimport {{ AREAS, CRIME_TYPES }} from '{'../' * depth}data/mockData';\nimport {{ getCrimesByType, getCrimesByArea, getCrimesByMonth, getCrimesByHour, getCyberByType, getTotalAmountLost }} from '{utils_path}';\n"
    content = new_imports + content

    # Add the hook to the component
    # Match standard export default function X() {
    comp_match = re.search(r'(export default function \w+\([^)]*\)\s*\{)', content)
    hook_str = "  const { crimes, hotspots, patrols, routes, cybercrime, alerts, predictions, loading } = useData();\n  if (loading) return <div>Loading...</div>;\n"
    
    if comp_match:
        content = content.replace(comp_match.group(1), comp_match.group(1) + "\n" + hook_str)
    else:
        # Match const X = () => {
        comp_match = re.search(r'(const \w+\s*=\s*\([^)]*\)\s*=>\s*\{)', content)
        if comp_match:
            content = content.replace(comp_match.group(1), comp_match.group(1) + "\n" + hook_str)

    # Special replacements for map properties
    content = content.replace('mapCrimes', 'crimes.slice(0, 2000)')
    content = content.replace('recentCrimes', 'crimes.slice(0, 20)')
    content = content.replace('mockHotspots', 'hotspots')
    content = content.replace('mockPatrolUnits', 'patrols')
    content = content.replace('mockPatrolRoutes', 'routes')
    content = content.replace('mockAlerts', 'alerts')
    content = content.replace('mockPredictions', 'predictions')
    content = content.replace('mockCrimes', 'crimes')
    content = content.replace('mockCybercrime', 'cybercrime')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Refactor complete.")
