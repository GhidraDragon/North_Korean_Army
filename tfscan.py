import os
import re
import html
import time
import json
import random
import heapq
import sqlite3
import urllib.parse
import requests
import concurrent.futures
import sys
import traceback
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
from bs4 import BeautifulSoup
from test_sites import test_sites

try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

XSS_MODEL_PATH = "xss_js_model_tf.keras"
SQLI_MODEL_PATH = "sql_injection_model_tf.keras"
MULTI_MODELS_DIR = "ml_models_tf"
MAX_BODY_SNIPPET_LEN = 5000
ENABLE_HEADER_SCANNING = True
ENABLE_FORM_PARSING = True
CUSTOM_HEADERS = {"User-Agent":"ImprovedSecurityScanner/1.0"}

XSS_REGEXES = [
    r"<\s*script[^>]*?>.*?<\s*/\s*script\s*>",
    r"<\s*img[^>]+onerror\s*=.*?>",
    r"<\s*svg[^>]*on(load|error)\s*=",
    r"<\s*iframe\b.*?>",
    r"<\s*body\b[^>]*onload\s*=",
    r"javascript\s*:",
    r"<\s*\w+\s+on\w+\s*=",
    r"<\s*s\s*c\s*r\s*i\s*p\s*t[^>]*>",
    r"&#x3c;\s*script\s*&#x3e;",
    r"<scr(?:.*?)ipt>",
    r"</scr(?:.*?)ipt>",
    r"<\s*script[^>]*src\s*=.*?>",
    r"expression\s*\(",
    r"vbscript\s*:",
    r"mozbinding\s*:",
    r"javascript:alert\(document.domain\)",
    "<script src=['\"]http://[^>]*?>"
]

VULN_PATTERNS = {
    "SQL Error":re.compile(r"(sql\s*exception|sql\s*syntax|warning.*mysql.*|unclosed\s*quotation\s*mark|microsoft\s*ole\s*db\s*provider|odbc\s*sql\s*server\s*driver|pg_query\()",re.IGNORECASE|re.DOTALL),
    "SQL Injection":re.compile(r"(\bunion\s+select\s|\bselect\s+\*\s+from\s|\bsleep\(|\b'or\s+1=1\b|\b'or\s+'a'='a\b|--|#|xp_cmdshell|information_schema)",re.IGNORECASE|re.DOTALL),
    "XSS":re.compile("|".join(XSS_REGEXES),re.IGNORECASE|re.DOTALL),
    "Directory Listing":re.compile(r"(<title>\s*index of\s*/\s*</title>|directory\s+listing\s+for)",re.IGNORECASE|re.DOTALL),
    "File Inclusion":re.compile(r"(include|require)(_once)?\s*\(.*?http://",re.IGNORECASE|re.DOTALL),
    "Server Error":re.compile(r"(internal\s+server\s+error|500\s+internal|traceback\s*\(most\s+recent\s+call\s+last\))",re.IGNORECASE|re.DOTALL),
    "Shellshock":re.compile(r"\(\)\s*\{:\;};",re.IGNORECASE|re.DOTALL),
    "Remote Code Execution":re.compile(r"(exec\(|system\(|shell_exec\(|/bin/sh|eval\(|\bpython\s+-c\s)",re.IGNORECASE|re.DOTALL),
    "LFI/RFI":re.compile(r"(etc/passwd|boot.ini|\\\\\\\\\.\\\\pipe\\\\|\\\.\\pipe\\)",re.IGNORECASE|re.DOTALL),
    "SSRF":re.compile(r"(127\.0\.0\.1|localhost|metadata\.google\.internal)",re.IGNORECASE|re.DOTALL),
    "Path Traversal":re.compile(r"(\.\./\.\./|\.\./|\.\.\\)",re.IGNORECASE|re.DOTALL),
    "Command Injection":re.compile(r"(\|\||&&|;|/bin/bash|/bin/zsh)",re.IGNORECASE|re.DOTALL),
    "WordPress Leak":re.compile(r"(wp-content|wp-includes|wp-admin)",re.IGNORECASE|re.DOTALL),
    "Java Error":re.compile(r"(java\.lang\.|exception\s+in\s+thread\s+\"main\")",re.IGNORECASE|re.DOTALL),
    "Open Redirect":re.compile(r"(=\s*https?:\/\/)",re.IGNORECASE|re.DOTALL),
    "Deserialization":re.compile(r"(java\.io\.objectinputstream|ysoserial|__proto__|constructor\.prototype)",re.IGNORECASE|re.DOTALL),
    "XXE":re.compile(r"(<!doctype\s+[^>]*\[.*<!entity\s+[^>]*system)",re.IGNORECASE|re.DOTALL),
    "File Upload":re.compile(r"(multipart/form-data.*filename=)",re.IGNORECASE|re.DOTALL),
    "Prototype Pollution":re.compile(r"(\.__proto__|object\.prototype|object\.setprototypeof)",re.IGNORECASE|re.DOTALL),
    "NoSQL Injection":re.compile(r"(db\.\w+\.find\(|\$\w+\{|{\s*\$where\s*:)",re.IGNORECASE|re.DOTALL),
    "Exposed Git Directory":re.compile(r"(\.git/HEAD|\.gitignore|\.git/config)",re.IGNORECASE|re.DOTALL),
    "Potential Secrets":re.compile(r"(aws_access_key_id|aws_secret_access_key|api_key|private_key|authorization:\s*bearer\s+[0-9a-z\-_\.]+)",re.IGNORECASE|re.DOTALL),
    "JWT Token Leak":re.compile(r"(eyjh[a-z0-9_-]*\.[a-z0-9_-]+\.[a-z0-9_-]+)",re.IGNORECASE|re.DOTALL),
    "ETC Shadow Leak":re.compile(r"/etc/shadow",re.IGNORECASE|re.DOTALL),
    "Possible Password Leak":re.compile(r"(password\s*=\s*\w+)",re.IGNORECASE|re.DOTALL),
    "CC Leak":re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "CRLF Injection":re.compile(r"(\r\n|%0d%0a|%0A%0D)",re.IGNORECASE|re.DOTALL),
    "HTTP Request Smuggling":re.compile(r"(content-length:\s*\d+.*\r?\n\s*transfer-encoding:\s*chunked|transfer-encoding:\s*chunked.*\r?\n\s*content-length:\s*\d+)",re.IGNORECASE|re.DOTALL),
    "LDAP Injection":re.compile(r"(\(\w+=\*\)|\|\(\w+=\*\)|\(\w+~=\*)",re.IGNORECASE|re.DOTALL),
    "XPath Injection":re.compile(r"(/[^/]+/|\[[^\]]+\]|text\(\)=)",re.IGNORECASE|re.DOTALL),
    "Exposed S3 Bucket":re.compile(r"s3\.amazonaws\.com",re.IGNORECASE),
    "Exposed Azure Blob":re.compile(r"blob\.core\.windows\.net",re.IGNORECASE),
    "Exposed K8s Secrets":re.compile(r"kube[\s_-]*config|k8s[\s_-]*secret|kubeadm[\s_-]*token",re.IGNORECASE|re.DOTALL),
    "npm Token":re.compile(r"npm[_-]token_[a-z0-9]{36}",re.IGNORECASE|re.DOTALL)
}

