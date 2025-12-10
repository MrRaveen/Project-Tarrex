from flask import jsonify
import requests

class scrapFoodPricingAll:
    def getFoodPricing():
        try:
            uri = "https://hapi.humdata.org/api/v2/food-security-nutrition-poverty/food-prices-market-monitor?app_identifier=dGFyZXg6ZGV2ZWxvcGVyb2ZmaWNpYWw1NEBnbWFpbC5jb20%3D&location_code=LKA&location_name=Sri%20Lanka&output_format=json&limit=100&offset=0"
            response = requests.get(uri)
        except Exception as e:
            return jsonify({"error" : str(e)})  
    
      