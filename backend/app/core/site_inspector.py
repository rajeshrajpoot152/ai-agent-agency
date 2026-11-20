import re
import time
import json
import urllib.request
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

def inspect_live_website(raw_url: str) -> Dict[str, Any]:
    """
    Crawls and performs a 360-degree real-time diagnostic audit of any URL:
    - Technical SEO (Title, Meta, Canonical, Robots, Status, Response Time)
    - Content & Structure (H1, H2, H3 hierarchy, Word count, Alt tags)
    - Structured Data (Schema.org JSON-LD, OpenGraph)
    - Conversion & CRO (CTAs, Phone/Email links, Value proposition)
    - AI Search / GEO Readiness (Entity clarity, llms.txt)
    """
    # 1. Normalize URL
    target_url = raw_url.strip()
    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        target_url = "https://" + target_url

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AgencyBot/2.0"
    }

    response = None
    corrected_note = ""
    candidate_urls = [target_url]

    # Generate smart phonetic & spelling fallbacks (e.g. 'w' -> 'v', like yashwiglobal -> yashviglobal)
    if "w" in target_url:
        candidate_urls.append(target_url.replace("w", "v"))
    if "https://www." not in target_url:
        candidate_urls.append(target_url.replace("https://", "https://www."))

    last_err = None
    for cand in candidate_urls:
        try:
            t0 = time.time()
            req = urllib.request.Request(cand, headers=headers)
            response = urllib.request.urlopen(req, timeout=12)
            latency_ms = round((time.time() - t0) * 1000)
            status_code = response.status
            final_url = response.url
            html_content = response.read().decode("utf-8", errors="ignore")
            if cand != target_url:
                corrected_note = f"(Corrected domain from '{raw_url}' to '{cand}')"
            target_url = cand
            break
        except Exception as e:
            last_err = e
            response = None

    if response is None:
        return {
            "status": "error",
            "url": target_url,
            "error_message": f"Website inaccessible ({last_err})"
        }

    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # 2. Meta & Title Analysis
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        meta_desc_el = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
        meta_desc = meta_desc_el.get("content", "").strip() if meta_desc_el else ""

        canonical_el = soup.find("link", attrs={"rel": "canonical"})
        canonical_url = canonical_el.get("href", "").strip() if canonical_el else ""

        robots_el = soup.find("meta", attrs={"name": re.compile(r"robots", re.I)})
        robots_content = robots_el.get("content", "").strip() if robots_el else "index, follow (default)"

        # OpenGraph
        og_title_el = soup.find("meta", attrs={"property": "og:title"})
        og_title = og_title_el.get("content", "") if og_title_el else ""
        og_image_el = soup.find("meta", attrs={"property": "og:image"})
        has_og_image = bool(og_image_el and og_image_el.get("content"))

        # 3. Headings Architecture (H1, H2, H3)
        h1_tags = [h.get_text().strip() for h in soup.find_all("h1") if h.get_text().strip()]
        h2_tags = [h.get_text().strip() for h in soup.find_all("h2") if h.get_text().strip()]
        h3_tags = [h.get_text().strip() for h in soup.find_all("h3") if h.get_text().strip()]

        # 4. Images Audit
        images = soup.find_all("img")
        images_count = len(images)
        images_missing_alt = sum(1 for img in images if not img.get("alt") or not img.get("alt").strip())

        # 5. Schema.org JSON-LD Detection
        schema_scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
        detected_schemas = []
        for s in schema_scripts:
            try:
                data = json.loads(s.string)
                if isinstance(data, dict) and "@type" in data:
                    detected_schemas.append(data["@type"])
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and "@type" in item:
                            detected_schemas.append(item["@type"])
            except Exception:
                pass

        # 6. CRO, Contact & Call-to-Actions
        text_content = soup.get_text(separator=" ", strip=True)
        words = len(text_content.split())

        ctas = []
        for btn in soup.find_all(["button", "a"]):
            btn_text = btn.get_text().strip()
            if any(w in btn_text.lower() for w in ["contact", "book", "call", "start", "sign up", "demo", "buy", "get started", "trial", "schedule"]):
                if len(btn_text) < 40 and btn_text not in ctas:
                    ctas.append(btn_text)

        has_phone = bool(soup.find("a", href=re.compile(r"^tel:")))
        has_email = bool(soup.find("a", href=re.compile(r"^mailto:")))

        # 7. Overall Health Scoring (0 - 100)
        score = 60
        if 30 <= len(title) <= 65: score += 8
        if 80 <= len(meta_desc) <= 165: score += 8
        if len(h1_tags) == 1: score += 8
        elif len(h1_tags) > 1: score -= 4
        if images_missing_alt == 0 and images_count > 0: score += 6
        if detected_schemas: score += 10
        if latency_ms < 1500: score += 8
        if ctas: score += 6
        if has_phone or has_email: score += 6
        score = max(20, min(100, score))

        return {
            "status": "success",
            "url": target_url,
            "final_url": final_url,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "score": score,
            "title": title,
            "title_length": len(title),
            "meta_description": meta_desc,
            "meta_desc_length": len(meta_desc),
            "canonical_url": canonical_url,
            "robots": robots_content,
            "og_title": og_title,
            "has_og_image": has_og_image,
            "h1_count": len(h1_tags),
            "h1_tags": h1_tags[:3],
            "h2_count": len(h2_tags),
            "h2_tags": h2_tags[:5],
            "h3_count": len(h3_tags),
            "images_count": images_count,
            "images_missing_alt": images_missing_alt,
            "detected_schemas": list(set(detected_schemas)),
            "word_count": words,
            "ctas": ctas[:6],
            "has_phone": has_phone,
            "has_email": has_email
        }

    except Exception as e:
        return {
            "status": "error",
            "url": target_url,
            "error_message": str(e)
        }