HEADER_PATTERNS = {
    "Missing Security Headers":["Content-Security-Policy","X-Content-Type-Options","X-Frame-Options","X-XSS-Protection","Strict-Transport-Security"],
    "Outdated or Insecure Server":re.compile(r"(apache/2\.2\.\d|nginx/1\.10\.\d|iis/6\.0|php/5\.2)",re.IGNORECASE),
}

VULN_EXPLANATIONS = {
    "SQL Error":"Server returned DB error messages.",
    "SQL Injection":"Likely injection in SQL queries.",
    "XSS":"Injected client-side scripts.",
    "Directory Listing":"Exposed directory contents.",
    "File Inclusion":"Local/remote file inclusion.",
    "Server Error":"HTTP 500 or similar response.",
    "Shellshock":"Bash vulnerability discovered.",
    "Remote Code Execution":"User input can run code.",
    "LFI/RFI":"File references for inclusion.",
    "SSRF":"Server-Side Request Forgery found.",
    "Path Traversal":"Possible directory traversal.",
    "Command Injection":"Shell commands inserted.",
    "WordPress Leak":"WordPress paths or files.",
    "Java Error":"Java exceptions or traces.",
    "Open Redirect":"Redirects to external URL.",
    "Deserialization":"Unsafe object deserialization.",
    "XXE":"XML External Entity usage.",
    "File Upload":"Multipart form can upload.",
    "Prototype Pollution":"JS prototype manipulation.",
    "NoSQL Injection":"Mongo-like injection references.",
    "Exposed Git Directory":"Git config or HEAD visible.",
    "Potential Secrets":"API keys or tokens leaked.",
    "JWT Token Leak":"JWT tokens exposed.",
    "ETC Shadow Leak":"Reference to /etc/shadow.",
    "Missing Security Headers":"Key headers absent.",
    "Outdated or Insecure Server":"Old or insecure server.",
    "Cookies lack 'Secure'/'HttpOnly'":"Cookie flags missing.",
    "Suspicious param name:":"Param name looks malicious.",
    "Suspicious param value in":"Param value looks malicious.",
    "Form uses GET with password/hidden":"Sensitive data in GET.",
    "Suspicious form fields (cmd/shell/token)":"Malicious field names.",
    "POST form without CSRF token":"Form missing CSRF token.",
    "Service Disruption":"5xx errors or repeated failures.",
    "Possible Password Leak":"Possible credential leakage.",
    "CC Leak":"Credit card pattern found.",
    "CRLF Injection":"New line injection discovered.",
    "HTTP Request Smuggling":"Conflicting request headers found.",
    "LDAP Injection":"Possible directory service injection.",
    "XPath Injection":"Injected XPath queries.",
    "Exposed S3 Bucket":"Cloud storage might be public.",
    "Exposed Azure Blob":"Unsecured Azure blob container.",
    "Exposed K8s Secrets":"Kubernetes secrets possibly exposed.",
    "npm Token":"npm private token possibly leaked.",
    "No explanation":"No explanation"
}

