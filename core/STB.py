import requests, re, json, random

from encrypt import *
from config import *


def getEncryptToken():
    url = f"http://{eas_ip}:{eas_port}/iptvepg/platform/getencrypttoken.jsp"

    queries = {
        "UserID": userID,
        "Action": "Login",
        "TerminalFlag": "1",
        "TerminalOsType": "0",
        "STBID": "",
        "stbtype": "",
    }

    query_string = "&".join([f"{key}={value}" for key, value in queries.items()])

    full_url = f"{url}?{query_string}"

    response = requests.get(full_url)

    if response.status_code == 200:
        match = re.search(r"GetAuthInfo\('(.*?)'\)", response.text)
        if match:
            encryptToken = match.group(1)
            return encryptToken
        else:
            print("getEncryptToken: 未找到 GetAuthInfo 函数中的值, 请检查网络连接")
            exit
    else:
        print(f"getEncryptToken: 请求失败，状态码：{response.status_code}")


def generateAuthenticator(encryptToken):
    try:
        random_number = random.randint(10000000, 99999999)
        strEncry = str(random_number) + "$" + encryptToken
        strEncry2 = (
            strEncry
            + "$"
            + userID
            + "$"
            + stbID
            + "$"
            + ip
            + "$"
            + MAC
            + "$"
            + CustomStr
        )
        res = UnionDesEncrypt(strEncry2, encryptKey)
        return res

    except Exception as e:
        print(f"generateAuthenticator: {e}")


def Authentication(Authenticator):
    user_token = ""
    url = f"http://{epgIP}:{epgPort}/iptvepg/platform/auth.jsp?easip={eas_ip}&ipVersion=4&networkid=1&serterminalno=311"

    data = {"UserID": userID, "Authenticator": Authenticator, "StbIP": ip}

    response = requests.post(url, data=data)

    cookies = response.cookies
    jsessionid = cookies.get("JSESSIONID")

    url_pattern = r"window\.location\s*=\s*'(http[^']+)'"
    match = re.search(url_pattern, response.content.decode("gbk"))

    if match:
        extracted_url = match.group(1)

        response = requests.post(
            extracted_url, headers={"Cookie": f"JSESSIONID={jsessionid}"}
        )
        if response.status_code == 200:
            pattern = r"UserToken=([A-Za-z0-9_\-\.]+)"
            match = re.search(pattern, extracted_url)

            if match:
                user_token = match.group(1)
    else:
        print("auth: 鉴权链接获取失败.")

    return jsessionid, user_token


def fetchRaw(jsessionid, user_token):

    url = f"http://{epgIP}:{epgPort}/iptvepg/function/funcportalauth.jsp"

    headers = {"Cookie": f"JSESSIONID={jsessionid}"}

    data = {
        "UserToken": user_token,
        "UserID": userID,
        "STBID": stbID,
        "stbinfo": "",
        "prmid": "",
        "easip": eas_ip,
        "networkid": 1,
        "stbtype": "",
        "drmsupplier": "",
        "stbversion": "",
    }

    response = requests.post(url, headers=headers, data=data)
    url = f"http://{epgIP}:{epgPort}/iptvepg/function/frameset_builder.jsp"
    headers = {"Cookie": f"JSESSIONID={jsessionid}"}
    data = {
        "MAIN_WIN_SRC": "/iptvepg/frame205/channel_start.jsp?tempno=-1",
        "NEED_UPDATE_STB": "1",
        "BUILD_ACTION": "FRAMESET_BUILDER",
        "hdmistatus": "undefined",
    }

    response = requests.post(url, headers=headers, data=data)
    raw_text = response.content.decode("gbk")

    channels = []
    for line in raw_text.splitlines():
        match = re.search(r"jsSetConfig\('Channel',\s*'([^']+)'\)", line)
        if match:
            config_str = match.group(1)
            pattern = r"(\w+)=\"([^\"]+)\""
            config_dict = dict(re.findall(pattern, config_str))
            channels.append(config_dict)

    with open("raw.json", "w", encoding="utf-8") as json_file:
        json.dump(channels, json_file, ensure_ascii=False, indent=4)
        print("数据已写入到 raw.json")


def get_iptw_raw():
    fetchRaw(*Authentication(generateAuthenticator(getEncryptToken())))
