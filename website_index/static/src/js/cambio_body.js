$(document).ready(function(){
        $("#btn_question").click(function() {
            question=$("input:radio[name=question]:checked").val();
            $("#"+question).modal('show');
            
        });
	});
// js del botón para reservación de paquetes.

    $( "#boton_abrir" ).click(function() {
      $( "#dialog" ).modal( "show" );
    });
    
    $( "#boton_abrir_user" ).click(function() {
        window.location.href =window.location.origin+"/web/login/";
    });

// js para modal de registro usuario en login.

    $( '#btn_registro') .click(function(){
        $( "#form_registro" ).modal( "show" );
    });



    $( '#reset_passwd') .click(function(){
       var login=($( "input:text[name=login]" ).val());
        if (login != ""){
            var ref= "http://"+document.domain+":8069/reset_passwd/"+login;
            window.location.href = ref;
       }
    });





