#!/usr/bin/env python3
import json, os, sys
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
import requests
from google.auth import transport
from google.oauth2 import service_account

OUT="analytics/data.json"; GA4_PROPERTY_ID=os.getenv("GA4_PROPERTY_ID","").strip()
GSC_SITE_URL=os.getenv("GSC_SITE_URL","").strip(); SERVICE_JSON=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON","").strip()
SCOPES=["https://www.googleapis.com/auth/analytics.readonly","https://www.googleapis.com/auth/webmasters.readonly"]

def fail(message): print(f"ERROR: {message}",file=sys.stderr); sys.exit(1)
if not SERVICE_JSON or not GA4_PROPERTY_ID or not GSC_SITE_URL: fail("Set GOOGLE_SERVICE_ACCOUNT_JSON, GA4_PROPERTY_ID and GSC_SITE_URL GitHub Secrets.")
try:
    info=json.loads(SERVICE_JSON); credentials=service_account.Credentials.from_service_account_info(info,scopes=SCOPES)
    credentials.refresh(transport.requests.Request()); session=requests.Session()
    session.headers.update({"Authorization":f"Bearer {credentials.token}"})
except Exception as exc: fail(f"Could not load service-account credentials: {exc}")

def ga4_report(dimensions,metrics,limit=10,start="90daysAgo",end="yesterday",order_metric=None,order_dimension=None):
    body={"dateRanges":[{"startDate":start,"endDate":end}],"dimensions":[{"name":d} for d in dimensions],"metrics":[{"name":m} for m in metrics],"limit":limit}
    if order_metric: body["orderBys"]=[{"metric":{"metricName":order_metric},"desc":True}]
    elif order_dimension: body["orderBys"]=[{"dimension":{"dimension":{"name":order_dimension}},"desc":False}]
    url=f"https://analyticsdata.googleapis.com/v1beta/properties/{quote(GA4_PROPERTY_ID,safe='')}:runReport"
    r=session.post(url,json=body,timeout=45)
    if not r.ok: raise RuntimeError(f"GA4 {r.status_code}: {r.text[:600]}")
    return r.json()

def rows(report):
    dims=[x["name"] for x in report.get("dimensionHeaders",[])]; mets=[x["name"] for x in report.get("metricHeaders",[])]
    return [dict(zip(dims,[x.get("value","") for x in row.get("dimensionValues",[])]))|{"metrics":dict(zip(mets,[x.get("value","0") for x in row.get("metricValues",[])]))} for row in report.get("rows",[])]

def gsc_query(dimensions,row_limit=100,start=None,end=None):
    url=f"https://searchconsole.googleapis.com/webmasters/v3/sites/{quote(GSC_SITE_URL,safe='')}/searchAnalytics/query"
    r=session.post(url,json={"startDate":start,"endDate":end,"dimensions":dimensions,"rowLimit":row_limit,"type":"web"},timeout=45)
    if not r.ok: raise RuntimeError(f"Search Console {r.status_code}: {r.text[:600]}")
    return r.json()

def gsc_rows(data):
    return [{"keys":row.get("keys",[]),"clicks":row.get("clicks",0),"impressions":row.get("impressions",0),"ctr":row.get("ctr",0),"position":row.get("position",0)} for row in data.get("rows",[])]

today=datetime.now(timezone.utc).date(); end=today-timedelta(days=1); current_start=today-timedelta(days=90)
previous_end=current_start-timedelta(days=1); previous_start=previous_end-timedelta(days=89)

try:
    overview_rows=rows(ga4_report([],["activeUsers","sessions","screenPageViews","engagementRate"],1)); overview=overview_rows[0]["metrics"] if overview_rows else {}
    sources=rows(ga4_report(["sessionDefaultChannelGroup"],["sessions"],10,order_metric="sessions"))
    pages=rows(ga4_report(["pagePath"],["screenPageViews"],20,order_metric="screenPageViews"))
    countries=rows(ga4_report(["country"],["activeUsers"],15,order_metric="activeUsers"))
    devices=rows(ga4_report(["deviceCategory"],["activeUsers"],10,order_metric="activeUsers"))
    events=rows(ga4_report(["eventName"],["eventCount"],50,order_metric="eventCount"))
    daily=rows(ga4_report(["date"],["activeUsers","sessions","screenPageViews","engagementRate"],1000,order_dimension="date"))
    previous_overview_rows=rows(ga4_report([],["activeUsers","sessions","screenPageViews","engagementRate"],1,start="181daysAgo",end="91daysAgo"))
    previous_overview=previous_overview_rows[0]["metrics"] if previous_overview_rows else {}

    cs=current_start.isoformat(); ce=end.isoformat(); ps=previous_start.isoformat(); pe=previous_end.isoformat()
    current_summary=gsc_rows(gsc_query([],start=cs,end=ce)); previous_summary=gsc_rows(gsc_query([],start=ps,end=pe))
    search_daily=gsc_rows(gsc_query(["date"],100,start=cs,end=ce))
    search_queries=gsc_rows(gsc_query(["query"],50,start=cs,end=ce)); previous_queries=gsc_rows(gsc_query(["query"],50,start=ps,end=pe))
    search_pages=gsc_rows(gsc_query(["page"],50,start=cs,end=ce)); previous_pages=gsc_rows(gsc_query(["page"],50,start=ps,end=pe))

    data={"schemaVersion":4,"generatedAt":datetime.now(timezone.utc).isoformat(),"range":"90 days ending yesterday",
          "comparison":{"current":{"start":cs,"end":ce},"previous":{"start":ps,"end":pe},"ga4":{"current":overview,"previous":previous_overview},
                       "searchConsole":{"current":current_summary,"previous":previous_summary}},
          "ga4":{"propertyId":GA4_PROPERTY_ID,"overview":overview,"sources":sources,"pages":pages,"countries":countries,"devices":devices,"events":events,"daily":daily},
          "searchConsole":{"site":GSC_SITE_URL,"startDate":cs,"endDate":ce,"summary":current_summary,"previousSummary":previous_summary,
                           "daily":search_daily,"queries":search_queries,"previousQueries":previous_queries,"pages":search_pages,"previousPages":previous_pages}}
except Exception as exc: fail(str(exc))
os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(OUT,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,separators=(",",":"))
print(f"Wrote {OUT}")
