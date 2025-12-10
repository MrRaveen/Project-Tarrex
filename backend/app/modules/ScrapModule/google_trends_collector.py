from pytrends.request import TrendReq
from datetime import datetime
from ...config.mongo import MongoDB

class GoogleTrendsCollector:

    def __init__(self):
        self.pytrends = TrendReq(
            hl="en-US",
            tz=330   # Sri Lanka timezone (UTC+5:30)
        )
        self.ins = MongoDB()
        self.db = self.ins.db
        
        
    def test_trends(self):
        try:
            print("Testing Google Trends API...")
            
            # Try interest over time first
            self.pytrends.build_payload(
                kw_list=["Sri Lanka"],
                timeframe="now 7-d",
                geo="LK"
            )
            
            interest_over_time = self.pytrends.interest_over_time()
            print(f"Interest over time data:\n{interest_over_time.head()}")
            
            # Test related topics
            related_topics = self.pytrends.related_topics()
            print(f"Related topics: {related_topics}")
            
            # Test related queries
            related_queries = self.pytrends.related_queries()
            print(f"Related queries: {related_queries}")
            
            return True
        except Exception as e:
            print(f"Test error: {e}")
            return False    
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
            self.ins.db.insert_many("google_trends_top_rising", output)

            return output

        except Exception as e:
            print("Top & Rising Error:", str(e))
            return []
