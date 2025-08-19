import requests
import streamlit as st

RXNORM_BASE = "https://rxnav.nlm.nih.gov/REST"

def get_rxcui(drug_name: str) -> str | None:
    """حوّل اسم المادة الفعّالة إلى RxCUI من RxNorm."""
    try:
        resp = requests.get(f"{RXNORM_BASE}/rxcui.json", params={"name": drug_name.strip(), "search": 1}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        id_group = data.get("idGroup", {})
        rxcui = id_group.get("rxnormId", [None])
        return rxcui[0] if rxcui else None
    except Exception:
        return None

def get_interactions_by_rxcuis(rxcuis: list[str]) -> list[dict]:
    """يرجع قائمة بالتفاعلات بين كل الأزواج داخل المجموعة."""
    if not rxcuis:
        return []
    try:
        resp = requests.get(f"{RXNORM_BASE}/interaction/list.json", params={"rxcuis": "+".join(rxcuis)}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        out = []
        for grp in data.get("fullInteractionTypeGroup", []) or []:
            for ftype in grp.get("fullInteractionType", []) or []:
                # أطراف التفاعل
                drugs = [d.get("minConceptItem", {}).get("name") for d in ftype.get("minConcept", [])]
                pair_desc = ftype.get("comment")
                for pair in ftype.get("interactionPair", []) or []:
                    severity = pair.get("severity")
                    desc = pair.get("description")
                    sources = [s.get("name") for s in pair.get("interactionConcept", []) if s.get("sourceConceptItem")]
                    out.append({
                        "drugs": drugs,
                        "severity": severity,
                        "description": desc or pair_desc,
                        "sources": ", ".join(set(sources)) if sources else None
                    })
        return out
    except Exception:
        return []

def normalize_names(names_text: str) -> list[str]:
    # تقسيم بالألفاص والفواصل والمسافات
    raw = [x.strip() for x in names_text.replace("،", ",").split(",")]
    # حذف الفارغ
    return [x for x in raw if x]

st.set_page_config(page_title="فاحص التفاعلات الدوائية", page_icon="💊", layout="centered")

st.title("💊 فاحص التفاعلات الدوائية")
st.caption("أدخل أسماء المواد الفعالة (Generic) بالعربية أو الإنجليزية. يعتمد على قاعدة RxNav (NIH).")

names = st.text_input("اكتب أسماء المواد الفعالة وافصل بينهم بفاصلة (مثال: amoxicillin, warfarin):")
btn = st.button("افحص التفاعلات")

if btn:
    inputs = normalize_names(names)
    if len(inputs) < 2:
        st.warning("من فضلك أدخل على الأقل دوائين.")
    else:
        with st.spinner("جارِ البحث..."):
            # حوّل لكل اسم → RxCUI
            mapping = {}
            for n in inputs:
                rxcui = get_rxcui(n)
                mapping[n] = rxcui

            # عرض أي أسماء فشل تحويلها
            not_found = [k for k, v in mapping.items() if not v]
            if not_found:
                st.error("تعذر التعرف على: " + "، ".join(not_found) + " — جرّب تهجئة إنجليزية للـ Generic أو اسم بديل.")

            # جهّز قائمة الـ RxCUI الصالحة
            rxcuis = [v for v in mapping.values() if v]
            interactions = get_interactions_by_rxcuis(rxcuis) if len(rxcuis) >= 2 else []

        st.subheader("النتائج")
        # خريطة الاسم ← RxCUI
        with st.expander("تطابق الأسماء (Name → RxCUI)"):
            for name_in, rx in mapping.items():
                st.write(f"- *{name_in}* → {rx if rx else 'لم يُعثر عليه'}")

        if not interactions:
            st.info("لا توجد تفاعلات مسجلة بين هذه المجموعة في قاعدة RxNav، أو لم يتم العثور على تعريفات لبعض الأدوية.")
        else:
            # ترتيب حسب الشدة (إن وُجدت)
            severity_order = {"high": 0, "contraindicated": 0, "moderate": 1, "low": 2, None: 3}
            interactions.sort(key=lambda x: severity_order.get((x["severity"] or "").lower(), 3))
            for i, item in enumerate(interactions, 1):
                sev = item["severity"]
                drugs = " + ".join(filter(None, item["drugs"])) if item["drugs"] else "Pair"
                st.markdown(f"### {i}. {drugs}")
                st.write(f"*درجة الخطورة:* {sev if sev else 'غير محددة'}")
                st.write(item["description"] or "لا يوجد وصف متاح.")
                if item["sources"]:
                    st.caption(f"المصدر: {item['sources']}")
            st.success(f"تم العثور على {len(interactions)} تفاعل(ات).")

st.divider()
st.markdown("#made by Mohammed Mostafa")
POST /ws/pidbws.asmx HTTP/1.1
Host: www.pidb.dk
Content-Type: text/xml; charset=utf-8
Content-Length: length
SOAPAction: "https://www.pidb.dk/WS/XML_Dato_2"

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <XML_Dato_2 xmlns="https://www.pidb.dk/WS">
      <AccessKey>string</AccessKey>
    </XML_Dato_2>
  </soap:Body>
</soap:Envelope>
HTTP/1.1 200 OK
Content-Type: text/xml; charset=utf-8
Content-Length: length

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <XML_Dato_2Response xmlns="https://www.pidb.dk/WS">
      <XML_Dato_2Result>
        <ID_XML_Dokument>string</ID_XML_Dokument>
        <XML_Type>string</XML_Type>
        <XML_Navn>string</XML_Navn>
        <XML_Size>string</XML_Size>
        <XML_Dato_Tid>string</XML_Dato_Tid>
      </XML_Dato_2Result>
    </XML_Dato_2Response>
  </soap:Body>
</soap:Envelope>
SOAP 1.2
The following is a sample SOAP 1.2 request and response. The placeholders shown need to be replaced with actual values.

POST /ws/pidbws.asmx HTTP/1.1
Host: www.pidb.dk
Content-Type: application/soap+xml; charset=utf-8
Content-Length: length

<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <XML_Dato_2 xmlns="https://www.pidb.dk/WS">
      <AccessKey>string</AccessKey>
    </XML_Dato_2>
  </soap12:Body>
</soap12:Envelope>
HTTP/1.1 200 OK
Content-Type: application/soap+xml; charset=utf-8
Content-Length: length

<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <XML_Dato_2Response xmlns="https://www.pidb.dk/WS">
      <XML_Dato_2Result>
        <ID_XML_Dokument>string</ID_XML_Dokument>
        <XML_Type>string</XML_Type>
        <XML_Navn>string</XML_Navn>
        <XML_Size>string</XML_Size>
        <XML_Dato_Tid>string</XML_Dato_Tid>
      </XML_Dato_2Result>
    </XML_Dato_2Response>
  </soap12:Body>
</soap12:Envelope>
HTTP GET
The following is a sample HTTP GET request and response. The placeholders shown need to be replaced with actual values.

GET /ws/pidbws.asmx/XML_Dato_2?AccessKey=string HTTP/1.1
Host: www.pidb.dk
HTTP/1.1 200 OK
Content-Type: text/xml; charset=utf-8
Content-Length: length

<?xml version="1.0" encoding="utf-8"?>
<XML_Dato_Doc xmlns="https://www.pidb.dk/WS">
  <ID_XML_Dokument>string</ID_XML_Dokument>
  <XML_Type>string</XML_Type>
  <XML_Navn>string</XML_Navn>
  <XML_Size>string</XML_Size>
  <XML_Dato_Tid>string</XML_Dato_Tid>
</XML_Dato_Doc>
HTTP POST
The following is a sample HTTP POST request and response. The placeholders shown need to be replaced with actual values.

POST /ws/pidbws.asmx/XML_Dato_2 HTTP/1.1
Host: www.pidb.dk
Content-Type: application/x-www-form-urlencoded
Content-Length: length

AccessKey=string
HTTP/1.1 200 OK
Content-Type: text/xml; charset=utf-8
Content-Length: length

<?xml version="1.0" encoding="utf-8"?>
<XML_Dato_Doc xmlns="https://www.pidb.dk/WS">
  <ID_XML_Dokument>string</ID_XML_Dokument>
  <XML_Type>string</XML_Type>
  <XML_Navn>string</XML_Navn>
  <XML_Size>string</XML_Size>
  <XML_Dato_Tid>string</XML_Dato_Tid>
</XML_Dato_Doc>
POST /ws/pidbws.asmx HTTP/1.1
Host: www.pidb.dk
Content-Type: text/xml; charset=utf-8
Content-Length: length
SOAPAction: "https://www.pidb.dk/WS/XML_Dato_4"

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <XML_Dato_4 xmlns="https://www.pidb.dk/WS">
      <AccessKey>string</AccessKey>
    </XML_Dato_4>
  </soap:Body>
</soap:Envelope>
HTTP/1.1 200 OK
Content-Type: text/xml; charset=utf-8
Content-Length: length

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <XML_Dato_4Response xmlns="https://www.pidb.dk/WS">
      <XML_Dato_4Result>
        <ID_XML_Dokument>string</ID_XML_Dokument>
        <XML_Type>string</XML_Type>
        <XML_Navn>string</XML_Navn>
        <XML_Size>string</XML_Size>
        <XML_Dato_Tid>string</XML_Dato_Tid>
      </XML_Dato_4Result>
    </XML_Dato_4Response>
  </soap:Body>
</soap:Envelope>
SOAP 1.2
The following is a sample SOAP 1.2 request and response. The placeholders shown need to be replaced with actual values.

POST /ws/pidbws.asmx HTTP/1.1
Host: www.pidb.dk
Content-Type: application/soap+xml; charset=utf-8
Content-Length: length

<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <XML_Dato_4 xmlns="https://www.pidb.dk/WS">
      <AccessKey>string</AccessKey>
    </XML_Dato_4>
  </soap12:Body>
</soap12:Envelope>
HTTP/1.1 200 OK
Content-Type: application/soap+xml; charset=utf-8
Content-Length: length

<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <XML_Dato_4Response xmlns="https://www.pidb.dk/WS">
      <XML_Dato_4Result>
        <ID_XML_Dokument>string</ID_XML_Dokument>
        <XML_Type>string</XML_Type>
        <XML_Navn>string</XML_Navn>
        <XML_Size>string</XML_Size>
        <XML_Dato_Tid>string</XML_Dato_Tid>
      </XML_Dato_4Result>
    </XML_Dato_4Response>
  </soap12:Body>
</soap12:Envelope>
HTTP GET
The following is a sample HTTP GET request and response. The placeholders shown need to be replaced with actual values.

GET /ws/pidbws.asmx/XML_Dato_4?AccessKey=string HTTP/1.1
Host: www.pidb.dk
HTTP/1.1 200 OK
Content-Type: text/xml; charset=utf-8
Content-Length: length

<?xml version="1.0" encoding="utf-8"?>
<XML_Dato_Doc xmlns="https://www.pidb.dk/WS">
  <ID_XML_Dokument>string</ID_XML_Dokument>
  <XML_Type>string</XML_Type>
  <XML_Navn>string</XML_Navn>
  <XML_Size>string</XML_Size>
  <XML_Dato_Tid>string</XML_Dato_Tid>
</XML_Dato_Doc>
HTTP POST
The following is a sample HTTP POST request and response. The placeholders shown need to be replaced with actual values.

POST /ws/pidbws.asmx/XML_Dato_4 HTTP/1.1
Host: www.pidb.dk
Content-Type: application/x-www-form-urlencoded
Content-Length: length

AccessKey=string
HTTP/1.1 200 OK
Content-Type: text/xml; charset=utf-8
Content-Length: length

<?xml version="1.0" encoding="utf-8"?>
<XML_Dato_Doc xmlns="https://www.pidb.dk/WS">
  <ID_XML_Dokument>string</ID_XML_Dokument>
  <XML_Type>string</XML_Type>
  <XML_Navn>string</XML_Navn>
  <XML_Size>string</XML_Size>
  <XML_Dato_Tid>string</XML_Dato_Tid>
</XML_Dato_Doc>
POST /ws/pidbws.asmx HTTP/1.1
Host: www.pidb.dk
Content-Type: text/xml; charset=utf-8
Content-Length: length
SOAPAction: "https://www.pidb.dk/WS/XML_Download"

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <XML_Download xmlns="https://www.pidb.dk/WS">
      <AccessKey>string</AccessKey>
      <ID_XML_Dokument>string</ID_XML_Dokument>
    </XML_Download>
  </soap:Body>
</soap:Envelope>
HTTP/1.1 200 OK
Content-Type: text/xml; charset=utf-8
Content-Length: length

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <XML_DownloadResponse xmlns="https://www.pidb.dk/WS">
      <XML_DownloadResult>xml</XML_DownloadResult>
    </XML_DownloadResponse>
  </soap:Body>
</soap:Envelope>
SOAP 1.2
The following is a sample SOAP 1.2 request and response. The placeholders shown need to be replaced with actual values.

POST /ws/pidbws.asmx HTTP/1.1
Host: www.pidb.dk
Content-Type: application/soap+xml; charset=utf-8
Content-Length: length

<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <XML_Download xmlns="https://www.pidb.dk/WS">
      <AccessKey>string</AccessKey>
      <ID_XML_Dokument>string</ID_XML_Dokument>
    </XML_Download>
  </soap12:Body>
</soap12:Envelope>
HTTP/1.1 200 OK
Content-Type: application/soap+xml; charset=utf-8
Content-Length: length

<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <XML_DownloadResponse xmlns="https://www.pidb.dk/WS">
      <XML_DownloadResult>xml</XML_DownloadResult>
    </XML_DownloadResponse>
  </soap12:Body>
</soap12:Envelope>
HTTP GET
The following is a sample HTTP GET request and response. The placeholders shown need to be replaced with actual values.

GET /ws/pidbws.asmx/XML_Download?AccessKey=string&ID_XML_Dokument=string HTTP/1.1
Host: www.pidb.dk
HTTP/1.1 200 OK
Content-Type: text/xml; charset=utf-8
Content-Length: length

<?xml version="1.0"?>
xml
HTTP POST
The following is a sample HTTP POST request and response. The placeholders shown need to be replaced with actual values.

POST /ws/pidbws.asmx/XML_Download HTTP/1.1
Host: www.pidb.dk
Content-Type: application/x-www-form-urlencoded
Content-Length: length

AccessKey=string&ID_XML_Dokument=string
HTTP/1.1 200 OK
Content-Type: text/xml; charset=utf-8
Content-Length: length

<?xml version="1.0"?>
xml
