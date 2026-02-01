const API = "https://YOUR-RENDER-URL.onrender.com";

function req(){
  fetch(API+"/request/account",{method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({email:email.value})
  });
}

function login(){
  fetch(API+"/customer/login",{method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({email:email.value,password:password.value})
  }).then(r=>r.json()).then(d=>exp.innerText=d.expires);
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
  fetch(API+"/staff/login",{method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({email:email.value,password:password.value})
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
