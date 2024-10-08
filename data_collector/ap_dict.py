ap_dict_ana = {
    "SPK" : "札幌(千歳)",
    "CTS" : "札幌(千歳)",
    "RIS" : "利尻",
    "WKJ" : "稚内",
    "MBE" : "オホーツク紋別",
    "MMB" : "女満別",
    "AKJ" : "旭川",
    "SHB" : "根室中標津",
    "KUH" : "釧路",
    "OBO" : "帯広",
    "HKD" : "函館",
    "AOJ" : "青森",
    "ONJ" : "大館能代",
    "AXT" : "秋田",
    "SYO" : "庄内",
    "SDJ" : "仙台",
    "FKS" : "福島",
    "HND" : "東京(羽田)",
    "NRT" : "東京(成田)",
    "HAC" : "八丈島",
    "KIJ" : "新潟",
    "FSZ" : "静岡",
    "NGO" : "名古屋(中部)",
    "TOY" : "富山",
    "KMQ" : "小松",
    "NTQ" : "能登",
    "ITM" : "大阪(伊丹)",
    "KIX" : "大阪(関西)",
    "UKB" : "大阪(神戸)",
    "OKJ" : "岡山",
    "HIJ" : "広島",
    "IWK" : "岩国",
    "UBJ" : "山口宇部",
    "TTJ" : "鳥取",
    "YGJ" : "米子",
    "IWJ" : "萩・石見",
    "TAK" : "高松",
    "TKS" : "徳島",
    "MYJ" : "松山",
    "KCZ" : "高知",
    "FUK" : "福岡",
    "KKJ" : "北九州",
    "HSG" : "佐賀",
    "OIT" : "大分",
    "KMJ" : "熊本",
    "NGS" : "長崎",
    "TSJ" : "対馬",
    "IKI" : "壱岐",
    "FUJ" : "五島福江",
    "AXJ" : "天草",
    "KMI" : "宮崎",
    "KOJ" : "鹿児島",
    "TNE" : "種子島",
    "KUM" : "屋久島",
    "KKX" : "喜界島",
    "RNJ" : "与論",
    "ASJ" : "奄美",
    "TKN" : "徳之島",
    "OKE" : "沖永良部",
    "OKA" : "沖縄(那覇)",
    "MMY" : "宮古",
    "ISG" : "石垣",
}
ap_dict_jal = {
    'HND': '東京（羽田）',
    "NRT" : '東京(成田)',
    "ITM" : '大阪（伊丹）',
    "KIX" : '大阪（関西）',
    "CTS" : '札幌（新千歳）',
    "NGO" : '名古屋（中部）',
    "NKM" : '名古屋（小牧）',
    "UKB" : '大阪（神戸）',
    "FUK" : '福岡',
    "OKA" : '沖縄（那覇）',
    "OKD" : '札幌（丘珠）',
    "RIS" : '利尻',
    "MMB" : '女満別',
    "AKJ" : '旭川',
    "SHB" : '根室中標津',
    "KUH" : '釧路',
    "OBO" : '帯広',
    "HKD" : '函館',
    "OIR" : '奥尻',
    "AOJ" : '青森',
    "MSJ" : '三沢',
    "AXT" : '秋田',
    "HNA" : '花巻',
    "SDJ" : '仙台',
    "GAJ" : '山形',
    "KIJ" : '新潟',
    "MMJ" : '松本',
    "KMQ" : '小松',
    "FSZ" : '静岡',
    "SHM" : '南紀白浜',
    "TJH" : '但馬',
    "OKI" : '隠岐',
    "OKJ" : '岡山',
    "IZO" : '出雲',
    "HIJ" : '広島',
    "UBJ" : '山口宇部',
    "TKS" : '徳島',
    "TAK" : '高松',
    "KCZ" : '高知',
    "MYJ" : '松山',
    "FUK" : '福岡',
    "KKJ" : '北九州',
    "OIT" : '大分',
    "NGS" : '長崎',
    "TSJ" : '対馬',
    "IKI" : '壱岐',
    "FUJ" : '五島福江',
    "KMJ" : '熊本',
    "AXJ" : '天草',
    "KMI" : '宮崎',
    "KOJ" : '鹿児島',
    "TNE" : '種子島',
    "KUM" : '屋久島',
    "KKX" : '喜界島',
    "ASJ" : '奄美大島',
    "TKN" : '徳之島',
    "OKE" : '沖永良部',
    "RNJ" : '与論',
    "KTD" : '北大東',
    "MMD" : '南大東',
    "UEO" : '久米島',
    "MMY" : '宮古',
    "TRA" : '多良間',
    "ISG" : '石垣',
    "OGN" : '与那国',
}

ap_dict_sky = {
    "HND" : "羽田",
    "CTS" : "新千歳",
    "FUK" : "福岡",
    "OKA" : "那覇",
    "NGO" : "中部",
}

ap_dict_ado = {
    "HND" : "東京(羽田)",
    "CTS" : "札幌(新千歳)",
}

def decode(ap_code, company = "jal"):
    '''空港コードを日本語に変換する。'''
    try:
        if company == "jal":
            return ap_dict_jal[ap_code]
        elif company == "ana":
            return ap_dict_ana[ap_code]
        elif company == "sky":
            return ap_dict_sky[ap_code]
        elif company == "ado":
            return ap_dict_ado[ap_code]
    except KeyError:
        return None

def encode(ap_name, company = "jal"):
    '''空港名を空港コードに変換する。'''
    if company == "jal":
        for key, value in ap_dict_jal.items():
            if value == ap_name:
                return key
    elif company == "ana":
        for key, value in ap_dict_ana.items():
            if value == ap_name:
                return key
    elif company == "sky":
        for key, value in ap_dict_sky.items():
            if value == ap_name:
                return key
    elif company == "ado":
        for key, value in ap_dict_ado.items():
            if value == ap_name:
                return key
    return None

