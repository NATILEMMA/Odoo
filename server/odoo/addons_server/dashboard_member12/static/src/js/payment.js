odoo.define('dashboard_member12.member_payment', function (require) {
    'use strict';

    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var _t = core._t;

    publicWidget.registry.OnlinePayment = publicWidget.Widget.extend({
        selector: '#payment_per_year',
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;

            $("#payment_years").on('change', function() {
                self._update_payment();
            });

            self._update_payment();
        },

        _update_payment: function () {
            console.log($("#payment_years").val())
            var self = this;
            this._rpc({
                route: '/yearly/payments',
                params: {
                    'year': $("#payment_years").val()
                },
            }).then(function(result) {
                var options = [];
                var payment_of_the_year_member = result.payments;
                for (var i = 0; i < payment_of_the_year_member.length; i++) {
                    options.push('<tr>')
                    options.push('<td><span>' + payment_of_the_year_member[i].member_id + '</span></td>')
                    options.push('<td><span>' + payment_of_the_year_member[i].year + '</span></td>');
                    options.push('<td><span>' + payment_of_the_year_member[i].month + '</span></td>');
                    options.push('<td><span>' + payment_of_the_year_member[i].fee_amount + '</span></td>');
                    options.push('<td><span>' + payment_of_the_year_member[i].amount_remaining + '</span></td>');
                    options.push('<td><span>' + payment_of_the_year_member[i].amount_paid + '</span></td>');
                    options.push('<td><span>' + payment_of_the_year_member[i].traced_member_payment + '</span></td>');
                    options.push('<td><span>' + payment_of_the_year_member[i].id_payment + '</span></td>');
                    options.push('<td><span>' + payment_of_the_year_member[i].state + '</span></td>');
                    if (payment_of_the_year_member[i].type_of_payment == "bank" && payment_of_the_year_member[i].cell_payment_state == "pending payments")
                    {
                        options.push('<td><a data-oe-model="ir.ui.view" data-oe-id="2113" data-oe-field="arch" data-oe-xpath="/t[1]/t[1]/body[1]/div[2]/div[1]/div[3]/div[1]/div[1]/table[1]/tbody[1]/t[1]/t[1]/t[4]/tr[1]/td[6]/a[1]" href="' + payment_of_the_year_member[i].payment + '"><em>Add Bank Slips</em></a></td>')
                    }
                    options.push('</tr>')
                }
                $("#payment_member_body").html(options.join(''));

                var options = [];
                var payment_of_the_year_league = result.league_payments;
                for (var i = 0; i < payment_of_the_year_league.length; i++) {
                    options.push('<tr>')
                    options.push('<td><span>' + payment_of_the_year_league[i].league_id + '</span></td>')
                    options.push('<td><span>' + payment_of_the_year_league[i].year + '</span></td>')
                    options.push('<td><span>' + payment_of_the_year_league[i].month + '</span></td>')
                    options.push('<td><span>' + payment_of_the_year_league[i].fee_amount + '</td>')
                    options.push('<td><span>' + payment_of_the_year_league[i].amount_remaining + '</span></td>')
                    options.push('<td><span>' + payment_of_the_year_league[i].amount_paid + '</span></td>')
                    options.push('<td><span>' + payment_of_the_year_league[i].traced_league_payment + '</span></td>')
                    options.push('<td><span>' + payment_of_the_year_league[i].id_payment + '</span></td>')
                    options.push('<td><span>' + payment_of_the_year_league[i].state + '</span></td>')
                    if (payment_of_the_year_league[i].type_of_payment == "bank" && payment_of_the_year_league[i].cell_payment_state == "pending payments")
                    {
                        options.push('<td><a data-oe-model="ir.ui.view" data-oe-id="2113" data-oe-field="arch" data-oe-xpath="/t[1]/t[1]/body[1]/div[2]/div[1]/div[3]/div[1]/div[1]/table[1]/tbody[1]/t[1]/t[1]/t[4]/tr[1]/td[6]/a[1]" href="' + payment_of_the_year_league[i].payment + '"><em>Add Bank Slips</em></a></td>')
                    }
                    options.push('</tr>')
                }
                $("#payment_league_body").html(options.join(''));

            });
        },

    })

});