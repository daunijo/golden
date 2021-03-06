# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = '1.22.37'

# 1.22.37
#   - Add ignore_permissions=True when cancel Payment Entry Receive and Payment Entry Pay in order to cancel Payment Entry
# 1.22.36
#   - Fix cannot save SO if item have 2 stock in one warehouse.
# 1.22.35
#   - Fix get remaining item RO in PI. #203
# 1.22.34
#   - Add field: default_purchase_return_write_off_account in Company. #202
#   - Checking uom base on item_code in SO, Packing, TO, SI, PO, RO, PI, Sales Return, . #200
#   - Hide Move % Add button in Item through css. #199
#   - Pindahkan Custom Script to public/js/ folder
#   - Update packing. #198
# 1.22.33
#   - Update report: Stock Card, Stock Card Sales & Stock Card Purchasing. #196
# 1.22.32
#   - Update report: Stock Card, Stock Card Sales & Stock Card Purchasing. #196
# 1.22.31
#   - Update report: Stock Card, Stock Card Sales & Stock Card Purchasing. #196
#   - Add field: picking_order in Sales Order Item. #194
#   - Add field: picking_order in Sales Invoice Item
# 1.22.30
#   - Add doctype Sales Commission Collect.
#   - Update Sales Commission.
# 1.22.29
#   - Add filter employee in Sales Analysis. #154
#   - Hide City/Town in Expedition. #189
#   - Add field: collect_in_range & collect_out_range in Sales Commission. #148
# 1.22.28
#   - Add report_data_map.py in golden folder
#   - Fix Sales Analysis - Sales Person. #154
#   - Add function on_login in hooks.py to fill empty employee in SO, DN & SI
#   - Update Custom Script: Sales Order & Sales Invoice
# 1.22.27
#   - Hide Region & City in Summary Generator. #189
# 1.22.26
#   - Replace City & Region in Summary Generator, Customer. #189
#   - Update status in Receive Order. #195
# 1.22.25
#   - Update Balance Qty in Stock Card, Stock Card Sales & Stock Card Purchasing. #181
#   - Update warehouse_tree.
#   - Add due_date_base_on in Purchase Invoice. #7
# 1.22.24
#   - Hilangkan Receiver Staff di module. #185
#   - Write Off Account di Sales Return sekarang mandatory. #182
#   - Fix double Parent Warehouse. #151
# 1.22.23
#   - Update on_submit Receive Order, purchase receipt date follows date from receive order. #179
#   - Update tree warehouse detail. #151
#   - Add link Receive Order in Purchase Invoice Item. #192
# 1.22.22
#   - Fix duplicate document in Commission Percentages
#   - Update Invoice Keeptrack
# 1.22.21
#   - Add field: show_all_items in Sales Return. #182
#   - Update json, js & py Sales Return
#   - Add field: account_currency in Sales Return. #143
#   - Update overlappping value in Commission Percentage. #145
#   - Update Sales Commission field #149 & #148
#   - Fix bug Dynamic Item Report - Purchase. #157
# 1.22.20
#   - Add report: Dynamic Item Report - Purchase
# 1.22.19
#   - Update Purchase Return
#   - Update Payment Entry Pay
# 1.22.18
#   - Automatically fill Collecting Planning if Target Planning is filled and collect planning is null
#   - Update Sales Return
#   - Update Payment Entry Receive
# 1.22.17
#   - Stock Card wrong stock value if stock reconciliation, #176
# 1.22.16
#   - Add Driver & Helper in Employee Settings, #175
# 1.22.15
#   - Add Sales in Customer, #173
#   - Update filter in item_code Purchase Invoice, #171
#   - Hide table customers in Summary Generator, #168
# 1.22.14
#   - Multiple Purhcase Invoice for one Receive Order, #174
# 1.22.13
#   - Add child doctype: Invoice Keeptrack Customer
#   - Major update Invoice Keeptrack
#   - Update Sales Invoice Summary
#   - Add modul: RS for Receiver Staff
#   - Update Sales Commission
#   - Update Sales Return
# 1.22.12
#   - Add column Stock Card by Location in Stock Card, #136
#   - Add collector_name in Invoice Keeptrack, #164
#   - Add filter in collector, #165
# 1.22.11
#   - Update Commission Percentage, #150
#   - Update Parent Warehouse & Parent Section in Warehouse, #151
# 1.22.10
#   - Add filter Item Group in Dynamic Item Report
#   - Update Payment Entry Receive
#   - Update submit_stock_entry in reference.py
#   - Update custom script & custom field
# 1.22.9
#   - Update Sales Return
#   - Update Purchase Budget
#   - Update Sales Commission
#   - Add report: Stock Card by Location
# 1.22.8
#   - [Fix] overlapping in commission percentate, #145
#   - Update balance in report Stock Card, Stock Card Sales & Stock Card Purchasing
#   - Hide detail in Purchase Budget, #147
#   - [Fix] Sales Return error when save, #143
# 1.22.7
#   - Update script Item
#   - Update Batck Picking
#   - [Fix] Customer Rgion above City #139
#   - Update Packing Barcode
#   - Update Picking Order
#   - Update Sales Commission
#   - Update Sales Target
#   - Update Stock Card
#   - Update Stock Sales
# 1.22.6
#   - Add doctype Delivery Keeptrack Barcode
#   - Update Delivery Keeptrack
#   - Update Receive Order
# 1.22.5
#   - Update Sales Commission
#   - Update Receive Order
# 1.22.4
#   - Fix issue #99 about Receive Order
#   - Fix issue #108 about Expedition checkbox
# 1.22.3
#   - Add doctype Commission Percentage Collect
#   - Add doctype Sales Commission Payment
# 1.22.2
#   - Update report Stock Card
#   - Update report Stock Card Sales
#   - Update report Stock Card Purchasing
# 1.22.1
#   - Add doctype Commission Percentage
#   - Add doctype Commission Percentage Detail
#   - Add doctype Sales Commission
#   - Add doctype Sales Commission Invoice
#   - Add doctype Sales Commission Return
# 1.21.2
#   - Add sales_name in Summary Generator
#   - Add sales in Summary Generator Customer
#   - Add sales_name in Summary Generator Detail
#   - Add sales_name in Sales Invoice Summary Detail
# 1.21.1
#   - Add doctype City
#   - Add doctype Region
#   - Add doctype Summary Generator
#   - Minor update in few doctype & script
# 1.20.5
#   - Update report Stock Card
#   - Update report Stock Card Sales
#   - Update report Stock Card Purchasing
# 1.20.4
#   - Update report Stock Card
#   - Update report Stock Card Sales
#   - Update report Stock Card Purchasing
#   - [Fix] expedition checkbox filter in Receive Order & Delivery Order #108
# 1.20.3
#   - Update Payment Entry Receive
#   - Update Payment Entry Pay
#   - Add report Stock Card Sales
#   - Add report Stock Card Purchasing
#   - Update doctype Sales Invoice Summary
# 1.20.2
#   - Update report Stock Card
# 1.20.1
#   - Add doctype Payment Entry Receive
#   - Add doctype Payment Entry Receive Reference
#   - Add doctype Payment Entry Receive Deduction
#   - Add doctype Payment Entry Pay
#   - Add doctype Payment Entry Pay Reference
#   - Add doctype Payment Entry Pay Deduction
# 1.19.24
#   - Add doctype Delivery Order Barcode
#   - Add Barcode in Delivery Order
#   - Update doctype Packing Barcode
#   - Update doctype Delivery Order Detail
#   - Update doctype Packing Picking
# 1.19.23
#   - Update on_submit in Transfer Order
# 1.19.22
#   - Update Get Item in Delivery Order
#   - Update Get Item in Delivery Keeptrack
# 1.19.21
#   - Update Stock Reconciliation
# 1.19.20
#   - Update Sales Order
#   - Update Sales Order (Allow Double Order)
# 1.20.1
#   - Update Sales Invoice
# 1.20.0
#   - Add doctype: KPI
# 1.19.19
#   - Update Delivery Order
#   - Update Delivery keeptrack
#   - Update Sales Invoice
# 1.19.18
#   - Update on_submit & on_cancel Purchase Invoice
# 1.19.17
#   - Update Purchase Invoice
# 1.19.16
#   - Update expedition
#   - Update Delivery Order
# 1.19.15
#   - Update reference
# 1.19.14
#   - Fix issue #22
# 1.19.13
#   - Fix issue #99, 100, 102, 103
# 1.19.12
#   - Fix issue #98 & #101
# 1.19.11
#   - Fix issue #60, 91, 84
# 1.19.10
#   - Update Custom script
# 1.19.9
#   - Update Receive Order
# 1.19.8
#   - Fix issue #78, 79, 81, 85
# 1.19.7
#   - Add report: Purchase & Sales Trends
# 1.19.6
#   - Hide check in packing, #77
# 1.19.5
#   - Update script Sales Order
# 1.19.4
#   - Update Packing
# 1.19.3
#   - Fix issue #67, #68, #69
# 1.19.2
#   - Fix issue #63 & #64
# 1.19.1
#   - Update Get Picking Order in Packing
# 1.19.0
#   - Add Doctype: Warehouse Routing & Warehouse Routing Detail
#   - Delete Doctype: Template Warehouse & Template Warehouse Detail
# 1.18.3
#   - Update fixtures
#   - Update Picking
#   - Update Transfer Order
# 1.18.2
#   - Update Script Sales Order
#   - Update Script Purchase Order
#   - Add item_query in stock.py
#   - Rename status 'In Packing' to 'Packed' in Sales Order and Packing
#   - Delete Packer & Packer Name in Packing
# 1.18.1
#   - Update field Picker, Packer, Checker in Packing
# 1.18.0
#   - Add Doctype: Employee Settings & Employee Settings Detail
# 1.17.0
#   - Add Doctype: Template Warehouse & Template Warehouse Detail
#   - Update Custom Script Item & Sales Order
# 1.16.4
#   - Add Report: Purchase Analysis Per Item
# 1.16.3
#   - Update on_submit & on_cancel: Sales Order
# 1.16.2
#   - Update Transfer Order
#   - Update Packing Item & Packing Picking
# 1.16.1
#   - Add field: Priority in Sales Order
#   - Add field: Conversion Factor in Transfer Order
# 1.16.0
#   - Add Doctype: Picking Order
# 1.15.10
#   - Update on_submit & on_cancel: Sales Order
#   - Update on_submit: Packing
# 1.15.9
#   - Update on_change: Sales Order
#   - Update js: Packing
#   - Update js: Transfer Order
#   - Delete replenishment_section in Warehouse
# 1.15.8
#   - Update on_submit & on_cancel: Sales Order
# 1.15.7
#   - Update scirpt: Sales Order
#   - Add Doctype: Sales Order Replenishment Warehouse
# 1.15.6
#   - Update Report: Dynamic Item Report
# 1.15.5
#   - Update Report: Dynamic Item Report
#   - Update custom script: Item
# 1.15.4
#   - Fix few minor update
# 1.15.3
#   - Add Report: Purchase By Item Group
# 1.15.2
#   - Add Report: Purchase Analysis
# 1.15.1
#   - Update calculation on Purchase Budget
# 1.15.0
#   - Add Doctype: Purchase Budget
#   - Add Doctype: Purchase Budget Detail
#   - Update Sales Target
# 1.14.11
#   - Update Sales Target
#   - Update on_cancel Sales Order
# 1.14.10
#   - Update Sales Target
# 1.14.9
#   - Update Delivery Keeptrack
# 1.14.8
#   - Update Delivery Keeptrack
#   - Update Delivery Return
# 1.14.7
#   - Update Annual Sold Summary Report
# 1.14.6
#   - Add Report: Annual Sold Summary Report
#   - Update sales target
#   - Update on_cancel & on_submit Delivery Note, sekarang akan update ke Receive Order
# 1.14.5
#   - Update Delivery Kepptrack & Delivery Return
# 1.14.4
#   - Update Delivery Order
# 1.14.3
#   - Update Sales Return
# 1.14.2
#   - Update Purchase Return & Sales Return
# 1.14.1
#   - Add get_packing in Delivery Order
# 1.14.0
#   - Add doctype: Delivery Return
# 1.13.12
#   - Update Delivery Keeptrack
# 1.13.11
#   - Update box Packing
# 1.13.10
#   - Update on_submit Packing
# 1.13.9
#   - Update on_cancel Sales Order
# 1.13.8
#   - Add doctype: Batch Packing Detail
#   - Add doctype: Batch Packing Detail Item
#   - Update Batch Picking
# 1.13.7
#   - Update on_cancel Sales Order
# 1.13.6
#   - Update on_cancel Packing
#   - Update Purchase Return
# 1.13.5
#   - Update on_submit Transfer Order
#   - Update validate Transfer Order
# 1.13.4
#   - Update Sales Invoice
# 1.13.3
#   - Add report: Dynamic Item Report
#   - Update Packing
# 1.13.2
#   - Update on_cancel Delivery Order
# 1.13.1
#   - Update delivery Order
#   - Update transfer order
# 1.13.0
#   - Add doctype: Delivery Order & Delivery Order Detail
# 1.12.15
#   - Update on_submit in Sales Order
# 1.12.14
#   - Update transfer order manual
# 1.12.13
#   - Update on_submit in Packing
# 1.12.12
#   - Update on_submit in Sales Order
#   - Update on_submit in Transfer Order
# 1.12.11
#   - Update on_submit in Transfer Order
# 1.12.10
#   - Update on_cancel in Sales Order
# 1.12.9
#   - Update on_submit in Sales Order
# 1.12.8
#   - Update on_submit in Transfer Order
# 1.12.7
#   - Update on_submit in Sales Order
#   - Update on_cancel in Sales Order
# 1.12.6
#   - Update on_submit in Sales Order
# 1.12.5
#   - Update on_submit in Sales Order
# 1.12.4
#   - Update on_submit in Sales Order
# 1.12.3
#   - Update on_submit in Sales Order
#   - Update on_cancel in Sales Order
#   - Update Receive Order
# 1.12.2
#   - Update on_cancel in Sales Order
#   - Update action in Picking
# 1.12.1
#   - Update on_submit Sales Order
# 1.12.0
#   - Add doctype: Batch Picking
# 1.11.1
#   - Update Packing
# 1.11.0
#   - Add doctype: Transfer Order
#   - Copy all content in from Ito to Transfer Order
#   - Delete doctype: ITO & ITO Item
#   - Update insert_pr_item in Purchase Order
#   - Update Receive Order Item
# 1.10.19
#   - Update delivery keeptrack
#   - Update sales return Detail
#   - update packing item
# 1.10.18
#   - Update receive order
# 1.10.17
#   - Update flow golden_status
# 1.10.16
#   - Update Purchase Return
# 1.10.15
#   - Update Purchase Return
#   - Update Sales Return
# 1.10.14
#   - Update Purchase Return
# 1.10.13
#   - Update Packing
# 1.10.12
#   - Update Receive Order Item
# 1.10.11
#   - Update Receive Order Item
# 1.10.10
#   - Update Receive Order
# 1.10.9
#   - Update conversion_factor in Receive Order
# 1.10.8
#   - Update Purchase & Sales Return
# 1.10.7
#   - Set default debit & credit in Purchase Return
# 1.10.6
#   - Update on_submit Purchase Return
#   - Update on_submit Sales Return
#   - Add custom form in Company
# 1.10.5
#   - Update on_submit Purchase Return
# 1.10.4
#   - Update Get PO in Receive Order
# 1.10.3
#   - Add checkbox in packing item
#   - Change few labels in ITO
# 1.10.2
#   - Update receive order
# 1.10.1
#   - Update receive order
# 1.10.0
#   - Add doctype: Receive Order
#   - Update Invoice Keeptrack
# 1.9.3
#   - Update invoice keeptrack
#   - Update sales invoice summary
# 1.9.2
#   - Update packing
# 1.9.1
#   - Update doctype: picking item
# 1.9.0
#   - Add doctype: Sales Target
#   - Major fix packing
# 1.8.3
#   - Add customer in picing
#   - Update validate packing
# 1.8.2
#   - Minur update Sales Invoice Summary
# 1.8.1
#   - Update Sales Invoice Summary
# 1.8.0
#   - Add Sales Invoice Summary doctype
# 1.7.1
#   - Get Picking List now in header
#   - Barcode in Packing now autogenerate from document name
#   - Hiding expedition in packing
# 1.7.0
#   - Add Invoice Keeptrack doctype
# 1.6.1
#   - Update barcodes
#   - Update script automatically create & submit DN when Picking submit
#   - Few minor fix
#   - Update Delivery Keeptrack
# 1.6.0
#   - Add Delivery Keeptrack Doctype
# 1.5.2
#   - Update on submit in Packing
#   - Fix create Delivery Note automatically from Packing
# 1.5.1
#   - Fix submit_sales_order_4
# 1.5.0
#   - Add Packing Doctype
# 1.4.1
#   - Update ITO when submit Stock Entry
# 0.4.0
#   - Add ITO Doctype
# 0.3.0
#   - Add Picking Doctype
# 0.2.0
#   - Add Sales Return Doctype
# 0.1.0
#   - Add Purchase Return Doctype
