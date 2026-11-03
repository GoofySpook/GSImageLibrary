// Living stills reel. Plate coordinates from top left. fx types:
// smoke{x,y,w,h,col,amt} fog{y,col,amt} light{x,y,r,col,amt,fl} eyes{x,y,x2,y2,r,col,t:[open,close],blink:[...]} lid{...}
// glint{x,y,x2,y2,w,t0,t1} orb{x,y,r,col} ; shot: cloth/flow/swing strengths use the _m.png mask
window.FILM={dur:23,drop:15.6,
SH:[
{s:0,e:3.6,a:'hero',z:[1.03,1.12],c:[.5,.3],d:[.6,-.3],cloth:.012,clothF:[10,2.6],part:{col:[1,.6,.2],v:[.02,.09],n:1,size:1},
 fx:[{k:'fog',y:.84,col:[1,.62,.28],amt:.75},{k:'light',x:.5,y:.3,r:.5,col:[1,.6,.25],amt:.28,fl:1}]},
{s:3.6,e:7,a:'hall',z:[1.04,1.08],c:[.40,.42],c2:[.60,.42],d:[.5,0],cloth:.020,clothF:[7,1.7],part:{col:[.9,.8,.7],v:[.012,.018],n:.8,size:.7},
 fx:[{k:'light',x:.5,y:.33,r:.14,col:[.45,.65,1],amt:.45,fl:.5},{k:'light',x:.37,y:.26,r:.13,col:[1,.3,.2],amt:.8,fl:1},{k:'light',x:.625,y:.26,r:.13,col:[1,.3,.2],amt:.8,fl:1},{k:'light',x:.12,y:.6,r:.3,col:[1,.6,.22],amt:.3,fl:1}]},
{s:7,e:10.1,a:'wood',z:[1.06,1.14],c:[.52,.56],d:[-.5,.3],swing:[.54,.525,.055,1.6],part:{col:[1,.72,.35],v:[.01,.02],n:.5,size:.7},
 fx:[{k:'light',x:.54,y:.635,r:.075,col:[1,.62,.2],amt:.75,fl:1.5,swing:1},{k:'light',x:.5,y:.92,r:.14,col:[1,.6,.2],amt:.3,fl:1.5},{k:'fog',y:.86,col:[.4,.5,.9],amt:.4}]},
{s:10.1,e:11.3,a:'wood',z:[1.32,1.36],c:[.45,.40],d:[.2,0],part:{col:[.7,.7,1],v:[.01,.01],n:.3,size:.6},
 fx:[{k:'eyes',x:.255,y:.335,x2:.335,y2:.325,r:.011,col:[1,.68,.2],on:10.25,bl:[10.8]},{k:'eyes',x:.60,y:.45,x2:.665,y2:.445,r:.009,col:[1,.5,.15],on:10.55,bl:[11.05]}]},
{s:11.3,e:12.4,a:'hood',z:[1.12,1.2],c:[.48,.38],d:[.1,0],part:{col:[.5,.7,.9],v:[.005,.01],n:.3,size:.6},
 fx:[{k:'lid',x:.27,y:.355,x2:.69,y2:.355,rx:.085,ry:.038,bl:[11.85]}]},
{s:12.4,e:15.6,a:'witch',z:[1.05,1.14],c:[.5,.48],d:[0,.6],flow:.012,part:{col:[.3,1,.6],v:[.012,.12],n:1,size:.9},
 fx:[{k:'smoke',x:.5,y:.7,w:.09,h:.62,col:[.2,1,.55],amt:.85},{k:'smoke',x:.34,y:.74,w:.045,h:.3,col:[.25,.9,.6],amt:.45},{k:'smoke',x:.7,y:.74,w:.05,h:.34,col:[.2,.9,.7],amt:.45},
 {k:'light',x:.5,y:.68,r:.26,col:[.25,1,.5],amt:.4,fl:1.2},{k:'eyes',x:.545,y:.31,x2:.61,y2:.38,r:.008,col:[.65,1,.75],on:13.4,bl:[]}]},
{s:15.6,e:17.6,a:'sword',z:[1.12,1.2],c:[.5,.52],d:[.3,-.3],part:{col:[1,.7,.3],v:[.02,.1],n:1,size:.8},
 fx:[{k:'glint',x:.64,y:.47,x2:.13,y2:.98,w:.04,t0:15.62,t1:16.2},{k:'light',x:.69,y:.43,r:.09,col:[1,.5,.1],amt:.6,fl:1}]},
{s:17.6,e:20.2,a:'mage',z:[1.04,1.12],c:[.42,.4],c2:[.32,.4],d:[.6,.2],flow:.009,part:{col:[.6,.9,1],v:[.018,.08],n:1,size:.9},
 fx:[{k:'orb',x:.115,y:.36,r:.055,col:[.45,.85,1]},{k:'fog',y:.92,col:[.5,.75,1],amt:.5}]}
],
CAP:[[.5,3.1,'SEVEN KNIGHTS RODE OUT AT DAWN'],[3.9,6.6,'THEIR BANNERS STILL HANG IN THE HALL'],[7.15,9.9,'THE ROAD HOME RUNS THROUGH THE DARK WOOD'],[10.25,12.3,'AND THE WOOD IS WATCHING'],[12.7,15.3,'SHE HAS KEPT THE FIRE LIT, FOR YOU'],[15.75,17.3,'DRAW STEEL'],[17.9,19.9,'OR CALL THE OLD FLAME']]};
