import re


def clean_name(name: str):
    clean_name = re.findall("[A-Za-z0-9]", name)
    return "".join(clean_name)


names = ["testing", "test:ting", "DistrictTest9ing*"]

results = []
for name in names:
    results.append(clean_name(name))

assert results == ["testing", "testting", "DistrictTest9ing"]