def label_entry(label,tactic,snippet,confidence=1.0):
    e = VULN_EXPLANATIONS.get(label,"No explanation")
    return (label,tactic,snippet,e,confidence)

MULTI_VULN_SAMPLES = {
    "SQL Error":(["syntax error near 'FROM'","ODBC SQL server driver failed","error in your SQL syntax"],["normal query","sql logging enabled"]),
    "SQL Injection":(["UNION SELECT pass FROM users","' OR '1'='1","xp_cmdshell"],["SELECT id, name FROM product","UPDATE user set pass=?"]),
    "XSS":(["<script>alert('X')</script>","<img src=x onerror=alert(1)>","<svg onload=alert('svgxss')>"],["function hello(){}","var cleanVar=5;"]),
    "Directory Listing":(["<title>Index of /</title>"],["normal html"]),
    "File Inclusion":(["require(http://evil.com)","include(http://hack.site)"],["normal require","safe block"]),
    "Server Error":(["internal server error","Traceback (most recent call last)"],["ok response"]),
    "Shellshock":(["() { :;}; echo exploit"],["bash script safe"]),
    "Remote Code Execution":(["exec(","shell_exec(","system("],["safe()"]),
    "LFI/RFI":(["etc/passwd","boot.ini","../../etc/passwd"],["safe file read"]),
    "SSRF":(["127.0.0.1","localhost","metadata.google.internal"],["remote api call"]),
    "Path Traversal":(["../etc/passwd"],["safe path usage"]),
    "Command Injection":(["|| ls","&& whoami","; uname -a"],["normal usage"]),
    "WordPress Leak":(["wp-content","wp-admin"],["mention WP"]),
    "Java Error":(["java.lang.NullPointerException"],["normal logs"]),
    "Open Redirect":(["=http://","=https://"],["redirect internal"]),
    "Deserialization":(["java.io.ObjectInputStream","__proto__","ysoserial"],["normal data"]),
    "XXE":(["<!DOCTYPE foo [<!ENTITY"],["normal xml"]),
    "File Upload":(["multipart/form-data","filename="],["safe form"]),
    "Prototype Pollution":([".__proto__","Object.setPrototypeOf"],["normal js"]),
    "NoSQL Injection":(["db.users.find(","$where"],["normal nosql"]),
    "Exposed Git Directory":([".git/HEAD",".gitignore",".git/config"],["repo mention"]),
    "Potential Secrets":(["aws_secret_access_key","api_key","authorization: bearer 123abc"],["key param masked"]),
    "JWT Token Leak":(["eyJh.eyJ"],["normal token usage"]),
    "ETC Shadow Leak":(["/etc/shadow"],["safe reference"]),
    "Missing Security Headers":(["lack of csp, x-frame"],["csp present"]),
    "Outdated or Insecure Server":(["apache/2.2.14","nginx/1.10.3"],["apache/2.4","nginx/1.22"]),
    "Cookies lack 'Secure'/'HttpOnly'":(["set-cookie: sessionid=abc123"],["set-cookie: secure; httponly"]),
    "Suspicious param name:":(["cmd","shell","token"],["id","name"]),
    "Suspicious param value in":(["<script>","' or 1=1","%0d%0a"],["normal"]),
    "Form uses GET with password/hidden":(["<form method='get'><input type='password'>"],["<form method='post'>"]),
    "Suspicious form fields (cmd/shell/token)":(["name='cmd'"],["name='username'"]),
    "POST form without CSRF token":(["<form method='post'>"],["<form method='post'><input name='csrf'>"]),
    "Service Disruption":(["503 service unavailable","502 bad gateway"],["200 ok"]),
    "Possible Password Leak":(["password=secret"],["pwd=masked"]),
    "CC Leak":(["4111 1111 1111 1111"],["1111"]),
    "CRLF Injection":(["%0d%0a","\\r\\n"],["normal line break"]),
    "HTTP Request Smuggling":(["transfer-encoding: chunked\r\ncontent-length: 100"],["normal headers"]),
    "LDAP Injection":(["(cn=*)","|(objectClass=*)","(uid=*)"],["(cn=John)","(&(objectClass=person)(cn=John))"]),
    "XPath Injection":(["/users/user","text()='secret'","[contains(text(),'test')]"],["normal xml","legitimate xpath"]),
    "Exposed S3 Bucket":(["mybucket.s3.amazonaws.com","bucket.s3.amazonaws.com"],["normal usage"]),
    "Exposed Azure Blob":([".blob.core.windows.net"],["safe azure usage"]),
    "Exposed K8s Secrets":(["kubeconfig","k8s_secret","kubeadm token"],["kube cluster safe"]),
    "npm Token":(["npm_token_123456789012345678901234567890123456"],["safe usage"])
}

