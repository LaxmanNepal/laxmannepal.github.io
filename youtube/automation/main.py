#!/usr/bin/env python3
"""Daily research -> Nepali script -> voice -> motion graphics -> optional publishing."""
from __future__ import annotations
import json, os, re, time, subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
import requests, feedparser
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"; OUT.mkdir(exist_ok=True)
CFG=json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
TODAY=datetime.now(timezone.utc).strftime("%Y-%m-%d")

def log(msg): print(f"[{datetime.now(timezone.utc).isoformat()}] {msg}",flush=True)

def rss_items(url,source):
    try:
        feed=feedparser.parse(requests.get(url,timeout=20,headers={"User-Agent":"LaxmanNepalTechShorts/1.0"}).text)
        out=[]
        for e in feed.entries[:25]:
            title=re.sub(r"\s+"," ",e.get("title","")).strip()
            summary=re.sub(r"<[^>]+>"," ",e.get("summary",""))
            if title and e.get("link"):
                out.append({"title":title,"summary":re.sub(r"\s+"," ",summary).strip()[:700],"url":e.link,"source":source,"published":e.get("published","")})
        return out
    except Exception as e:
        log(f"RSS unavailable ({source}): {e}"); return []

def research():
    q=requests.utils.quote(CFG["research"]["google_news_query"])
    items=rss_items(f"https://news.google.com/rss/search?q={q}+when:1d&hl=ne&gl=NP&ceid=NP:ne","Google News")
    items+=rss_items("https://trends.google.com/trending/rss?geo=NP","Google Trends")
    ytkey=os.getenv("YOUTUBE_API_KEY")
    if ytkey:
        for query in CFG["research"].get("youtube_queries",[]):
            try:
                data=requests.get("https://www.googleapis.com/youtube/v3/search",params={"part":"snippet","type":"video","order":"date","publishedAfter":(datetime.now(timezone.utc)-timedelta(hours=48)).isoformat(),"maxResults":5,"q":query,"regionCode":"NP","relevanceLanguage":"ne","key":ytkey},timeout=20).json()
                for x in data.get("items",[]):
                    s=x.get("snippet",{}); vid=x.get("id",{}).get("videoId","")
                    items.append({"title":s.get("title",""),"summary":s.get("description","")[:500],"url":"https://www.youtube.com/watch?v="+vid,"source":"YouTube search","published":s.get("publishedAt","")})
            except Exception as e: log(f"YouTube research unavailable: {e}")
    seen=set(); ranked=[]
    tech=re.compile(r"ai|artificial intelligence|technology|tech|digital|app|mobile|phone|internet|software|google|chatgpt|cyber|नेपाल|प्रविधि|एआई|मोबाइल|डिजिटल|एप|इन्टरनेट|सफ्टवेयर",re.I)
    now=datetime.now(timezone.utc)
    for x in items:
        key=re.sub(r"\W+","",x["title"].lower())
        if not key or key in seen: continue
        seen.add(key)
        try:
            dt=datetime.fromisoformat(x["published"].replace("Z","+00:00"))
            age=max(0,(now-dt).total_seconds()/3600)
        except Exception: age=24
        score=(5 if tech.search(x["title"]+" "+x["summary"]) else 0)+max(0,4-min(age,48)/12)
        if "Nepal" in x["title"] or "नेपाल" in x["title"]: score+=2
        x["score"]=round(score,2); ranked.append(x)
    ranked.sort(key=lambda x:x["score"],reverse=True)
    return ranked[:CFG["research"]["max_items"]]

