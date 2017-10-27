$(document).ready(function () {
                var hoy = new Date();
                dia = hoy.getDate(); 
                dia_salida = hoy.getDate()+1; 
                mes = hoy.getMonth()+1;
                anio= hoy.getFullYear();
                var fecha_actual = String(mes+"/"+dia+"/"+anio);
                var fecha_salida = String(mes+"/"+dia_salida+"/"+anio);
                fecha_actual = new Date(fecha_actual);
                 
                
                $('#date_checkin').datepicker({dateFormat:"mm/dd/yy"});
                $('#date_checkout').datepicker({dateFormat:"mm/dd/yy"});
                  
                    
                $( "#date_checkin" ).change(function() {
                    date_checkin=$('#date_checkin').val();
                    date_checkin=new Date(date_checkin);
                    if(date_checkin < fecha_actual){
                        alert('Fecha erronea, es menor a la fecha actual');
                        $('#date_checkin').datepicker("setDate",fecha_actual);
                        $('#date_checkout').datepicker("setDate",new Date(fecha_salida));
                    }
                    else{
                        dia_checkout=date_checkin.getDate()+1;
                        mes_checkout=date_checkin.getMonth()+1;
                        anio_checkout=date_checkin.getFullYear();
                        fecha_checkout=String(mes_checkout+"/"+dia_checkout+"/"+anio_checkout);
                        $('#date_checkout').datepicker("setDate",new Date(fecha_checkout));
                    }
                    
                    
                }); 
                $( "#date_checkout" ).change(function() {
                    date_checkin=$('#date_checkin').val();
                    date_checkout=$('#date_checkout').val();
                    date_checkin=new Date(date_checkin);
                    date_checkout=new Date(date_checkout);
                    if(date_checkin>date_checkout){
                        alert('Fechas erroneas, la Fecha es menor a la de llegada');
                        $('#date_checkout').datepicker("setDate",new Date(fecha_checkout));
                    }
                });
                
                
            });