def build_text_model():
    text_input = tf.keras.Input(shape=(), dtype=tf.string)
    vectorizer = tf.keras.layers.TextVectorization(output_mode='int', max_tokens=1000)
    x = vectorizer(text_input)
    x = tf.keras.layers.Embedding(1000, 16)(x)
    x = tf.keras.layers.GlobalAveragePooling1D()(x)
    x = tf.keras.layers.Dense(16, activation='relu')(x)
    out = tf.keras.layers.Dense(1, activation='sigmoid')(x)
    model = tf.keras.Model(text_input, out)
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model, vectorizer

def train_tf_model(X_data, y_data, outpath):
    if not TENSORFLOW_AVAILABLE:
        return
    model, vectorizer = build_text_model()
    vectorizer.adapt(X_data)
    ds = tf.data.Dataset.from_tensor_slices((X_data, y_data)).batch(2)
    model.fit(ds, epochs=5, verbose=0)
    model.save(outpath)

def train_base_ml_models():
    if not TENSORFLOW_AVAILABLE:
        return
    if not os.path.exists(XSS_MODEL_PATH):
        sus_js = ["<script>alert('Hacked!')</script>","javascript:alert('XSS')","onerror=alert(document.cookie)","<img src=x onerror=alert(1)>","<svg onload=alert('svgxss')>","<script src='http://evil.com/x.js'></script>"]
        ben_js = ["function greetUser(name) {}","var x=5; if(x>2){x++;}","document.getElementById('x').innerText='Safe';","function normalFunc(){}"]
        X_data = sus_js + ben_js
        y_data = [1]*len(sus_js) + [0]*len(ben_js)
        train_tf_model(X_data, y_data, XSS_MODEL_PATH)

    if not os.path.exists(SQLI_MODEL_PATH):
        sus_sql = ["' OR '1'='1","UNION SELECT username, password FROM users","' OR 'a'='a","SELECT * FROM table WHERE id='","' DROP TABLE users --","xp_cmdshell","OR 1=1 LIMIT 1"]
        ben_sql = ["SELECT id, name FROM products","INSERT INTO users VALUES ('test','pass')","UPDATE accounts SET balance=500 WHERE userid=1","CREATE TABLE logs (entry TEXT)"]
        X_data = sus_sql + ben_sql
        y_data = [1]*len(sus_sql) + [0]*len(ben_sql)
        train_tf_model(X_data, y_data, SQLI_MODEL_PATH)

def train_all_vulnerability_models():
    if not TENSORFLOW_AVAILABLE:
        return
    if not os.path.isdir(MULTI_MODELS_DIR):
        os.makedirs(MULTI_MODELS_DIR)
    for vuln_name,(suspicious,benign) in MULTI_VULN_SAMPLES.items():
        model_path = os.path.join(MULTI_MODELS_DIR, f"{vuln_name.replace(' ','_').replace(':','').replace('/','_')}.keras")
        if not os.path.exists(model_path):
            X_data = suspicious + benign
            y_data = [1]*len(suspicious) + [0]*len(benign)
            train_tf_model(X_data, y_data, model_path)

def load_ml_model(path):
    if not TENSORFLOW_AVAILABLE or not os.path.exists(path):
        return None
    try:
        return tf.keras.models.load_model(path)
    except:
        return None

def ml_detection_confidence(snippet,model):
    if not model:
        return (0.0,False)
    pred = model.predict([snippet])[0][0]
    prob = float(pred)
    return (prob, prob>=0.5)

def normalize_and_decode(text):
    if not text:
        return text
    d1 = urllib.parse.unquote(text)
    d2 = html.unescape(d1)
    return d2.lower()

def multiple_decode_passes(text,passes=3):
    c = text
    for _ in range(passes):
        c = urllib.parse.unquote(c)
        c = html.unescape(c)
    return c.lower()

