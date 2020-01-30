import json


def create_emoji_v1_0():
    # not for api 23
    skip23 = ["keycap ASTERISK",
            "flag for Ascension Island",
            "flag for Antarctica",
            "flag for Bouvet Island",
            "flag for Clipperton Island",
            "flag for Heard & McDonald Islands",
            "flag for Canary Islands",
            "flag for St. Helena",
            "flag for Svalbard & Jan Mayen",
            "flag for Tristan da Cunha",
            "flag for U.S. Outlying Islands"]

    # not for api 24
    skip24 = ["flag for St. Barthélemy",
                "flag for Caribbean Netherlands",
                "flag for Diego Garcia",
                "flag for Ceuta & Melilla",
                "flag for Western Sahara",
                "flag for Falkland Islands",
                "flag for French Guiana",
                "flag for Guadeloupe",
                "flag for South Georgia & South Sandwich Islands",
                "flag for St. Martin",
                "flag for Martinique",
                "flag for New Caledonia",
                "flag for St. Pierre & Miquelon",
                "flag for Réunion",
                "flag for French Southern Territories",
                "flag for Wallis & Futuna",
                "flag for Kosovo",
                "flag for Mayotte"]
    file = open("data/emoji-data_1_0.txt", encoding="utf8")
    result = {}
    result['emoji'] = []
    for line in file:
        # We remove the commented lines since these are not interesting for us.
        if not line.startswith("#"):
            data = line.split(";")
            # There are always the same amount of semicolons dividing the data, namely 5.
            # The codes are split up with spaces
            codes = data[0].split(" ")
            # The last item is always an empty string, we remove it.
            del codes[-1]
            # We first only include the 'L1' (level 1) emojis
            APIS = []
            details = data[-1]
            char = details.split("(")[1].split(")")[0]
            name = details.split(")")[1].rstrip("\n\r")[1:]

            APIS.append(26)
            # The flags that were flaged to not work in 24 also don't work in 25, we include them in 26
            if name not in skip24:
                APIS.append(24)
                if "V7.0" not in details and "V8.0" not in details:
                    if name not in skip23:
                        APIS.append(23)
            else:
                if name not in skip24:
                    APIS.append(24)
                    if name not in skip23:
                        APIS.append(23)
            if "L1" in data[2]:
                APIS.append(22)

            result['emoji'].append({
                'codes': codes,
                'char': char,
                'name': name,
                'category': "",
                'apis': APIS
            })

    with open('emoji_1_0.json', 'w') as outfile:
        json.dump(result, outfile)


if __name__ == "__main__":
    create_emoji_v1_0()