def call_model(items,topic_override="",script_override=""):
    prompt=(ROOT/"prompts/nepali-tech-short.md").read_text(encoding="utf-8")
    user=prompt+"\n\nResearch input JSON:\n"+json.dumps({"date_utc":TODAY,"sources":items,"topic_override":topic_override,"script_override":script_override},ensure_ascii=False)
    ak=os.getenv("ANTHROPIC_API_KEY"); gk=os.getenv("GROQ_API_KEY")
    if ak:
        r=requests.post("https://api.anthropic.com/v1/messages",headers={"x-api-key":ak,"anthropic-version":"2023-06-01","content-type":"application/json"},json={"model":os.getenv("ANTHROPIC_MODEL","claude-3-5-haiku-latest"),"max_tokens":1800,"messages":[{"role":"user","content":user}]},timeout=60)
        r.raise_for_status(); raw="".join(z.get("text","") for z in r.json().get("content",[]) if z.get("type")=="text")
    elif gk:
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {gk}","Content-Type":"application/json"},json={"model":os.getenv("GROQ_MODEL","llama-3.3-70b-versatile"),"temperature":0.35,"response_format":{"type":"json_object"},"messages":[{"role":"user","content":user}]},timeout=60)
        r.raise_for_status(); raw=r.json()["choices"][0]["message"]["content"]
    else: raise RuntimeError("Add ANTHROPIC_API_KEY or GROQ_API_KEY to GitHub Actions Secrets. Claude Pro is not an API key.")
    raw=raw.replace(chr(96)*3+"json","").replace(chr(96)*3,"").strip()
    m=re.search(r"\{.*\}",raw,re.S)
    if not m: raise ValueError("AI did not return JSON: "+raw[:500])
    data=json.loads(m.group(0))
    if script_override.strip(): data["script"]=script_override.strip(); data["decision"]="MAKE"
    return data

def make_voice(script,path):
    key=os.getenv("ELEVENLABS_API_KEY"); voice=os.getenv("ELEVENLABS_VOICE_ID")
    if key and voice:
        try:
            r=requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",headers={"xi-api-key":key,"Content-Type":"application/json","Accept":"audio/mpeg"},json={"text":script,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.48,"similarity_boost":0.75}},timeout=120)
            r.raise_for_status(); path.write_bytes(r.content); return "ElevenLabs"
        except Exception as e: log(f"ElevenLabs failed; using gTTS: {e}")
    gTTS(text=script,lang="ne",slow=False).save(str(path)); return "gTTS Nepali"

def font(size,bold=False):
    paths=["/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for p in paths:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def wrap_text(draw,text,fnt,max_width):
    lines=[]; line=""
    for word in str(text).split():
        test=(line+" "+word).strip()
        if draw.textbbox((0,0),test,font=fnt)[2]<=max_width: line=test
        else:
            if line: lines.append(line)
            line=word
    if line: lines.append(line)
    return lines

def render_video(data,audio,video):
    p=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(audio)],capture_output=True,text=True,check=True)
    total=max(15.0,float(p.stdout.strip())+0.3); W,H=1080,1920
    phrases=[str(x) for x in (data.get("on_screen") or [data.get("hook","आजको टेक अपडेट"),data.get("topic","नेपाली टेक"),"यो कुरा उपयोगी हुन सक्छ","थप अपडेटका लागि Follow गर्नुहोस्"])[:5]]
    while len(phrases)<4: phrases.append("Laxman Nepal Official")
    tmp=OUT/"scenes"; tmp.mkdir(exist_ok=True); images=[]
    for i,phrase in enumerate(phrases):
        im=Image.new("RGB",(W,H),CFG["video"]["background"]); d=ImageDraw.Draw(im)
        d.rounded_rectangle((55,65,1025,1855),radius=48,outline=CFG["video"]["accent"],width=5)
        d.rounded_rectangle((90,105,990,175),radius=28,fill=CFG["video"]["accent"])
        d.text((125,125),"LAXMAN NEPAL  •  NEPALI TECH",font=font(31,True),fill="#06151D")
        d.text((95,260),f"DAILY TECH UPDATE / {i+1:02d}",font=font(29,True),fill="#71E4D3")
        d.rounded_rectangle((95,365,985,1470),radius=42,fill="#102638",outline="#29485C",width=3)
        f=font(66,True); lines=wrap_text(d,phrase,f,790); y=520+(700-len(lines)*100)//2
        for line in lines:
            d.text((145,y),line,font=f,fill="#FFFFFF",stroke_width=1,stroke_fill="#FFFFFF"); y+=100
        d.rounded_rectangle((95,1535,985,1660),radius=28,fill="#173B4B")
        d.text((135,1570),"सजिलो टेक • उपयोगी जानकारी",font=font(38,True),fill="#D9FFF8")
        d.text((100,1770),"@laxmannepalofficial",font=font(34,True),fill="#A9B8C4")
        pth=tmp/f"scene_{i:02d}.png"; im.save(pth); images.append(pth)
    per=total/len(images); cmd=["ffmpeg","-y"]
    for pth in images: cmd+=["-loop","1","-t",str(per),"-i",str(pth)]
    cmd+=["-i",str(audio)]; filters=[]
    for i in range(len(images)):
        frames=max(1,int(per*CFG["video"]["fps"]))
        filters.append(f"[{i}:v]scale=1080:1920,zoompan=z='min(zoom+0.00035,1.055)':d={frames}:s=1080x1920:fps={CFG['video']['fps']},trim=duration={per},setpts=PTS-STARTPTS[v{i}]")
    filters.append("".join(f"[v{i}]" for i in range(len(images)))+f"concat=n={len(images)}:v=1:a=0,format=yuv420p[v]")
    music=ROOT/CFG["video"].get("music_file","assets/background.mp3")
    if music.exists():
        cmd+=["-stream_loop","-1","-i",str(music)]
        filters += [f"[{len(images)+1}:a]volume=0.12,atrim=duration={total}[bg]",f"[{len(images)}:a][bg]amix=inputs=2:duration=first:dropout_transition=2[a]"]; amap="[a]"
    else: amap=f"{len(images)}:a"
    cmd+=["-filter_complex",";".join(filters),"-map","[v]","-map",amap,"-t",str(total),"-c:v","libx264","-preset","veryfast","-crf","22","-r",str(CFG["video"]["fps"]),"-c:a","aac","-b:a","128k","-movflags","+faststart",str(video)]
    subprocess.run(cmd,check=True,capture_output=True,text=True); return total