def scan_for_vuln_patterns(snippet):
    f = []
    n = normalize_and_decode(snippet)
    m = multiple_decode_passes(snippet,2)
    for label,pattern in VULN_PATTERNS.items():
        for match in pattern.finditer(n):
            s = match.group(0)
            if len(s)>200: s = s[:200]+"..."
            f.append(label_entry(label,"pattern-based detection",s))
        for match in pattern.finditer(m):
            s = match.group(0)
            if len(s)>200: s = s[:200]+"..."
            f.append(label_entry(label,"pattern-based detection",s))
    return list(set(f))

def dom_based_xss_detection(ht):
    r = []
    try:
        soup = BeautifulSoup(ht,"lxml")
    except:
        return r
    for s in soup.find_all("script"):
        if s.string and re.search(r"(alert|document\.cookie|<script)",s.string,re.IGNORECASE):
            sn = s.string.strip()
            if len(sn)>200: sn = sn[:200]+"..."
            r.append(label_entry("XSS","DOM-based detection",sn))
    for tag in soup.find_all():
        for attr in tag.attrs:
            if attr.lower().startswith("on"):
                a = f"{attr}={tag.attrs[attr]}"
                r.append(label_entry("XSS","DOM-based detection",a))
    return r

def scan_response_headers(headers):
    f = []
    if not headers:
        return f
    for h in HEADER_PATTERNS["Missing Security Headers"]:
        if h.lower() not in [k.lower() for k in headers.keys()]:
            f.append(label_entry("Missing Security Headers","header-based detection",h))
    srv = headers.get("Server","")
    p = HEADER_PATTERNS["Outdated or Insecure Server"]
    if p.search(srv):
        f.append(label_entry("Outdated or Insecure Server","header-based detection",srv))
    sc = headers.get("Set-Cookie","")
    if sc and ("secure" not in sc.lower() or "httponly" not in sc.lower()):
        f.append(label_entry("Cookies lack 'Secure'/'HttpOnly'","header-based detection",sc))
    return f

def parse_suspicious_forms(ht):
    r = []
    t = normalize_and_decode(ht)
    form_p = re.compile(r"<form\b.*?</form>",re.IGNORECASE|re.DOTALL)
    fs = form_p.findall(t)
    for f_ in fs:
        mm = re.search(r"method\s*=\s*(['\"])(.*?)\1",f_,re.IGNORECASE|re.DOTALL)
        c = f_[:200]+"..." if len(f_)>200 else f_
        if mm and mm.group(2).lower()=="get":
            if re.search(r"type\s*=\s*(['\"])(password|hidden)\1",f_,re.IGNORECASE):
                r.append(label_entry("Form uses GET with password/hidden","form-based detection",c))
        if re.search(r"name\s*=\s*(['\"])(cmd|shell|token)\1",f_,re.IGNORECASE):
            r.append(label_entry("Suspicious form fields (cmd/shell/token)","form-based detection",c))
        if mm and mm.group(2).lower()=="post" and not re.search(r"name\s*=\s*(['\"])(csrf|csrf_token)\1",f_,re.IGNORECASE):
            r.append(label_entry("POST form without CSRF token","form-based detection",c))
    return r

def analyze_query_params(url):
    from urllib.parse import urlparse,parse_qs
    f = []
    u = urlparse(url)
    qs = parse_qs(u.query)
    for p,vals in qs.items():
        dp = normalize_and_decode(p)
        if re.search(r"(cmd|exec|shell|script|token|redir|redirect)",dp,re.IGNORECASE):
            f.append(label_entry("Suspicious param name:","query-param detection",p))
        for v in vals:
            dv = normalize_and_decode(v)
            if re.search(r"(<>|<script>|' or 1=1|../../|jsessionid=|%0a|%0d)",dv,re.IGNORECASE):
                f.append(label_entry("Suspicious param value in","query-param detection",f"{p}={v}"))
    return f

def fuzz_injection_tests(url):
    fs = []
    pl = [
        "' OR '1'='1",
        "<script>alert(1)</script>",
        "; ls;",
        "&& cat /etc/passwd",
        "<img src=x onerror=alert(2)>",
        "'; DROP TABLE users; --",
        "|| ping -c 4 127.0.0.1 ||"
    ]
    for p in pl:
        time.sleep(random.uniform(1.2,2.5))
        try:
            tu = f"{url}?inj={urllib.parse.quote(p)}"
            r = requests.get(tu,timeout=3,headers=CUSTOM_HEADERS)
            fs.extend(scan_for_vuln_patterns(r.text))
        except:
            pass
    return fs

