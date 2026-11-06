import json, math, time, urllib.request
d=json.load(open(__import__('sys').argv[1]))
G=[(c[1],c[0]) for c in d["geom"]]
def hv(a,b):
    R=6371000;p1,p2=math.radians(a[0]),math.radians(b[0]);dl=math.radians(b[1]-a[1]);dp=p2-p1
    return 2*R*math.asin(math.sqrt(math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2))
# dedupe + cumulative raw distance
P=[G[0]]
for p in G[1:]:
    if hv(P[-1],p)>1: P.append(p)
cum=[0]
for i in range(1,len(P)): cum.append(cum[-1]+hv(P[i-1],P[i]))
def project(pt):
    best=(1e18,0,None)
    for i in range(len(P)-1):
        a,b=P[i],P[i+1]; kx=math.cos(math.radians(a[0]))
        ax,ay,bx,by,px,py=a[1]*kx,a[0],b[1]*kx,b[0],pt[1]*kx,pt[0]
        dx,dy=bx-ax,by-ay; L=dx*dx+dy*dy or 1e-18
        t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/L)); q=(a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]))
        dd=hv(q,pt)
        if dd<best[0]: best=(dd,cum[i]+t*hv(a,b),q)
    return best
FORT_RAW=project((43.59034,7.12762))[1]; TOTAL=cum[-1]
def cal(raw):  # piecewise anchors: start 0, Fort Carré 21.1, finish 42.195
    return 1000*(raw/FORT_RAW*21.1 if raw<=FORT_RAW else 21.1+(raw-FORT_RAW)/(TOTAL-FORT_RAW)*21.095)
print("raw total",round(TOTAL/1000,2),"fort raw",round(FORT_RAW/1000,2))
# Douglas-Peucker simplify (~8 m)
def dp(pts,eps):
    if len(pts)<3: return pts
    a,b=pts[0],pts[-1]; dmax,idx=0,0
    for i in range(1,len(pts)-1):
        p=pts[i]; kx=math.cos(math.radians(a[0]))*111320; ky=110540
        ax,ay,bx,by,px,py=a[1]*kx,a[0]*ky,b[1]*kx,b[0]*ky,p[1]*kx,p[0]*ky
        dx,dy=bx-ax,by-ay; L=math.hypot(dx,dy) or 1e-9
        dd=abs(dy*px-dx*py+bx*ay-by*ax)/L
        if dd>dmax: dmax,idx=dd,i
    if dmax>eps: return dp(pts[:idx+1],eps)[:-1]+dp(pts[idx:],eps)
    return [a,b]
idx=list(range(len(P)))
S=dp([(p[0],p[1],i) for i,p in zip(idx,P)],8)
line=[[round(p[0],5),round(p[1],5),round(cal(cum[p[2]])/1000 if False else cal(cum[p[2]])/1000,3)] for p in S]
print("simplified points",len(line))
ST={"nice":(43.70483,7.26166),"staug":(43.66881,7.21058),"stl":(43.66239,7.19459),"cros":(43.66056,7.16713),"cagnes":(43.65773,7.14843),
 "vlp":(43.62924,7.13406),"biot":(43.61183,7.1262),"antibes":(43.58564,7.11944),"juan":(43.57102,7.11141),"gj":(43.56649,7.0736),"cannes":(43.55414,7.01976)}
SP_=[("start",(43.69563,7.26779),"nice"),("magnan",(43.6897,7.2442),"nice"),("airport",(43.6670,7.2105),"staug"),
 ("stlaurent",(43.65851,7.19733),"stl"),("cros",(43.6580,7.1680),"cros"),("plage",(43.6505,7.1500),"cagnes"),
 ("baie",(43.63414,7.13999),"vlp"),("biot",(43.61532,7.12608),"biot"),("fort",(43.59034,7.12762),"antibes"),
 ("port",(43.58679,7.12867),"antibes"),("salis",(43.5705,7.12871),"antibes"),("juan",(43.5681,7.11388),"juan"),
 ("gj",(43.56558,7.08036),"gj"),("palm",(43.53709,7.03669),"cannes"),("finish",(43.54825,7.03095),"cannes")]
out={"line":line,"spots":{}}
for sid,ll,st in SP_:
    dd,raw,q=project(ll)
    s=ST[st]; u=f"https://routing.openstreetmap.de/routed-foot/route/v1/foot/{s[1]},{s[0]};{q[1]},{q[0]}?overview=false"
    r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"race-spotter-dev/1.0"}),timeout=30))["routes"][0]
    walk=math.ceil(r["distance"]/1000/4.8*60)  # 4.8 km/h
    km=1e-3*cal(raw)
    out["spots"][sid]={"lat":round(q[0],5),"lon":round(q[1],5),"km":round(km,1),"walk":walk,"walk_m":round(r["distance"]),"off_m":round(dd)}
    print(f"{sid:10s} km {km:5.1f}  walk {walk:3d} min ({r['distance']:.0f} m)  landmark {dd:.0f} m from course")
    time.sleep(0.3)
km_finish=cal(TOTAL)/1000; print("check finish",round(km_finish,3))
json.dump(out,open(__import__('sys').argv[2],"w"))
