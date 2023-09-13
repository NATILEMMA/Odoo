odoo.define('dashboard_member12.transfer', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    const {_t, qweb} = require('web.core');

    publicWidget.registry.tranferLeaderMemberDetails = publicWidget.Widget.extend({

        selector: '.o_transfer_details',
        read_events: {
            'change select[name="transfer_as_a_leader_or_member"]': '_transferChange',
        },

        start: function () {
            var def = this._super.apply(this, arguments);
            return def;
        },

        _tempChange: function() {
            var $transfer = this.$('select[name="transfer_as_a_leader_or_member"]');
            var transferValue = ($transfer.val() || 0);
            // var member = document.getElementById('member')
            // var member1 = document.getElementById('member1')
            var member2 = document.getElementById('member2')
            var member3 = document.getElementById('member3')
            var member4 = document.getElementById('member4')
            var member5 = document.getElementById('member5')
            var member6 = document.getElementById('member6')
            // var member7 = document.getElementById('member7')
            // var league = document.getElementById('league')
            // var league1 = document.getElementById('league1')
            var league2 = document.getElementById('league2')
            var league3 = document.getElementById('league3')
            var league4 = document.getElementById('league4')
            var league5 = document.getElementById('league5')
            if (transferValue === 'leader') {
                // league.style.display = 'none';
                // league1.style.display = 'none';
                league2.style.display = 'none';
                league3.style.display = 'none';
                league4.style.display = 'none';
                league5.style.display = 'none';
                // member.style.display = 'block';
                // member1.style.display = 'block';
                member2.style.display = 'none';
                member3.style.display = 'none'; 
                member4.style.display = 'none';
                member5.style.display = 'none';
                member6.style.display = 'block';
                // member7.style.display = 'none';           
            } else if (transferValue === 'member') {
                // league.style.display = 'none';
                // league1.style.display = 'none';
                league2.style.display = 'none';
                league3.style.display = 'none';
                league4.style.display = 'none';
                league5.style.display = 'none';
                // member.style.display = 'block';
                // member1.style.display = 'block';
                member2.style.display = 'block';
                member3.style.display = 'block';
                member4.style.display = 'block';
                member5.style.display = 'block';
                member6.style.display = 'none';
                // member7.style.display = 'none';
            } else if (transferValue === 'league') {
                // league.style.display = 'block';
                // league1.style.display = 'block';
                league2.style.display = 'block';
                league3.style.display = 'block';
                league4.style.display = 'block';
                league5.style.display = 'block';
                // member.style.display = 'none';
                // member1.style.display = 'none';
                member2.style.display = 'none';
                member3.style.display = 'none';
                member4.style.display = 'none';
                member5.style.display = 'none';
                member6.style.display = 'none';
                // member7.style.display = 'none';
            } else if (transferValue === 0) {        
                // league.style.display = 'none';
                // league1.style.display = 'none';
                league2.style.display = 'none';
                league3.style.display = 'none';
                league4.style.display = 'none';
                league5.style.display = 'none';
                // member.style.display = 'block';
                // member1.style.display = 'block';
                member2.style.display = 'none';
                member3.style.display = 'none'; 
                member4.style.display = 'none';
                member5.style.display = 'none';
                member6.style.display = 'block';
                // member7.style.display = 'none';
            }
        },
        _transferChange: function() {
            this._tempChange()
        },
    });

    publicWidget.registry.tranferLeagueMemberDetails = publicWidget.Widget.extend({

        selector: '.o_transfer_details',
        read_events: {
            'change select[name="transfer_as_a_league_or_member"]': '_transferChange',
        },

        start: function () {
            var def = this._super.apply(this, arguments);
            return def;
        },

        _tempChange: function() {
            var $transfer = this.$('select[name="transfer_as_a_league_or_member"]');
            var transferValue = ($transfer.val() || 0);
            // var member = document.getElementById('member')
            // var member1 = document.getElementById('member1')
            var member2 = document.getElementById('member2')
            var member3 = document.getElementById('member3')
            var member4 = document.getElementById('member4')
            var member5 = document.getElementById('member5')
            // var league = document.getElementById('league')
            // var league1 = document.getElementById('league1')
            var league2 = document.getElementById('league2')
            var league3 = document.getElementById('league3')
            var league4 = document.getElementById('league4')
            var league5 = document.getElementById('league5')
            if (transferValue === 'member') {
                // league.style.display = 'none';
                // league1.style.display = 'none';
                league2.style.display = 'none';
                league3.style.display = 'none';
                league4.style.display = 'none';
                league5.style.display = 'none';
                // member.style.display = 'block';
                // member1.style.display = 'block';
                member2.style.display = 'block';
                member3.style.display = 'block';
                member4.style.display = 'block';
                member5.style.display = 'block';
            } else if (transferValue === 'league') {
                // league.style.display = 'block';
                // league1.style.display = 'block';
                league2.style.display = 'block';
                league3.style.display = 'block';
                league4.style.display = 'block';
                league5.style.display = 'block';
                // member.style.display = 'none';
                // member1.style.display = 'none';
                member2.style.display = 'none';
                member3.style.display = 'none';
                member4.style.display = 'none';
                member5.style.display = 'none';
            } else if (transferValue === 0) {
                // league.style.display = 'none';
                // league1.style.display = 'none';
                league2.style.display = 'none';
                league3.style.display = 'none';
                league4.style.display = 'none';
                league5.style.display = 'none';
                // member.style.display = 'block';
                // member1.style.display = 'block';
                member2.style.display = 'block';
                member3.style.display = 'block';
                member4.style.display = 'block';
                member5.style.display = 'block';
            }
        },
        _transferChange: function() {
            this._tempChange()
        },
    });

    publicWidget.registry.tranferDetails = publicWidget.Widget.extend({

        selector: '.o_transfer_details',
        read_events: {
            'change select[name="transfer_subcity_id"]': '_subcityChange',
        },

         start: function () {
            var def = this._super.apply(this, arguments);
            this.$wereda = this.$('select[name="transfer_wereda_id"]');
            this.$weredaOptions = this.$wereda.filter(':enabled').find('option:not(:first)');
            this._weredaChange();
            return def;
         },

         _weredaChange: function() {
             var $subcity = this.$('select[name="transfer_subcity_id"]');
             var subcityID = ($subcity.val() || 0);
             this.$weredaOptions.detach();
             var $displayedState = this.$weredaOptions.filter('[data-parent_id=' + subcityID + ']');
             var nb = $displayedState.appendTo(this.$wereda).show().length;
         },

         _subcityChange: function() {
             this._weredaChange();
         },
    });

    publicWidget.registry.transferDetailsMainSpecific = publicWidget.Widget.extend({

        selector: '.o_transfer_details',
        read_events: {
            'change select[name="transfer_membership_org"]': '_mainChange',
            'change select[name="transfer_wereda_id"]': '_mainChange',
            'change select[name="transfer_as_a_leader_or_member"]': '_mainChange',
            'change select[name="transfer_as_a_league_or_member"]': '_mainChange',
            
        },

         start: function () {
            var def = this._super.apply(this, arguments);
            this.$main = this.$('select[name="transfer_main_office"]');
            this.$mainOptions = this.$main.filter(':enabled').find('option:not(:first)');
            this._orgChange();
            return def;
         },

         _orgChange: function() {
            var $transferLeague = this.$('select[name="transfer_as_a_league_or_member"]');
            var $transferLeader = this.$('select[name="transfer_as_a_leader_or_member"]');
            var transferValueLeader = ($transferLeader.val() || 0);
            var transferValueLeague = ($transferLeague.val() || 0);
            if (transferValueLeague === 'member') {
                var $wereda = this.$('select[name="transfer_wereda_id"]');
                var $org = this.$('select[name="transfer_membership_org"]');
                var weredaID = ($wereda.val() || 0);
                var orgID = ($org.val() || 0);
                console.log(orgID)
                console.log(this.$mainOptions)
                this.$mainOptions.detach();
                var $displayedState = this.$mainOptions.filter('[data-wereda_id=' + weredaID  + ']').filter('[data-memb-org_id=' + orgID  + ']').filter('[data-member_type=' + String(transferValueLeague)  + ']');
                var nb = $displayedState.appendTo(this.$main).show().length;
                console.log($displayedState)
            }
            if (transferValueLeader === 'member') {
                var $wereda = this.$('select[name="transfer_wereda_id"]');
                var $org = this.$('select[name="transfer_membership_org"]');
                var weredaID = ($wereda.val() || 0);
                var orgID = ($org.val() || 0);
                console.log(orgID)
                console.log(this.$mainOptions)
                this.$mainOptions.detach();
                var $displayedState = this.$mainOptions.filter('[data-wereda_id=' + weredaID  + ']').filter('[data-memb-org_id=' + orgID  + ']').filter('[data-member_type=' + String(transferValueLeader)  + ']');
                var nb = $displayedState.appendTo(this.$main).show().length;
                console.log($displayedState)
            }
         },

         _mainChange: function() {
             this._orgChange();
         },
    });

    publicWidget.registry.transferDetailsCell = publicWidget.Widget.extend({

        selector: '.o_transfer_details',
        read_events: {
            'change select[name="transfer_main_office"]': '_mainChange',
        },

         start: function () {
            var def = this._super.apply(this, arguments);
            this.$cell = this.$('select[name="transfer_member_cells"]');
            this.$cellOptions = this.$cell.filter(':enabled').find('option:not(:first)');
            this._cellChange();
            return def;
         },

         _cellChange: function() {
             var $main = this.$('select[name="transfer_main_office"]');
             var mainID = ($main.val() || 0);
             this.$cellOptions.detach();
             var $displayedState = this.$cellOptions.filter('[data-main_office=' + mainID  + ']');
             var nb = $displayedState.appendTo(this.$cell).show().length;
         },

         _mainChange: function() {
             this._cellChange();
         },
    });

    publicWidget.registry.transferDetailsWoreda = publicWidget.Widget.extend({

        selector: '.o_transfer_details',
        read_events: {
            'change select[name="transfer_wereda_id"]': '_weredaChange',
            'change select[name="transfer_league_organization"]': '_weredaChange',
            'change select[name="transfer_as_a_leader_or_member"]': '_weredaChange',
            'change select[name="transfer_as_a_league_or_member"]': '_weredaChange',
        },

         start: function () {
            var def = this._super.apply(this, arguments);
            this.$main = this.$('select[name="transfer_league_main_office"]');
            this.$mainOptions = this.$main.filter(':enabled').find('option:not(:first)');
            this._mainChange();
            return def;
         },

         _mainChange: function() {
            var $transferLeague = this.$('select[name="transfer_as_a_league_or_member"]');
            var $transferLeader = this.$('select[name="transfer_as_a_leader_or_member"]');
            var transferValueLeader = ($transferLeader.val() || 0);
            var transferValueLeague = ($transferLeague.val() || 0);
            if (transferValueLeague === 'league') {
                var $wereda = this.$('select[name="transfer_wereda_id"]');
                var $leagueorg = this.$('select[name="transfer_league_organization"]');
                var weredaID = ($wereda.val() || 0);
                var leagueID = ($leagueorg.val() || 0);
                this.$mainOptions.detach();
                console.log(this.$mainOptions)
                var $displayedState = this.$mainOptions.filter('[data-wereda_id=' + weredaID  + ']').filter('[data-org_id=' + leagueID  + ']').filter('[data-league_type=' + String(transferValueLeague)  + ']');
                //  $displayedState.filter('[data-org_id=' + leagueID  + ']');
                console.log($displayedState)
                var nb = $displayedState.appendTo(this.$main).show().length;
            }
            if (transferValueLeader === 'league') {
                var $wereda = this.$('select[name="transfer_wereda_id"]');
                var $leagueorg = this.$('select[name="transfer_league_organization"]');
                var weredaID = ($wereda.val() || 0);
                var leagueID = ($leagueorg.val() || 0);
                this.$mainOptions.detach();
                console.log(this.$mainOptions)
                var $displayedState = this.$mainOptions.filter('[data-wereda_id=' + weredaID  + ']').filter('[data-org_id=' + leagueID  + ']').filter('[data-league_type=' + String(transferValueLeader)  + ']');
                //  $displayedState.filter('[data-org_id=' + leagueID  + ']');
                console.log($displayedState)
                var nb = $displayedState.appendTo(this.$main).show().length;
            }
         },

         _weredaChange: function() {
             this._mainChange();
         },
    });



    publicWidget.registry.transferDetailsMainoffice = publicWidget.Widget.extend({

        selector: '.o_transfer_details',
        read_events: {
            'change select[name="transfer_league_main_office"]': '_mainChange',
        },

         start: function () {
            var def = this._super.apply(this, arguments);
            this.$cell = this.$('select[name="transfer_league_member_cells"]');
            this.$cellOptions = this.$cell.filter(':enabled').find('option:not(:first)');
            this._cellChange();
            return def;
         },

         _cellChange: function() {
             var $main = this.$('select[name="transfer_league_main_office"]');
             var mainID = ($main.val() || 0);
             this.$cellOptions.detach();
             var $displayedState = this.$cellOptions.filter('[data-league-main_office=' + mainID  + ']');
             var nb = $displayedState.appendTo(this.$cell).show().length;
         },

         _mainChange: function() {
             this._cellChange();
         },
    });

    publicWidget.registry.transferLeader = publicWidget.Widget.extend({

        selector: '.o_transfer_details',
        read_events: {
            'change select[name="transfer_responsibility_leader"]': '_leaderChange',
        },

        start: function () {
            var def = this._super.apply(this, arguments);
            return def;
        },


         _leaderChange: function() {
            var $responsiblity = this.$('select[name="transfer_responsibility_leader"]');
            var resValue = ($responsiblity.val() || 0);
            var subcity = document.getElementById('subcity')
            var woreda = document.getElementById('woreda')
            console.log(resValue)
            if (resValue == 1) {
                console.log(resValue)
                subcity.style.display = 'block';
                woreda.style.display = 'block';
            } else if (resValue == 2) {
                console.log(resValue)
                subcity.style.display = 'block';
                woreda.style.display = 'none';
            } else if (resValue == 3) {
                console.log(resValue)
                subcity.style.display = 'none';
                woreda.style.display = 'none';
            }
         },
    });


});