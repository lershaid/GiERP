# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools import drop_view_if_exists

class WorkCenterLoad(models.Model):
    _name = "report.workcenter.load"
    _description = "Work Center Load"
    _auto = False
    _log_access = False

    name = fields.Char('Week', required=True)
    workcenter_id = fields.Many2one('mrp.workcenter', 'Work Center', required=True)
    duration = fields.Float('Duration')

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'report_workcenter_load')
        self._cr.execute("""
            create view report_workcenter_load as (
                SELECT
                    min(wl.id) as id,
                    to_char(p.date_planned_start,'YYYY:mm:dd') as name,
                    SUM(wl.duration_expected) AS duration,
                    wl.workcenter_id as workcenter_id
                FROM
                    mrp_workorder wl
                    LEFT JOIN mrp_production p
                        ON p.id = wl.production_id
                GROUP BY
                    wl.workcenter_id,
                    to_char(p.date_planned_start,'YYYY:mm:dd')
            )""")


class ValueVariation(models.Model):
    _name = "report.mrp.inout"
    _description = "Stock value variation"
    _auto = False
    _log_access = False
    _rec_name = 'date'

    date = fields.Char('Week', required=True)
    value = fields.Float('Stock value', required=True, digits=(16, 2))
    company_id = fields.Many2one('res.company', 'Company', required=True)

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'report_mrp_inout')
        self._cr.execute("""
            create view report_mrp_inout as (
                select
                    min(sm.id) as id,
                    to_char(sm.date,'YYYY:IW') as date,
                    sum(case when (sl.usage='internal') then
                        sm.price_unit * sm.product_qty
                    else
                        0.0
                    end - case when (sl2.usage='internal') then
                        sm.price_unit * sm.product_qty
                    else
                        0.0
                    end) as value,
                    sm.company_id
                from
                    stock_move sm
                left join product_product pp
                    on (pp.id = sm.product_id)
                left join product_template pt
                    on (pt.id = pp.product_tmpl_id)
                left join stock_location sl
                    on ( sl.id = sm.location_id)
                left join stock_location sl2
                    on ( sl2.id = sm.location_dest_id)
                where
                    sm.state = 'done'
                group by
                    to_char(sm.date,'YYYY:IW'), sm.company_id
            )""")
