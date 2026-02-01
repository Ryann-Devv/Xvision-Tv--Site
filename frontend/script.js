const API = "https://YOUR-RENDER-APP.onrender.com";

// ---------- CUSTOMER ----------
function login(){
  fetch(API+"/customer/login",{
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      email:email.value,
      password:password.value
    })
  }).then(r=>r.json()).then(d=>{
    if(d.expires){
      loginBox.style.display="none";
      portal.style.display="block";
      exp.innerText=d.expires;
    } else alert("Login failed");
  });
}

function filmReq(){
  fetch(API+"/customer/film",{
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({email:email.value, film:film.value})
  });
}

function supportReq(){
  fetch(API+"/customer/support",{
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({email:email.value, message:msg.value})
  });
}

// ---------- STAFF ----------
function staffLogin(){
  fetch(API+"/staff/login",{
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({email:email.value,password:password.value})
  }).then(r=>r.json()).then(d=>{
    if(d.email){
      staffLoginBox.style.display="none";
      staffPanel.style.display="block";
    } else alert("Login failed");
  });
}

function createCustomer(){
  fetch(API+"/staff/create",{
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      email:cemail.value,
      password:cpass.value,
      expires:cexp.value
    })
  });
}
