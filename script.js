let username=""

let traits={
extraversion:0,
curiosity:0,
discipline:0,
empathy:0,
dominance:0,
risk:0,
loyalty:0,
stability:0
}

document.getElementById("startBtn").onclick=function(){

username=document.getElementById("username").value

if(username===""){
alert("Enter your name")
return
}

document.getElementById("startScreen").style.display="none"
document.getElementById("quiz").style.display="block"

loadQuestion()

}


function shuffle(array){

for(let i=array.length-1;i>0;i--){

let j=Math.floor(Math.random()*(i+1))

let temp=array[i]
array[i]=array[j]
array[j]=temp

}

return array

}


let questions = shuffle([...questionPool]).slice(0,20)

let currentQuestion=0


function loadQuestion(){

let q=questions[currentQuestion]

document.getElementById("question").innerText=q.text
document.getElementById("optionA").innerText=q.A
document.getElementById("optionB").innerText=q.B

updateProgress()

}


function updateProgress(){

let percent=((currentQuestion+1)/questions.length)*100

document.getElementById("progressText").innerText=
`Question ${currentQuestion+1} / ${questions.length}`

document.getElementById("progressBar").style.width=percent+"%"

}


function answer(choice){

let q=questions[currentQuestion]

let effect = choice==="A"?q.Aeffect:q.Beffect

for(let trait in effect){

traits[trait]+=effect[trait]

}

currentQuestion++

if(currentQuestion<questions.length){

loadQuestion()

}else{

finishTest()

}

}


document.getElementById("optionA").onclick=()=>answer("A")
document.getElementById("optionB").onclick=()=>answer("B")


function finishTest(){

document.getElementById("quiz").style.display="none"
document.getElementById("result").style.display="block"

document.getElementById("analysis").innerText="Analyzing..."


fetch("http://127.0.0.1:5000/analyze",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
name:username,
traits:traits
})

})
.then(res=>res.json())
.then(data=>{

document.getElementById("analysis").innerText=data.analysis

drawRadarChart()

})

}


function drawRadarChart(){

new Chart(

document.getElementById("traitChart"),

{

type:"radar",

data:{

labels:[
"Extraversion",
"Curiosity",
"Discipline",
"Empathy",
"Dominance",
"Risk",
"Loyalty",
"Stability"
],

datasets:[{

label:"Personality Traits",

data:[
traits.extraversion,
traits.curiosity,
traits.discipline,
traits.empathy,
traits.dominance,
traits.risk,
traits.loyalty,
traits.stability
],

backgroundColor:"rgba(56,189,248,0.2)",
borderColor:"#38bdf8"

}]

}

})

}