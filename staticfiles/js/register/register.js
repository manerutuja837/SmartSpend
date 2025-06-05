console.log("Register Working")

const usernameField  = document.querySelector("#usernameField");
const feedbackArea = document.querySelector(".invalid_feedback");
const emailField = document.querySelector("#emailField");
const emailFeedbackArea = document.querySelector(".emailFeedbackArea");
const passwordField = document.querySelector("#passwordField");
const usernameSuccessOutput = document.querySelector(".usernameSuccessOutput");
const emailSuccessOutput = document.querySelector(".emailSuccessOutput");
const submitBtn = document.querySelector(".submit-btn");

const showPasswordToggle = document.querySelector(".showPasswordToggle");
const handleToggleInput = (e)=>{
  if(showPasswordToggle.textContent==="SHOW"){
    showPasswordToggle.textContent = "HIDE";
    passwordField.setAttribute("type","text");
  }else{
    showPasswordToggle.textContent = "SHOW";
    passwordField.setAttribute("type","password");
  }
}

showPasswordToggle.addEventListener('click',handleToggleInput);

emailField.addEventListener("keyup", (e) => {
  const emailVal = e.target.value;

  emailField.classList.remove("is-invalid");
  emailFeedbackArea.style.display = "none";

  emailSuccessOutput.style.display = "block";
  emailSuccessOutput.textContent =  `Checking ${emailVal}...`;

  if (emailVal.length > 0) {
    fetch("/authentication/validate-email/", {
      body: JSON.stringify({ email: emailVal }),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
            console.log("data",data)
            if(data.email_error){
              emailField.classList.add("is-invalid");
              emailSuccessOutput.style.display = "none";
              emailFeedbackArea.style.display = "block";
              emailFeedbackArea.innerHTML = `<p>${data.email_error}</p>`;
              submitBtn.setAttribute("disabled","disabled");
              submitBtn.disabled = True;
            }else {
              // If there's no error, remove the invalid class and hide feedback
              emailField.classList.remove("is-invalid");
              emailFeedbackArea.style.display = "none";
              emailSuccessOutput.style.display = "none";
              submitBtn.removeAttribute("disabled");
            }
        });
  }else {
    // Clear the error state if the input is empty
    emailField.classList.remove("is-invalid");
    emailFeedbackArea.style.display = "none";
  }
});

usernameField.classList.remove("is-invalid");
feedbackArea.style.display = "none";

usernameField.addEventListener("keyup", (e) => {
  const usernameVal = e.target.value;
  usernameSuccessOutput.style.display = "block";
  usernameSuccessOutput.textContent =  `Checking ${usernameVal}...`;
  if (usernameVal.length > 0) {
    fetch("/authentication/validate-username/", {
      body: JSON.stringify({ username: usernameVal }),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
            console.log("data",data)
            if(data.username_error){
              usernameField.classList.add("is-invalid");
              usernameSuccessOutput.style.display = "none";
              feedbackArea.style.display = "block";
              feedbackArea.innerHTML = `<p>${data.username_error}</p>`;
              submitBtn.setAttribute("disabled","disabled");
              submitBtn.disabled = True;
            }else {
              // If there's no error, remove the invalid class and hide feedback
              usernameField.classList.remove("is-invalid");
              usernameSuccessOutput.style.display = "none";
              feedbackArea.style.display = "none";
              submitBtn.removeAttribute("disabled");
            }
        });
  }else {
    // Clear the error state if the input is empty
    usernameField.classList.remove("is-invalid");
    feedbackArea.style.display = "none";
  }
});