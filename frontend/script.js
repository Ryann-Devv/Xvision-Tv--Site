const API = "https://xvision-backend-ao7z.onrender.com/";

function req(){
  fetch(API+"/request/account",{method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({email:email.value})
  });
}

function login(){
  fetch(API+"/customer/login",{
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      email:email.value,
      password:password.value
    })
  })
  .then(r=>r.json())
  .then(d=>{
    if(d.expires){
      document.getElementById("exp").innerText = d.expires;
      document.getElementById("loginBox").style.display = "none";
      document.getElementById("portal").style.display = "block";
    } else {
      alert("Login failed");
    }
  });
}


function filmReq(){
  fetch(API+"/request/film",{method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({title:film.value})
  });
}

function support(){
  fetch(API+"/request/support",{method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({message:msg.value})
  });
}

function staffLogin(){
  fetch(API+"/staff/login",{
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      email:email.value,
      password:password.value
    })
  })
  .then(r=>r.json())
  .then(d=>{
    console.log("STAFF LOGIN RESPONSE:", d);

    if(d.email){
      document.getElementById("staffLogin").style.display="none";
      document.getElementById("staffPanel").style.display="block";
    } else {
      alert("Login failed");
    }
  })
  .catch(err=>{
    console.error(err);
    alert("Server error");
  });
}


function create(){
  fetch(API+"/staff/create",{method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      email:cemail.value,
      password:cpass.value,
      expires:cexp.value
    })
  });
}