def fuzz_injection_tests_chromedriver(url):
    results = []
    if not SELENIUM_AVAILABLE:
        return results
    pl = [
        "' OR '1'='1",
        "<script>alert(1)</script>",
        "; ls;",
        "&& cat /etc/passwd",
        "<img src=x onerror=alert(2)>",
        "'; DROP TABLE users; --",
        "|| ping -c 4 127.0.0.1 ||"
    ]
    for payload in pl:
        injected_url = f"{url}?inj={urllib.parse.quote(payload)}"
        print(f"Running Chromedriver injection test: {injected_url}")
        try:
            o = Options()
            o.add_argument("--headless=new")
            d = webdriver.Chrome(options=o)
            d.get(injected_url)
            time.sleep(random.uniform(1.0,2.0))
            ps = d.page_source
            found = scan_for_vuln_patterns(ps)
            if found:
                for f_ in found:
                    print(f"Detected from Chromedriver injection test: {f_}")
                results.extend(found)
            d.quit()
        except Exception as e:
            print(f"Chromedriver injection test error on {injected_url}: {str(e)}")
    return list(set(results))

def repeated_disruption_test(url,attempts=3):
    f = []
    for _ in range(attempts):
        time.sleep(random.uniform(1.0,2.0))
        try:
            r = requests.get(url,timeout=3,headers=CUSTOM_HEADERS)
            if r.status_code>=500:
                f.append(label_entry("Service Disruption","frequent-request detection",str(r.status_code)))
        except:
            f.append(label_entry("Service Disruption","frequent-request detection","Exception"))
    return f

def extract_js_functions(ht):
    d = []
    sc = re.findall(r"<script[^>]*>(.*?)</script>",ht,re.IGNORECASE|re.DOTALL)
    for sb in sc:
        m = re.findall(r"(function\s+[a-zA-Z0-9_$]+\s*\([^)]*\)\s*\{.*?\})",sb,re.DOTALL)
        for mm in m:
            if len(mm)>400: mm = mm[:400]+"..."
            d.append(mm.strip())
    return d

def scan_target(url):
    ds = analyze_query_params(url)
    ds.extend(fuzz_injection_tests(url))
    ds.extend(fuzz_injection_tests_chromedriver(url))
    ds.extend(repeated_disruption_test(url))
    try:
        time.sleep(random.uniform(1.5,3.0))
        r = requests.get(url,timeout=5,headers=CUSTOM_HEADERS)
        b = r.text[:MAX_BODY_SNIPPET_LEN]
        p_tags = scan_for_vuln_patterns(b)
        h_tags = scan_response_headers(r.headers) if ENABLE_HEADER_SCANNING else []
        f_tags = parse_suspicious_forms(b) if ENABLE_FORM_PARSING else []
        d_tags = dom_based_xss_detection(b)
        ml_tags = []
        if TENSORFLOW_AVAILABLE:
            xm = load_ml_model(XSS_MODEL_PATH)
            sm = load_ml_model(SQLI_MODEL_PATH)
            if xm:
                scr_pat = re.compile(r"<script\b.*?>(.*?)</script>",re.IGNORECASE|re.DOTALL)
                for s_ in scr_pat.findall(b):
                    prob,pred = ml_detection_confidence(s_,xm)
                    if pred:
                        sn = s_.strip()
                        if len(sn)>200: sn = sn[:200]+"..."
                        ml_tags.append(label_entry("XSS",f"ML-based detection (score={prob:.3f})",sn,prob))
            if sm:
                prob,pred = ml_detection_confidence(b,sm)
                if pred:
                    sn = b[:200]+"..." if len(b)>200 else b
                    ml_tags.append(label_entry("SQL Injection",f"ML-based detection (score={prob:.3f})",sn,prob))
            for vn in MULTI_VULN_SAMPLES.keys():
                mp = os.path.join(MULTI_MODELS_DIR,f"{vn.replace(' ','_').replace(':','').replace('/','_')}.keras")
                mm = load_ml_model(mp)
                if mm:
                    prob,pred = ml_detection_confidence(b,mm)
                    if pred:
                        sn = b[:200]+"..." if len(b)>200 else b
                        ml_tags.append(label_entry(vn,f"ML-based detection (score={prob:.3f})",sn,prob))
        all_tags = ds + p_tags + h_tags + f_tags + d_tags + ml_tags
        funcs = extract_js_functions(r.text)
        return {
            "url":url,
            "status_code":r.status_code,
            "reason":r.reason,
            "server":r.headers.get("Server","Unknown"),
            "matched_details":all_tags,
            "extracted_js_functions":funcs,
            "body":r.text
        }
    except Exception as e:
        return {
            "url":url,
            "error":str(e),
            "matched_details":ds,
            "server":"Unknown",
            "extracted_js_functions":[],
            "body":""
        }

