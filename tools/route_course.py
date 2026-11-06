import json, sys, math, urllib.request
W = [
 ("start",43.69540,7.26770),("negresco",43.69440,7.25780),("magnan",43.68930,7.24470),("carras",43.67760,7.22660),
 ("airport",43.66600,7.20900),("var_bridge",43.66378,7.19867),("stl_sea",43.65750,7.19300),("stl_port",43.65650,7.18300),
 ("cros_sea",43.65760,7.16900),("cagnes_plage",43.65504,7.15983),("vlp_road",43.62900,7.13500),("brague",43.61500,7.12750),
 ("fort",43.58811,7.12173),("port",43.58600,7.12550),("ramparts",43.57950,7.12900),("salis",43.57080,7.12950),
 ("garoupe",43.55822,7.13494),("cap_tip",43.54915,7.12045),("cap_w",43.55500,7.11600),("juan",43.56750,7.11300),
 ("guillaumont",43.56930,7.10760),("gj",43.56644,7.07632),("n7",43.55440,7.06010),("gazagnaire",43.54650,7.04620),
 ("palm",43.53780,7.03600),("finish",43.54830,7.03100)]
coords=";".join(f"{lon},{lat}" for _,lat,lon in W)
u=f"https://routing.openstreetmap.de/routed-foot/route/v1/foot/{coords}?overview=full&geometries=geojson"
r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"race-spotter-dev/1.0"}),timeout=60))["routes"][0]
def hv(a,b):
    R=6371000;p1,p2=math.radians(a[0]),math.radians(b[0]);dl=math.radians(b[1]-a[1]);dp=p2-p1
    return 2*R*math.asin(math.sqrt(math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2))
c=0
for i,l in enumerate(r["legs"]):
    c+=l["distance"];s=hv(W[i][1:],W[i+1][1:]);print(f"{W[i+1][0]:13s} km {c/1000:6.2f} ratio {l['distance']/s:4.2f}")
print("TOTAL",round(r["distance"]/1000,2))
json.dump({"w":W,"geom":r["geometry"]["coordinates"],"legs":[l["distance"] for l in r["legs"]]},open(sys.argv[1],"w"))
