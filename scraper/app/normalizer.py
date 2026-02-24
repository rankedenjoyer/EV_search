import re


def clean_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^a-z0-9 ]", "", name)
    return name.strip()


def canonical_key(team_a: str, team_b: str) -> str:
    teams = sorted([clean_name(team_a), clean_name(team_b)])
    return f"{teams[0]}__vs__{teams[1]}"