def write_scan_results_text(rs,filename="scan_results.txt"):
    with open(filename,"w",encoding="utf-8") as f:
        for r in rs:
            f.write(f"Server causing detection: {r.get('server','Unknown')}\n")
            f.write(f"URL: {r['url']}\n")
            if "error" in r:
                f.write(f"  Error: {r['error']}\n")
                for pt,tac,snip,ex,conf in r["matched_details"]:
                    f.write(f"    {pt}\n      Tactic: {tac}\n      Explanation: {ex}\n      Snippet: {snip}\n")
            else:
                f.write(f"  Status: {r['status_code']} {r['reason']}\n")
                if r["matched_details"]:
                    for pt,tac,snip,ex,conf in r["matched_details"]:
                        f.write(f"    {pt}\n      Tactic: {tac}\n      Explanation: {ex}\n      Snippet: {snip}\n")
            if r.get("extracted_js_functions"):
                f.write("  JS Functions:\n")
                for funcdef in r["extracted_js_functions"]:
                    f.write(f"    {funcdef}\n")
            f.write("\n")

def write_scan_results_json(rs):
    ts = time.strftime("%Y%m%d_%H%M%S")
    d = f"results_{ts}"
    try:
        os.makedirs(d,exist_ok=True)
    except:
        d="."
    op = os.path.join(d,"scan_results.json")
    o = []
    for r in rs:
        i = {
            "server":r.get("server","Unknown"),
            "url":r["url"],
            "status":None,
            "error":r.get("error",""),
            "detections":[],
            "extracted_js_functions":r.get("extracted_js_functions",[])
        }
        if "status_code" in r:
            i["status"] = f"{r.get('status_code','N/A')} {r.get('reason','')}"
        for pt,tac,snip,ex,conf in r["matched_details"]:
            i["detections"].append({
                "type":pt,"tactic":tac,"explanation":ex,"snippet":snip,"confidence":round(conf,3)
            })
        o.append(i)
    with open(op,"w",encoding="utf-8") as f:
        json.dump(o,f,indent=2)

def extract_links_from_html(url,html_text):
    links = set()
    try:
        soup = BeautifulSoup(html_text,"lxml")
        for a in soup.find_all("a",href=True):
            u = urllib.parse.urljoin(url,a["href"])
            if u.startswith("http"):
                links.add(u)
    except:
        pass
    return links

def scan_with_chromedriver(url):
    if not SELENIUM_AVAILABLE:
        return {"url":url,"error":"Selenium not available","data":"","found_flags":[]}
    try:
        time.sleep(random.uniform(1.0,2.0))
        o = Options()
        o.add_argument("--headless=new")
        d = webdriver.Chrome(options=o)
        d.get(url)
        found_flags = []
        try:
            forms = d.find_elements(By.TAG_NAME, "form")
            for form in forms:
                inputs = form.find_elements(By.TAG_NAME, "input")
                for inp in inputs:
                    try:
                        inp.send_keys("CTF_INJECTION_PAYLOAD")
                    except:
                        pass
                try:
                    form.submit()
                    time.sleep(1.5)
                    page_source_after_submit = d.page_source
                    matches = re.findall(r"(CTF\{.*?\})", page_source_after_submit, re.IGNORECASE)
                    if matches:
                        found_flags.extend(matches)
                except:
                    pass
        except:
            pass
        c = d.page_source
        matches_global = re.findall(r"(CTF\{.*?\})", c, re.IGNORECASE)
        if matches_global:
            found_flags.extend(matches_global)
        d.quit()
        return {"url":url,"error":"","data":c,"found_flags":list(set(found_flags))}
    except Exception as e:
        error_details = traceback.format_exc()
        return {"url":url,"error":f"{str(e)}\nTraceback:\n{error_details}","data":"","found_flags":[]}

from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

def google_style_page(results, depth):
    page = f"""<html><head><style>
    body {{ font-family: Arial, sans-serif; }}
    .search-bar {{ width: 500px; border:1px solid #ccc; padding:5px; }}
    .result {{ margin-bottom:10px; padding:5px; border-bottom:1px solid #ccc; }}
    </style></head><body>
    <div style="text-align:center;">
      <h1>Google Style Results for Depth {depth}</h1>
      <input class="search-bar" type="text" placeholder="Search..."/>
    </div>
    """
    for i, r_ in enumerate(results):
        page += f"<div class='result'><b>({i+1}) {r_['url']}</b><br>"
        if r_['error']:
            page += f"Error: {r_['error']}<br>"
        if r_['matched_details']:
            page += "<ul>"
            for pt,tac,snip,ex,cf in r_['matched_details']:
                page += f"<li>{pt} - {ex}</li>"
            page += "</ul>"
        page += "</div>"
    page += "</body></html>"
    return page

