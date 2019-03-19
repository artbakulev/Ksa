(function () {
    'use strict';
    window.addEventListener('load', function () {
        checkRepeatedFields();
        // Fetch all the forms we want to apply custom Bootstrap validation styles to
        let forms = document.getElementsByClassName('needs-validation');
        // Loop over them and prevent submission
        let validation = Array.prototype.filter.call(forms, function (form) {
            form.addEventListener('submit', function (event) {
                if (form.checkValidity() === false) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }, false);
})();

function checkRepeatedFields(){
    let fields = document.getElementsByClassName('repeat');
    if (fields === undefined)
        return false;
    let original_value, check_value;
    alert(fields[0]['repeat_field']);
    fields.forEach(function(item, index){
        check_value = item.value;
        original_value = document.getElementById(item['repeat_field']).value;
        if (check_value === original_value){
            alert("The same")
        }
        else {
            alert('Not the same')
        }
    });
}