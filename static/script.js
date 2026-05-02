let state = {};

function draw(){

    let g = document.getElementById("grid");
    let R = parseInt(rows.value);
    let C = parseInt(cols.value);

    g.style.gridTemplateColumns = `repeat(${C},60px)`;
    g.innerHTML = "";

    for(let i=0;i<R;i++){
        for(let j=0;j<C;j++){

            let d = document.createElement("div");
            d.className = "cell";

            if(state.visited?.some(v => v[0]==i && v[1]==j)){
                d.classList.add("safe");
            }

            if(state.agent && state.agent[0]==i && state.agent[1]==j){
                d.innerHTML = "🤖";
            }

            if(state.pits?.some(p => p[0]==i && p[1]==j)){
                d.classList.add("danger");
                d.innerHTML = "🕳️";
            }

            if(state.wumpus && state.wumpus[0]==i && state.wumpus[1]==j){
                d.classList.add("danger");
                d.innerHTML = "👹";
            }

            d.innerHTML += `<br>${i+1},${j+1}`;
            g.appendChild(d);
        }
    }
}


function updateDashboard(data){

    // visited count
    document.getElementById("visitedCount").innerText =
        data.visited.length;

    // KB update
    let kbDiv = document.getElementById("kb");
    kbDiv.innerHTML = "";

    data.kb.forEach(c => {
        let p = document.createElement("div");
        p.innerText = c;
        kbDiv.appendChild(p);
    });
}


function init(){
    fetch("/init",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
            rows:rows.value,
            cols:cols.value
        })
    })
    .then(r => r.json())
    .then(data => {
        state = data;
        updateDashboard(data);
        draw();
    });
}


function step(){
    fetch("/step",{method:"POST"})
    .then(r => r.json())
    .then(data => {

        state = data;

        let breeze = data.percepts.breeze
            ? `<span class="badge true">TRUE</span>`
            : `<span class="badge false">FALSE</span>`;

        let stench = data.percepts.stench
            ? `<span class="badge true">TRUE</span>`
            : `<span class="badge false">FALSE</span>`;

        let statusHTML = "";

        if(data.game_over){
            statusHTML = data.win
                ? `<div class="status-box">🏆 YOU WIN</div>`
                : `<div class="status-box">💀 GAME OVER</div>`;
        }

        document.getElementById("info").innerHTML =
        `Breeze: ${breeze} | Stench: ${stench} | Steps: ${data.steps} | Score: ${data.score} ${statusHTML}`;

        updateDashboard(data);
        draw();
    });
}

draw();