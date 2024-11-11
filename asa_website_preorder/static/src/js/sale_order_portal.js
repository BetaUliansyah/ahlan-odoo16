/** @odoo-module **/
//This JavaScript function handles the cancellation of a sale order on the website.
//The function checking for there is a valid reason for cancelling the order
var publicWidget = require('web.public.widget');
var ajax = require('web.ajax');
publicWidget.registry.WebsitePreOrder = publicWidget.Widget.extend({
     selector: '.editReasonForm',
     events: {
            'click #submit_button': '_onSubmit',
        },
        _onSubmit: function (e) {
            var product = this.$("#product_id").val(); // Product ID, typically a string
            var qty_cancel = parseInt(this.$("#qty").val(), 10); // Cancel quantity as an integer
            var sisa = parseInt(this.$("#qty_order").val(), 10); // Remaining quantity as an integer
            var note = this.$("#note").val(); // Note, typically a string

            console.log("start",qty_cancel, sisa)

            if (qty_cancel > sisa ){
                    alert("Qty tidak boleh melebihi Qty Pre Order...!!");
                    e.preventDefault();
                }
            else{
              ajax.jsonRpc("/create_cancel_order", 'call', {
                   'product': product,
                   'qty': qty_cancel,
                   'note': note,
              }).then(function() {
                 location.reload();
            });
            }
        }
    });
    var WebsitePreOrder = new publicWidget.registry.WebsitePreOrder(this);
    WebsitePreOrder.appendTo($(".editReasonForm"));
    return publicWidget.registry.WebsitePreOrder;
