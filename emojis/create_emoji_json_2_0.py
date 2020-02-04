import json


def create_emoji_v1_0():

    omit = [
        "1F573"
            ]
    data = None
    with open('data/emoji.json', encoding="utf8") as json_file:
        data = json.load(json_file)

    copy = []
    for d in data:

        if not d['codes'] in omit \
                and not "Component" in d['category']:
            APIS = []
            APIS.append(29)
            APIS.append(28)
            APIS.append(27)
            APIS.append(26)
            APIS.append(25)
            APIS.append(24)

            category = d['category']
            if "Smileys & Emotion" in d['category'] or "People & Body" in d['category']:
                category = "Smileys and people"
            elif "Animals" in d['category']:
                category = "Animals and nature"
            elif "Food" in d['category']:
                category = "Food and drinks"
            elif "Activities" in d['category']:
                category = "Sports and activities"
            elif "Travel" in d['category']:
                category = "Travel and places"
            elif "Objects" in d['category']:
                category = "Objects"
            elif "Symbols" in d['category']:
                category = "Symbols"
            elif "Flags" in d['category']:
                category = "Flags"

            copy.append({
                'codes': d['codes'],
                'char': d['char'],
                'name': d['name'],
                'category': category,
                'apis': APIS
            })

        # print(d)



    with open('emoji_api.json', 'w') as outfile:
        json.dump(copy, outfile)


if __name__ == "__main__":
    create_emoji_v1_0()