def youtube_upload(video,data):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    client=json.loads(os.environ["YOUTUBE_CLIENT_SECRETS_JSON"]); info=client.get("installed") or client.get("web")
    creds=Credentials(token=None,refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],token_uri=info["token_uri"],client_id=info["client_id"],client_secret=info["client_secret"],scopes=["https://www.googleapis.com/auth/youtube.upload"])
    creds.refresh(Request()); yt=build("youtube","v3",credentials=creds)
    desc=data.get("caption","")+"\n\nSources:\n"+"\n".join(s["url"] for s in data.get("sources",[]))
    body={"snippet":{"title":data["title"][:100],"description":desc,"tags":["Nepali Tech","Laxman Nepal","AI","Technology"],"categoryId":"28","defaultLanguage":"ne"},"status":{"privacyStatus":CFG["publishing"]["privacy_status"],"selfDeclaredMadeForKids":False}}
    result=yt.videos().insert(part="snippet,status",body=body,media_body=MediaFileUpload(str(video),mimetype="video/mp4",chunksize=-1,resumable=True)).execute()
    return {"id":result.get("id"),"url":"https://youtube.com/shorts/"+result.get("id","")}

def graph_post(path,token,params=None):
    r=requests.post(f"https://graph.facebook.com/{os.getenv('META_GRAPH_API_VERSION','v23.0')}/{path}",params={**(params or {}),"access_token":token},timeout=180)
    if not r.ok: raise RuntimeError(f"Meta API {r.status_code}: {r.text[:700]}")
    return r.json()

def facebook_reel(video,data):
    token=os.environ["META_PAGE_ACCESS_TOKEN"]; page=os.environ["META_PAGE_ID"]
    start=graph_post(f"{page}/video_reels",token,{"upload_phase":"start"}); vid=start["video_id"]
    upload=start.get("upload_url") or f"https://rupload.facebook.com/video-upload/{os.getenv('META_GRAPH_API_VERSION','v23.0')}/{vid}"
    size=video.stat().st_size
    with video.open("rb") as fh:
        r=requests.post(upload,data=fh,headers={"Authorization":f"OAuth {token}","offset":"0","file_size":str(size),"Content-Type":"application/octet-stream"},timeout=300)
    if not r.ok: raise RuntimeError(f"Facebook transfer failed: {r.status_code} {r.text[:500]}")
    return {"id":vid,"publish":graph_post(f"{page}/video_reels",token,{"video_id":vid,"upload_phase":"finish","video_state":"PUBLISHED","description":data.get("caption",""),"title":data.get("title","")})}

