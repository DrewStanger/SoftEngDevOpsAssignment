class FormValidator {
    constructor(inputs) {
        this.inputs = inputs;
        this.validationRules = [];
    }

    addRule(regex, errorMessage) {
        this.validationRules.push({ regex, errorMessage });
    }

    validate() {
        for (let i = 0; i < this.inputs.length; i++) {
            const inputValue = this.inputs[i].value;
            const validationRule = this.validationRules[i];

            if (!validationRule.regex.test(inputValue)) {
                alert(validationRule.errorMessage);
                return false;
            }
        }
        return true;
    }
}

// Validation function for edit status form
function validateEditStatusForm() {
    const status = document.getElementById("status");
    const reason = document.getElementById("reason");
    
    const validator = new FormValidator([status, reason]);
    validator.addRule(/^[a-zA-Z0-9\s\-.,!?()'"\\/]+$/, "Status contains invalid characters");
    validator.addRule(/^[a-zA-Z0-9\s\-.,!?()'"\\/]+$/, "Reason contains invalid characters");

    return validator.validate();
}

// Validation function for login form and register form
function validateLoginForm() {
    return validateUserForm("username", "password");
}

function validateRegisterForm() {
    return validateUserForm("username", "password");
}

// Validation function for username and password
function validateUserForm(usernameId, passwordId) {
    const username = document.getElementById(usernameId);
    const password = document.getElementById(passwordId);

    const validator = new FormValidator([username, password]);
    validator.addRule(/^[a-zA-Z0-9]{4,20}$/, "Username must be 4-20 characters and alphanumeric");
    validator.addRule(/^.{8,}$/, "Password must be at least 8 characters");

    return validator.validate();
}