 openerp.tent = function(openerp) {
    var _t = openerp.web._t;
    _lt = openerp.web._lt;
    var QWeb = openerp.web.qweb;
    
    openerp.tent.TentSummary = openerp.web.form.FormWidget.extend(openerp.web.form.ReinitializeWidgetMixin, {
        
        display_namez: _lt('Form'),
        view_type:"form",
        
        init: function() {
            this._super.apply(this, arguments);
            if(this.field_manager.model == "tent.reservation.summary")
            {
                $(".oe_view_manager_buttons").hide();
                $(".oe_view_manager_header").hide();
            }
            this.set({
                date_tent_to: false,
                date_tent_from: false,
                summary_tent_header: false,
                tent_summary: false,
            });
            this.summary_tent_header = [];
            this.tent_summary = [];
            this.field_manager.on("field_changed:date_tent_from", this, function() {
                this.set({"date_tent_from": openerp.web.str_to_datetime(this.field_manager.get_field_value("date_tent_from"))});
            });
            this.field_manager.on("field_changed:date_tent_to", this, function() {
                this.set({"date_tent_to": openerp.web.str_to_datetime(this.field_manager.get_field_value("date_tent_to"))});
            });
            
            this.field_manager.on("field_changed:summary_tent_header", this, function() {
                this.set({"summary_tent_header": this.field_manager.get_field_value("summary_tent_header")});
            });
            this.field_manager.on("field_changed:tent_summary", this, function() {
                this.set({"tent_summary":this.field_manager.get_field_value("tent_summary")});
            });
            
        },
        
        initialize_field: function() {
            openerp.web.form.ReinitializeWidgetMixin.initialize_field.call(this);
            var self = this;
            self.on("change:summary_tent_header", self, self.initialize_content);
            self.on("change:tent_summary", self, self.initialize_content);
        },
        
      initialize_content: function() {
           var self = this;
           if (self.setting)
               return;
           
           if (!this.summary_tent_header || !this.tent_summary)
              	return
              	
           this.destroy_content();
           
           if (this.get("summary_tent_header")) {
            this.summary_tent_header = py.eval(this.get("summary_tent_header"));
           }
           if (this.get("tent_summary")) {
            this.tent_summary = py.eval(this.get("tent_summary"));
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
                console.log("hoooola");
                console.log($(this).attr("data"));
                console.log($(this).attr("date"));
                self.action_manager.do_action({
                        type: 'ir.actions.act_window',
                        res_model: "tent.reservation",
                        views: [[false, 'form']],
                        target: 'new',
                        context: {"tent_id": $(this).attr("data"), 'date': $(this).attr("date")},
                });
            });
        
        },
       
        renderElement: function() {
             this.destroy_content();
             this.$el.html(QWeb.render("summaryTentDetails", {widget: this}));
        }     
    });

    openerp.web.form.custom_widgets.add('Tent_Reservation', 'openerp.tent.TentSummary');
};

