otpForm = document.getElementById('otpForm');
const otp = document.getElementById('otpcode');

const showError = (message, whichEl) => {

    // add the error class
    whichEl.style.display = 'block';

    // show the error message
    whichEl.innerHTML = message;
};

const showSuccess = (whichSc) => {
    
    // remove the error class
    whichSc.style.display = 'none';

    // hide the error message
    whichSc.innerHTML = '';
}


const checkOTP = () => {
    const otpReq = document.getElementById('otpReq');
    let valid = false;
    const otpVal = otp.value.trim();

    if(otpVal.length != 6){
        showError('OTP should consists of 6 characters', otpReq);
    } else if(isNaN(otpVal)){
        showError('OTP should consists of numbers only', otpReq);
    } else{
        showSuccess(otpReq);
        valid = true;
    };
    return valid;
};

otpForm.addEventListener('submit', function(e){
    e.preventDefault();

    let isOTPValid = checkOTP();

    if (isOTPValid) {
        console.log('correct');
        otpForm.submit();
        console.log('form submitted');
    };

})