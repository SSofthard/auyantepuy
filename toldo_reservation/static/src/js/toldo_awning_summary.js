 openerp.toldo_reservation = function(openerp) {
    var _t = openerp.web._t;
    _lt = openerp.web._lt;
    var QWebs = openerp.web.qweb;
    
    openerp.toldo_reservation.AwningSummary = openerp.web.form.FormWidget.extend(openerp.web.form.ReinitializeWidgetMixin, {
    	
    	display_names: _lt('Form'),
        view_type:"form",
        
        init: function() {
            this._super.apply(this, arguments);
	    	if(this.field_manager.model == "awning.reservation.summary")
	    	{
	    		$(".oe_view_manager_buttons").hide();
	    		$(".oe_view_manager_header").hide();
	   		}
            this.set({
                dates_to: false,
                dates_from: false,
                summary_headers: false,
                awning_summary: false,
            });
            this.summary_headers = [];
            this.awning_summary = [];
            this.field_manager.on("field_changed:dates_from", this, function() {
                this.set({"dates_from": openerp.web.str_to_datetime(this.field_manager.get_field_value("dates_from"))});
            });
            this.field_manager.on("field_changed:dates_to", this, function() {
                this.set({"dates_to": openerp.web.str_to_datetime(this.field_manager.get_field_value("dates_to"))});
            });
            
            this.field_manager.on("field_changed:summary_headers", this, function() {
                this.set({"summary_headers": this.field_manager.get_field_value("summary_headers")});
            });
            this.field_manager.on("field_changed:awning_summary", this, function() {
                this.set({"awning_summary":this.field_manager.get_field_value("awning_summary")});
            });
            
        },
        
        initialize_field: function() {
            openerp.web.form.ReinitializeWidgetMixin.initialize_field.call(this);
            var self = this;
            self.on("change:summary_headers", self, self.initialize_content);
            self.on("change:awning_summary", self, self.initialize_content);
        },
        
      initialize_content: function() {
    	   var self = this;
           if (self.setting)
               return;
           
           if (!this.summary_headers || !this.awning_summary)
              	return
           // don't render anything until we have summary_header and awning_summary
              	
           this.destroy_content();
           
           if (this.get("summary_headers")) {
            this.summary_headers = py.eval(this.get("summary_headers"));
           }
           if (this.get("awning_summary")) {
            this.awning_summary = py.eval(this.get("awning_summary"));
           }
           	
           this.renderElement();
           this.view_loading();
        },
        
        view_loading: function(r) {
            return this.load_form(r);
        },
        
        load_form: function(data) {
            self.action_manager = new openerp.web.ActionManager(self);
            
            this.$el.find(".table_free").bind("click", function(event){
                self.action_manager.do_action({
                        type: 'ir.actions.act_window',
                        res_model: "awning.reservation",
                        views: [[false, 'form']],
                        target: 'new',
                        context: {"awning_id": $(this).attr("data"), 'date': $(this).attr("date")},
                });
            });
        
        },
       
        renderElement: function() {
             this.destroy_content();
             this.$el.html(QWebs.render("summarysDetails", {widget: this}));
        }     
    });
   
    openerp.web.form.custom_widgets.add('Awning_Reservation', 'openerp.toldo_reservation.AwningSummary');
 };
    
