from pytrends.request import TrendReq
from datetime import datetime

class GoogleTrendsCollector:

    def __init__(self):
        self.pytrends = TrendReq(
            hl="en-US",
            tz=330   # Sri Lanka timezone (UTC+5:30)
        )


    def fetch_top_and_rising(self, keywords=["Sri Lanka"], timeframe="now 7-d"):
        """
        Fetch top & rising keywords related to a topic.
        """
        try:
            self.pytrends.build_payload(
                kw_list=keywords,
                cat=0,
                timeframe=timeframe,
                geo="LK",
                gprop=""
            )

            related = self.pytrends.related_queries()
            output = []

            for kw, data in related.items():
                if data["top"] is not None:
                    for _, row in data["top"].iterrows():
                        output.append({
                            "keyword": row["query"],
                            "value": int(row["value"]),
                            "type": "top_query",
                            "topic": kw,
                            "timeframe": timeframe,
                            "scraped_at": datetime.utcnow().isoformat()
                        })

                if data["rising"] is not None:
                    for _, row in data["rising"].iterrows():
                        output.append({
                            "keyword": row["query"],
                            "value": int(row["value"]),
                            "type": "rising_query",
                            "topic": kw,
                            "timeframe": timeframe,
                            "scraped_at": datetime.utcnow().isoformat()
                        })

            return output

        except Exception as e:
            print("Top & Rising Error:", str(e))
            return []
