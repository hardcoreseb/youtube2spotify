import json

def filter_for_title():
    titles = []
    with open("output/playlistitems.json", "r") as f:
        data = json.load(f)  # Load the entire JSON data
        for item in data:
            title = item.get("title")
            if title:
                titles.append(title)
    
    print("Extracted titles:", titles)
    return titles

filter_for_title()
