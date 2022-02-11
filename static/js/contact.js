function checkDetails() {
    fullname = document.getElementById('nameId').value;
    email = document.getElementById('email').value;
    msg = document.getElementById('msg').value;

    nameReq = document.getElementById('nameReq');
    emailReq = document.getElementById('emailReq');
    msgReg = document.getElementById('msgReq');

    if(fullname.length <= 3){
        var text = "Name should contain atleast 3 Characters.";
        nameReq.classList.add('is-danger');
        nameReq.style.display = "block";
        nameReq.innerHTML = text;
        return false;
    }else{
        nameReq.innerHTML = '';
    };

    var mailformat = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    if(!email.match(mailformat)){
        var text = "You have entered an invalid email address!";
        emailReq.classList.add('is-danger');
        emailReq.style.display = "block";
        emailReq.innerHTML = text;
        return false;
    }else{
        emailReq.innerHTML = '';
    }

    if(msg.length <= 10){
        text = "Please Enter More Than 10 Characters";
        msgReg.classList.add('is-danger');
        msgReg.style.display = "block";
        msgReq.innerHTML = text;
        return false;
    }else{
        msgReg.innerHTML = '';
    }


    return true;
}