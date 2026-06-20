import os
import re

def refactor_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # If it's a component, inject the useData hook
    if 'from' in content and 'mockData' in content:
        # Import useData
        if 'useData' not in content:
            # Figure out relative path to context
            depth = filepath.count(os.sep) - filepath.find('src') - 1
            rel_path = '../' * (depth) + 'context/DataContext'
            content = f"import {{ useData }} from '{rel_path}';\n" + content
            
            # Find the component declaration to inject the hook
            # e.g., export default function CommandCenter() {
            component_match = re.search(r'(export default function \w+\([^)]*\)\s*\{)', content)
            if component_match:
                hook_inject = "  const { crimes, hotspots, patrols, routes, cybercrime, alerts, predictions, loading } = useData();\n"
                content = content.replace(component_match.group(1), component_match.group(1) + "\n" + hook_inject)
            elif re.search(r'(const \w+ = \([^)]*\) =>\s*\{)', content):
                component_match = re.search(r'(const \w+ = \([^)]*\) =>\s*\{)', content)
                hook_inject = "  const { crimes, hotspots, patrols, routes, cybercrime, alerts, predictions, loading } = useData();\n"
                content = content.replace(component_match.group(1), component_match.group(1) + "\n" + hook_inject)

    # Note: This regex-based refactor is risky. Instead of full regex, I will just do it file by file with replace_file_content to guarantee 100% correctness.

print("Use replace_file_content instead.")