def instagram_reel(video,data):
    import boto3
    keys=["R2_ACCOUNT_ID","R2_ACCESS_KEY_ID","R2_SECRET_ACCESS_KEY","R2_BUCKET","R2_PUBLIC_BASE_URL"]
    missing=[k for k in keys if not os.getenv(k)]
    if missing: raise RuntimeError("Instagram requires public media hosting; missing R2 secrets: "+", ".join(missing))
    s3=boto3.client("s3",endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],region_name="auto")
    key=f"laxmannepal-shorts/{TODAY}-{int(time.time())}.mp4"
    s3.upload_file(str(video),os.environ["R2_BUCKET"],key,ExtraArgs={"ContentType":"video/mp4"})
    url=os.environ["R2_PUBLIC_BASE_URL"].rstrip("/")+"/"+key
    token=os.environ["META_PAGE_ACCESS_TOKEN"]; ig=os.environ["META_IG_USER_ID"]
    created=graph_post(f"{ig}/media",token,{"media_type":"REELS","video_url":url,"caption":data.get("caption","")+"\n"+" ".join(data.get("hashtags",[])),"share_to_feed":"true"})
    cid=created["id"]
    for _ in range(60):
        status=requests.get(f"https://graph.facebook.com/{os.getenv('META_GRAPH_API_VERSION','v23.0')}/{cid}",params={"fields":"status_code,status","access_token":token},timeout=30).json()
        if status.get("status_code")=="FINISHED": break
        if status.get("status_code")=="ERROR": raise RuntimeError(f"Instagram processing failed: {status}")
        time.sleep(10)
    else: raise RuntimeError("Instagram processing timed out.")
    return {"container_id":cid,"publish":graph_post(f"{ig}/media_publish",token,{"creation_id":cid})}

def main():
    topic=os.getenv("TOPIC_OVERRIDE","").strip(); script_override=os.getenv("SCRIPT_OVERRIDE","").strip()
    items=research(); (OUT/"research.json").write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding="utf-8")
    log(f"Collected {len(items)} research candidates.")
    data=call_model(items,topic,script_override)
    # Only allow source URLs actually discovered in the research stage; reject invented citations.
    allowed_urls={x["url"] for x in items}
    data["sources"]=[s for s in data.get("sources",[]) if isinstance(s,dict) and s.get("url") in allowed_urls]
    if data.get("decision")!="MAKE":
        (OUT/"latest.json").write_text(json.dumps({"status":"skipped","reason":"Evidence or topic strength insufficient","research":items},ensure_ascii=False,indent=2),encoding="utf-8")
        log("No suitable topic; safely skipped."); return
    for k in ["title","script","caption"]:
        if not data.get(k): raise ValueError("AI output missing "+k)
    if CFG["safety"]["require_sources"] and not data.get("sources"): raise ValueError("No source links returned; refusing unsourced video.")
    audio=OUT/"voice.mp3"; video=OUT/"laxmannepal-tech-short.mp4"
    provider=make_voice(data["script"].strip(),audio); duration=render_video(data,audio,video)
    report={"status":"ready","date_utc":TODAY,"channel":CFG["channel"],"topic":data.get("topic",""),"title":data["title"],"hook":data.get("hook",""),"script":data["script"].strip(),"caption":data["caption"],"hashtags":data.get("hashtags",[]),"sources":data.get("sources",[]),"fact_check":data.get("fact_check",[]),"voice_provider":provider,"duration_seconds":round(duration,1),"video_file":video.name,"created_at":datetime.now(timezone.utc).isoformat(),"publishing":{}}
    publish=os.getenv("PUBLISH_NOW","false").lower()=="true" and os.getenv("AUTO_PUBLISH","false").lower()=="true"
    if os.getenv("PUBLISH_NOW","false").lower()=="true" and not publish: log("AUTO_PUBLISH is not true; generated draft only.")
    if publish:
        for name,enabled,fn in [("youtube",CFG["publishing"].get("youtube"),youtube_upload),("facebook",CFG["publishing"].get("facebook"),facebook_reel),("instagram",CFG["publishing"].get("instagram"),instagram_reel)]:
            if not enabled: continue
            try: report["publishing"][name]={"status":"published","result":fn(video,data)}; log(name+" publish complete.")
            except Exception as e: report["publishing"][name]={"status":"failed","error":str(e)}; log(name+" publish failed: "+str(e))
    else: report["publishing"]={"status":"not_requested"}
    (OUT/"latest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    log(f"Video ready: {video} ({duration:.1f}s), voice={provider}")

if __name__=="__main__":
    try: main()
    except Exception as e: log("FATAL: "+str(e)); raise
