<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>AgriVision Prototype</title>
  <script src="https://cdn.jsdelivr.net/npm/phaser@3.55.2/dist/phaser.min.js"></script>
  <style>
    body { margin:0; font-family: Arial, Helvetica, sans-serif; background:#f4f7f9; }
    #ui { position: absolute; top:10px; left:10px; width:360px; padding:12px; background:rgba(255,255,255,0.95); border-radius:8px; box-shadow:0 6px 18px rgba(0,0,0,0.08);}
    #ndvi { width: 330px; height: 180px; object-fit:cover; border-radius:6px; border:1px solid #ddd; }
    button { margin-top:8px; padding:8px 12px; border-radius:6px; border: none; cursor:pointer; background:#2b7cff; color:white; }
    .secondary { background:#666; }
    #messages { margin-top:8px; font-size:14px; color:#222; }
  </style>
</head>
<body>

<div id="ui">
  <h3>AgriVision — Mini Scenario</h3>
  <div>
    <img id="ndvi" src="https://earthengine.googleapis.com/v1/projects/angelic-ivy-473311-b3/thumbnails/44e9619e1c3d149e05c6bf79e087c571-db05b9e550e90b87d78f133c063f198d:getPixels" alt="NDVI"/>
  </div>
  <div style="margin-top:8px;">
    <label><strong>Crop:</strong> Olive Tree</label><br/>
    <label><strong>Soil type:</strong> Loam</label><br/>
    <label><strong>Root depth:</strong> 1.0 m</label>
  </div>

  <div style="margin-top:8px;">
    <button id="irrigateBtn">Irrigate today (20 mm)</button>
    <button id="skipBtn" class="secondary">Skip irrigation</button>
  </div>

  <div id="messages">Loading recent precipitation...</div>
</div>

<script>
(async function(){
  const messages = document.getElementById('messages');

  // NASA POWER API (your link) - precipitation for 2025-09-07 to 2025-09-13
  const url = "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=PRECTOTCORR&start=20250907&end=20250913&latitude=31.51&longitude=9.7&community=AG&format=JSON";

  try {
    const resp = await fetch(url);
    if(!resp.ok) throw new Error('Network response not OK');
    const data = await resp.json();
    const rainObj = data.properties.parameter.PRECTOTCORR;
    const entries = Object.entries(rainObj).map(([date,val])=>({date, val:+val}));
    const total = entries.reduce((s,e)=>s+e.val,0);
    messages.innerHTML = `<strong>Precipitation (7–13 Sep 2025):</strong> ${total.toFixed(1)} mm total<br/><em>Daily:</em> ${entries.map(e=>e.val.toFixed(1)).join(', ')}`;
  } catch (e) {
    messages.innerText = "Could not fetch precipitation — check network or CORS. (Error: "+e.message+")";
  }

  // Simple soil water model params (toy)
  let rootDepth = 1.0; // m
  let whc = 150; // mm/m for loam
  let fieldCapacity = whc * rootDepth; // mm
  let soilWater = fieldCapacity * 0.75; // start at 75% FC
  const cropKc = 0.65; // olive (toy)
  const ETo = 5.0; // mm/day (toy)
  const ETc = ETo * cropKc;

  function simulateDay(irrigation_mm, rain_mm) {
    soilWater = Math.min(fieldCapacity, soilWater + rain_mm + irrigation_mm - ETc);
    // simple stress check
    const stress = soilWater < (fieldCapacity * 0.3);
    return {soilWater: soilWater.toFixed(1), stress};
  }

  document.getElementById('irrigateBtn').onclick = () => {
    // apply 20 mm irrigation and average rain of last period (toy)
    const rainToday = 0; // assume no rain today
    const result = simulateDay(20, rainToday);
    messages.innerHTML += `<br/><br/><strong>Action:</strong> Irrigated 20 mm. Soil water = ${result.soilWater} mm. Stress: ${result.stress ? 'Yes' : 'No' }`;
    showTutorialPeek('Irrigation increased soil water; avoid overwatering—monitor root zone.');
  };

  document.getElementById('skipBtn').onclick = () => {
    const rainToday = 0;
    const result = simulateDay(0, rainToday);
    messages.innerHTML += `<br/><br/><strong>Action:</strong> Skipped irrigation. Soil water = ${result.soilWater} mm. Stress: ${result.stress ? 'Yes' : 'No' }`;
    showTutorialPeek('Skipping saves water but may cause crop stress if soil water drops below threshold.');
  };

  function showTutorialPeek(text){
    const t = document.createElement('div');
    t.style.marginTop='10px';
    t.style.padding='8px';
    t.style.background='#eef6ff';
    t.style.borderRadius='6px';
    t.innerHTML = `<strong>Tutorial:</strong> ${text}`;
    messages.appendChild(t);
  }

  // Minimal Phaser canvas below (visual only)
  const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 480,
    parent: null,
    backgroundColor: '#ffffff',
    scene: {
      preload: preload,
      create: create,
      update: update
    }
  };
  const game = new Phaser.Game(config);

  function preload(){ 
    this.load.image('olive', 'https://upload.wikimedia.org/wikipedia/commons/6/6c/Olive_tree%2C_Martwa.jpg'); 
  }
  function create(){
    this.add.text(420, 40, 'Scenario: Heatwave Incoming', {font:'18px Arial', fill:'#222'});
    this.add.image(570, 220, 'olive').setDisplaySize(320,220);
    this.add.text(420, 80, 'ETc (approx): ' + ETc.toFixed(1) + ' mm/day', {font:'14px Arial', fill:'#333'});
    this.add.text(420, 110, 'Field capacity: ' + fieldCapacity.toFixed(0) + ' mm', {font:'14px Arial', fill:'#333'});
  }
  function update(){}
})();
</script>

</body>
</html>
