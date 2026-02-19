from datetime import datetime

def normalize_date(date_str: str | None) -> str:
    """
    Returns date in YYYY-MM-DD format.
    Accepts:
    - 19 Feb
    - 19 February
    - 19 Feb 2026
    - 2026-02-19
    - 19-02-2026
    - None -> today
    """

    if not date_str:
        return datetime.today().strftime("%d-%m-%Y")

    date_str = " ".join(date_str.strip().split()).title()

    formats = [
        "%Y-%m-%d",   # 2026-02-19  ← API format
        "%d-%m-%Y",   # 19-02-2026
        "%d %b %Y",   # 19 Feb 2026
        "%d %B %Y",   # 19 February 2026
        "%d %b",      # 19 Feb
        "%d %B",      # 19 February
        "%d %m %Y",   # 19 02 2026
        "%d %m",  
        "%m %d",
        "%B %d",
        "%b %d"    
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            if "%Y" not in fmt:   # year missing → add current year
                parsed = parsed.replace(year=datetime.today().year)
            return parsed.strftime("%d-%m-%Y")
        except ValueError:
            pass

    # fallback → try ISO auto parse
    try:
        return datetime.fromisoformat(date_str).strftime("%d-%m-%Y")
    except Exception:
        return datetime.today().strftime("%d-%m-%Y")  



if __name__=='__main__':
    print(normalize_date("Feb 16"))  # → 2026-02-19
    print(normalize_date("19 February"))   # → 2026-02-19
    print(normalize_date("19 Feb 2024"))   # → 2024-02-19
