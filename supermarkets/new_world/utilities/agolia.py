import json

def create_algolia_query(category, page):
    query = {
            "attributestohighlight": [],
            "attributestoretrieve": [
                "productid",
                "type",
                "sponsored",
                "category0NI",
                "category1NI",
                "category2NI"
            ],
            "facets": [
                "brand",
                "category1ni",
                "onpromotion",
                "productfacets"
            ],
            "filters": f'stores:d4408e0f-5268-42c2-ba76-2bc9732d4316 and category0ni:"{category}"',
            "highlightposttag": "__/ais-highlight__",
            "highlightpretag": "__ais-highlight__",
            "hitsperpage": 50,
            "maxvaluesperfacet": 100,
            "page": page
        }
    return json.dumps(query)

def generate_query(category, page):
    precision_media = json.dumps({"adDomain":"CATEGORY_PAGE","adPositions":[4,8,12,16]})

    return [
          f"""algoliaQuery:='{{"attributesToHighlight":[],"attributesToRetrieve":["productID","Type","sponsored","category0NI","category1NI","category2NI"],"facets":["brand","category1NI","onPromotion","productFacets"],"filters":"stores:d4408e0f-5268-42c2-ba76-2bc9732d4316 AND category0NI:\\"{category}\\"","highlightPostTag":"__/ais-highlight__","highlightPreTag":"__ais-highlight__","hitsPerPage":50,"maxValuesPerFacet":100,"page":{page}}}'"""
        , "storeId='d4408e0f-5268-42c2-ba76-2bc9732d4316'"
        , "hitsPerPage:=50"
        , f"page:={page}"
        , "sortOrder='NI_POPULARITY_ASC'"
        , "tobaccoQuery:=false"
        , "disableAds:=true"
        , "publishImpressionEvent:=false"
        , f"precisionMedia:='{precision_media}'"
    ]
