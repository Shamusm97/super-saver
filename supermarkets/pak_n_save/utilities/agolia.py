import json

def generate_query(category, page):
    precision_media = json.dumps({"adDomain":"CATEGORY_PAGE","adPositions":[4,8,12,16]})

    return [
          f"""algoliaQuery:='{{"attributesToHighlight":[],"attributesToRetrieve":["productID","Type","sponsored","category0NI","category1NI","category2NI"],"facets":["brand","category1NI","onPromotion","productFacets"],"filters":"stores:21ecaaed-0749-4492-985e-4bb7ba43d59c AND category0NI:\\"{category}\\"","highlightPostTag":"__/ais-highlight__","highlightPreTag":"__ais-highlight__","hitsPerPage":50,"maxValuesPerFacet":100,"page":{page}}}'"""
        , "storeId='21ecaaed-0749-4492-985e-4bb7ba43d59c'"
        , "hitsPerPage:=50"
        , f"page:={page}"
        , "sortOrder='NI_POPULARITY_ASC'"
        , "tobaccoQuery:=false"
        , "disableAds:=true"
        , "publishImpressionEvent:=false"
        , f"precisionMedia:='{precision_media}'"
    ]
