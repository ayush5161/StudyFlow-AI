function showOther(select){

let input = select.nextElementSibling

if(select.value === "others"){
input.style.display="inline-block"
}
else{
input.style.display="none"
}

}