def serve_results_on_port_6999(results, depth):
    html_content = google_style_page(results, depth)
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_content.encode("utf-8"))
    server = HTTPServer(('0.0.0.0', 6999), Handler)
    t = threading.Thread(target=server.serve_forever)
    t.start()
    print(f"Serving updated results for depth {depth} on port 6999 for 5 seconds...")
    time.sleep(5)
    server.shutdown()
    t.join()

def priority_bfs_crawl_and_scan(starts,max_depth=20):
    visited = set()
    G = nx.DiGraph()
    depth_map = {}
    for s in starts:
        depth_map[s] = 0
        G.add_node(s,depth=0)
    results_by_depth = {}
    q = [(0,s) for s in starts]
    heapq.heapify(q)
    http_executor = concurrent.futures.ThreadPoolExecutor(max_workers=50)
    bot_executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    current_depth = 0
    while current_depth <= max_depth:
        depth_bucket = []
        while q and q[0][0] == current_depth:
            d,u = heapq.heappop(q)
            if u in visited:
                continue
            visited.add(u)
            f1 = http_executor.submit(scan_target,u)
            f2 = bot_executor.submit(scan_with_chromedriver,u)
            r1 = f1.result()
            r2 = f2.result()
            body1 = r1["body"] if "body" in r1 else ""
            body2 = r2["data"] if "data" in r2 else ""
            if "error" not in r1:
                extracted1 = extract_links_from_html(u,body1)
                for nl in extracted1:
                    if nl not in visited:
                        nd = current_depth+1
                        if nd<=max_depth:
                            heapq.heappush(q,(nd,nl))
                            depth_map[nl] = nd
                            G.add_node(nl,depth=nd)
                            G.add_edge(u,nl)
            if body2:
                extracted2 = extract_links_from_html(u,body2)
                for nl2 in extracted2:
                    if nl2 not in visited:
                        nd2 = current_depth+1
                        if nd2<=max_depth:
                            heapq.heappush(q,(nd2,nl2))
                            depth_map[nl2] = nd2
                            G.add_node(nl2,depth=nd2)
                            G.add_edge(u,nl2)
            combined_details = r1["matched_details"] if "matched_details" in r1 else []
            if r2["error"]:
                combined_details.append(label_entry("ChromeDriver Error","browser-based detection",r2["error"]))
            else:
                combined_details.extend(scan_for_vuln_patterns(body2))
            combined_js = r1.get("extracted_js_functions",[])
            if body2:
                combined_js.extend(extract_js_functions(body2))
            final = {
                "url":u,
                "server":r1.get("server","Unknown"),
                "status_code":r1.get("status_code","N/A"),
                "reason":r1.get("reason","N/A"),
                "error":r1.get("error","") or r2.get("error",""),
                "matched_details":combined_details,
                "extracted_js_functions":combined_js,
                "found_flags":r2.get("found_flags",[])
            }
            depth_bucket.append(final)
        if depth_bucket:
            results_by_depth[current_depth] = depth_bucket
            serve_results_on_port_6999(depth_bucket, current_depth)
        current_depth += 1
        if not q: 
            break

    http_executor.shutdown()
    bot_executor.shutdown()

    for layer in sorted(results_by_depth.keys()):
        layer_nodes = [r_['url'] for r_ in results_by_depth[layer]]
        subG = G.subgraph(layer_nodes)
        plt.figure(figsize=(8,6))
        pos = nx.spring_layout(subG, seed=42)
        nx.draw_networkx(subG, pos, with_labels=True)
        plt.title(f"Layer {layer}")
        plt.show()

    all_results = []
    for d_ in sorted(results_by_depth.keys()):
        all_results.extend(results_by_depth[d_])
    return all_results

def main():
    sys.stdout.reconfigure(line_buffering=True)
    train_base_ml_models()
    train_all_vulnerability_models()
    all_results = priority_bfs_crawl_and_scan(test_sites,20)
    for r in all_results:
        print(f"\nServer: {r.get('server','Unknown')} | {r['url']}")
        if "error" in r and r["error"]:
            print(f"  Error: {r['error']}")
        for pt,tactic,snippet,explanation,conf in r["matched_details"]:
            print(f"  Detected: {pt}\n    Explanation: {explanation}\n    Tactic: {tactic}\n    Snippet: {snippet}")
        if r.get("extracted_js_functions"):
            print("  Extracted JS Functions:")
            for f_ in r["extracted_js_functions"]:
                print(f"    {f_}")
        if r.get("found_flags"):
            print("  Found Flags:")
            for flg in r["found_flags"]:
                print(f"    {flg}")
    write_scan_results_text(all_results,"scan_results.txt")
    write_scan_results_json(all_results)

if __name__=="__main__":
    main()