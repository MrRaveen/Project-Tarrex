# use to get Google Trends data via requests but fails
"""
# src/collectors/google_trends_new.py
import requests
import json
import re
from datetime import datetime
from html import unescape

class GoogleTrendsNew:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://trends.google.com/"
        })

    def _clean_js_prefix(self, text: str):
        # Google often prefixes JSON responses with )]}',
        return re.sub(r"^\)\]\}',\s*", "", text, count=1)

    def fetch_trending_now(self, country="LK", debug=False, fallback_limit=10):

        result = {"timeline": [], "keywords": []}

        # --- PART A: Try the official explore -> widget -> widgetdata flow ---
        try:
            # 1) fetch explore widgets
            widget_url = (
                "https://trends.google.com/trends/api/explore?"
                f"hl=en-US&req={{\"comparisonItem\":[{{\"geo\":\"{country}\",\"time\":\"now 1-d\"}}],"
                "\"category\":0,\"property\":\"\"}}"
            )

            widget_resp = self.session.get(widget_url, timeout=15)
            if debug:
                print("EXPLORE status:", widget_resp.status_code)

            if widget_resp.status_code == 200 and widget_resp.text:
                cleaned = self._clean_js_prefix(widget_resp.text)
                # quick sanity check
                if debug:
                    print("EXPLORE raw snippet:", cleaned[:400])

                data = json.loads(cleaned)
                # find a TIMESERIES or related widget that has timeline/token
                timeline_widget = None
                # widgets can have types: TIMELINE, GEO_MAP, RELATED_QUERIES, etc.
                for w in data.get("widgets", []):
                    wid = w.get("id", "").upper()
                    if "TIMESERIES" in wid or w.get("title", "").lower().find("trend") != -1:
                        timeline_widget = w
                        break
                # fallback: pick first widget with a token & request
                if not timeline_widget:
                    for w in data.get("widgets", []):
                        if "token" in w and "request" in w:
                            timeline_widget = w
                            break

                if timeline_widget and "token" in timeline_widget and "request" in timeline_widget:
                    token = timeline_widget["token"]
                    req_obj = timeline_widget["request"]
                    # call widgetdata/multiline
                    timeline_url = (
                        "https://trends.google.com/trends/api/widgetdata/multiline?"
                        f"hl=en-US&req={json.dumps(req_obj)}&token={token}"
                    )

                    tr_resp = self.session.get(timeline_url, timeout=15)
                    if debug:
                        print("TIMELINE status:", tr_resp.status_code)
                        print("TIMELINE snippet:", (tr_resp.text or "")[:300])

                    if tr_resp.status_code == 200 and tr_resp.text:
                        cleaned2 = self._clean_js_prefix(tr_resp.text)
                        timeline_data = json.loads(cleaned2)
                        for point in timeline_data.get("default", {}).get("timelineData", []):
                            result["timeline"].append({
                                "time": point.get("formattedTime"),
                                "value": point.get("value", [0])[0],
                                "scraped_at": datetime.utcnow().isoformat()
                            })
                        # also try to extract top keywords from the 'widgets' related queries if available
                        for w in data.get("widgets", []):
                            if w.get("id", "").upper().startswith("RELATED"):
                                # try to parse top queries from widget content if present
                                token_r = w.get("token")
                                req_r = w.get("request")
                                if token_r and req_r:
                                    url_r = (
                                        "https://trends.google.com/trends/api/widgetdata/relatedsearches?"
                                        f"hl=en-US&req={json.dumps(req_r)}&token={token_r}"
                                    )
                                    rr = self.session.get(url_r, timeout=12)
                                    if rr.status_code == 200 and rr.text:
                                        cleaned_rr = self._clean_js_prefix(rr.text)
                                        try:
                                            rr_json = json.loads(cleaned_rr)
                                            # try to collect 'query' strings
                                            for entry in rr_json.get("default", {}).get("rankedList", []):
                                                for item in entry.get("rankedKeyword", []):
                                                    q = item.get("query", {}).get("query")
                                                    if q:
                                                        result["keywords"].append(q)
                                        except Exception:
                                            pass
                        # dedupe keywords
                        result["keywords"] = list(dict.fromkeys(result["keywords"]))
                        if result["timeline"] or result["keywords"]:
                            return result
                    else:
                        if debug:
                            print("Timeline request failed or empty body; status:", tr_resp.status_code)
                else:
                    if debug:
                        print("No suitable timeline widget in explore response")
            else:
                if debug:
                    print("Explore request failed or empty. status:", widget_resp.status_code)
        except Exception as e:
            if debug:
                print("Widget flow exception:", repr(e))

        # --- PART B: FALLBACK — scrape the public trends page for visible keywords ---
        try:
            page_url = f"https://trends.google.com/trending?geo={country}"
            page_resp = self.session.get(page_url, timeout=15)
            if debug:
                print("PAGE status:", page_resp.status_code)
            text = page_resp.text or ""
            snippet = text[:1000]
            if debug:
                print("PAGE snippet:", snippet.replace("\n", " ")[:800])

            # Attempt 1: Find JSON-like blocks embedded in the HTML (common patterns)
            # look for "trends" / "trending" JSON snippets, or for "title":"..." patterns
            keywords = []

            # pattern 1: find "title":"Some title"
            for m in re.finditer(r'"title"\s*:\s*"([^"]{3,120}?)"', text):
                kw = unescape(m.group(1)).strip()
                if len(kw) > 1:
                    keywords.append(kw)

            # pattern 2: find "query":"some query"
            for m in re.finditer(r'"query"\s*:\s*"([^"]{3,120}?)"', text):
                kw = unescape(m.group(1)).strip()
                if len(kw) > 1:
                    keywords.append(kw)

            # pattern 3: anchors that visually look like trend items (heuristic)
            for m in re.finditer(r'<a[^>]*>\s*([^<]{3,120}?)\s*</a>', text):
                txt = m.group(1).strip()
                # filter out navigation/labels by requiring some whitespace and letters
                if len(txt) > 3 and re.search(r"[A-Za-z0-9]", txt):
                    keywords.append(unescape(txt))

            # filter and dedupe while keeping order
            seen = set()
            cleaned_keywords = []
            for k in keywords:
                k2 = re.sub(r'\s+', ' ', k).strip()
                if k2.lower() in seen:
                    continue
                if len(k2) < 3:
                    continue
                seen.add(k2.lower())
                cleaned_keywords.append(k2)
                if len(cleaned_keywords) >= fallback_limit:
                    break

            result["keywords"] = cleaned_keywords
            if result["keywords"]:
                return result

            # If nothing found, return empty with helpful debug hint
            if debug:
                print("Fallback scraping found no keywords. Page length:", len(text))

        except Exception as e:
            if debug:
                print("Fallback scraping exception:", repr(e))

        # final: empty result
        return result
"""